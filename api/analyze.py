import asyncio
import json
import os
import re
import ssl
from http.server import BaseHTTPRequestHandler
from pathlib import Path

from eth_account import Account
from web3 import Web3
from x402 import x402Client
from x402.http.clients import x402HttpxClient
from x402.mechanisms.evm import EthAccountSigner
from x402.mechanisms.evm.exact.register import register_exact_evm_client
from x402.mechanisms.evm.upto.register import register_upto_evm_client
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

_RPC_URL      = "https://ogevmdevnet.opengradient.ai"
_REGISTRY     = "0x4e72238852f3c918f4E4e57AeC9280dDB0c80248"
_NETWORK      = "eip155:84532"
_MODEL        = "claude-sonnet-4-6"
_CHAT_PATH    = "/v1/chat/completions"
_PLACEHOLDER  = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
_TIMEOUT      = 90

_TEE_REGISTRY_ABI = [{"inputs":[{"internalType":"uint8","name":"teeType","type":"uint8"}],"name":"getActiveTEEs","outputs":[{"components":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"paymentAddress","type":"address"},{"internalType":"string","name":"endpoint","type":"string"},{"internalType":"bytes","name":"publicKey","type":"bytes"},{"internalType":"bytes","name":"tlsCertificate","type":"bytes"},{"internalType":"bytes32","name":"pcrHash","type":"bytes32"},{"internalType":"uint8","name":"teeType","type":"uint8"},{"internalType":"bool","name":"enabled","type":"bool"},{"internalType":"uint256","name":"registeredAt","type":"uint256"},{"internalType":"uint256","name":"lastHeartbeatAt","type":"uint256"}],"internalType":"struct TEERegistry.TEEInfo[]","name":"","type":"tuple[]"}],"stateMutability":"view","type":"function"}]

_tee_cache: dict = {}

SYSTEM_PROMPT = """You are an expert Web3 security analyst specializing in detecting rug pulls, scams, and high-risk token launches.
You MUST respond with ONLY valid JSON in this exact format:
{
  "rug_pull_score": <integer 0-100>,
  "risk_level": "<VERY LOW | LOW | MEDIUM | HIGH | CRITICAL>",
  "summary": "<2-3 sentence overall assessment>",
  "categories": {
    "tokenomics": { "score": <integer 0-100>, "findings": ["<finding1>", "<finding2>"] },
    "vesting":    { "score": <integer 0-100>, "findings": ["<finding1>", "<finding2>"] },
    "team":       { "score": <integer 0-100>, "findings": ["<finding1>", "<finding2>"] },
    "liquidity":  { "score": <integer 0-100>, "findings": ["<finding1>", "<finding2>"] },
    "contract":   { "score": <integer 0-100>, "findings": ["<finding1>", "<finding2>"] }
  },
  "red_flags": ["<flag1>", "<flag2>"],
  "green_flags": ["<flag1>", "<flag2>"],
  "recommendation": "<AVOID | EXTREME CAUTION | PROCEED WITH CAUTION | RELATIVELY SAFE>"
}
Score meaning: 0 = no risk, 100 = definite rug pull."""


def _build_prompt(d: dict) -> str:
    return f"""Analyze this token launch for rug pull risk:
TOKEN: {d.get('token_name')} (${d.get('token_symbol')}) on {d.get('chain')}
SUPPLY: {d.get('total_supply')} | PRICE: {d.get('token_price')} | HARD CAP: {d.get('hard_cap')}
TOKENOMICS: Team {d.get('team_allocation')}% | Investors {d.get('investor_allocation')}% | Public {d.get('public_allocation')}% | Ecosystem {d.get('ecosystem_allocation')}% | Liquidity {d.get('liquidity_allocation')}%
VESTING: {d.get('vesting_schedule') or 'Not provided'}
LIQUIDITY LOCKED: {d.get('liquidity_locked')} for {d.get('lock_duration')} on {d.get('dex')}
TEAM DOXXED: {d.get('team_doxxed')} | PREVIOUS PROJECTS: {d.get('previous_projects')}
TEAM WALLETS: {d.get('team_wallets') or 'Not provided'}
AUDITED: {d.get('audited')} by {d.get('audit_firm')} | MINT FUNCTION: {d.get('mint_function')} | OWNERSHIP RENOUNCED: {d.get('ownership_renounced')}
NOTES: {d.get('additional_info') or 'None'}
Respond with JSON only."""


def _get_tee_endpoint() -> tuple:
    if _tee_cache:
        return _tee_cache["endpoint"], _tee_cache.get("cert"), _tee_cache.get("payment")
    w3 = Web3(Web3.HTTPProvider(_RPC_URL))
    contract = w3.eth.contract(address=Web3.to_checksum_address(_REGISTRY), abi=_TEE_REGISTRY_ABI)
    tees = contract.functions.getActiveTEEs(0).call()
    if not tees:
        raise RuntimeError("No active LLM TEEs found in registry")
    tee = tees[0]
    endpoint, tls_cert, payment = tee[2], bytes(tee[4]), tee[1]
    _tee_cache.update({"endpoint": endpoint, "cert": tls_cert, "payment": payment})
    return endpoint, tls_cert, payment


async def _analyze(data: dict) -> dict:
    private_key = os.getenv("OG_PRIVATE_KEY")
    if not private_key:
        raise ValueError("OG_PRIVATE_KEY not set")

    endpoint, tls_cert, _ = _get_tee_endpoint()

    ssl_ctx = None
    if tls_cert:
        pem = ssl.DER_cert_to_PEM_cert(tls_cert)
        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_ctx.load_verify_locations(cadata=pem)
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_REQUIRED

    account = Account.from_key(private_key)
    signer = EthAccountSigner(account)
    x402 = x402Client()
    register_exact_evm_client(x402, signer, networks=[_NETWORK])
    register_upto_evm_client(x402, signer, networks=[_NETWORK])

    http = x402HttpxClient(x402, verify=ssl_ctx if ssl_ctx else True)
    try:
        response = await http.post(
            endpoint + _CHAT_PATH,
            json={
                "model": _MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": _build_prompt(data)},
                ],
                "max_tokens": 1200,
                "temperature": 0.0,
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {_PLACEHOLDER}",
                "X-SETTLEMENT-TYPE": "batch_hashed",
            },
            timeout=_TIMEOUT,
        )
        response.raise_for_status()
        result = json.loads((await response.aread()).decode())
        choices = result.get("choices", [])
        if not choices:
            raise RuntimeError(f"No choices in response: {result}")
        content = choices[0].get("message", {}).get("content", "")
        m = re.search(r"\{.*\}", content, re.DOTALL)
        if not m:
            raise ValueError(f"Could not parse JSON: {content[:200]}")
        parsed = json.loads(m.group())
        parsed["tee_signature"] = result.get("tee_signature")
        parsed["tee_timestamp"] = result.get("tee_timestamp")
        return parsed
    finally:
        await http.aclose()


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))
            result = asyncio.run(_analyze(data))
            self._respond(200, result)
        except Exception as e:
            self._respond(500, {"detail": str(e)})

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _respond(self, code, payload):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass
