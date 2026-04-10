import asyncio
import json
import os
import re
from http.server import BaseHTTPRequestHandler
from pathlib import Path

import opengradient as og
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

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


async def _analyze(data: dict) -> dict:
    private_key = os.getenv("OG_PRIVATE_KEY")
    if not private_key:
        raise ValueError("OG_PRIVATE_KEY not set")

    llm = og.LLM(private_key=private_key)
    llm.ensure_opg_approval(min_allowance=5)

    completion = await llm.chat(
        model=og.TEE_LLM.CLAUDE_SONNET_4_6,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": _build_prompt(data)},
        ],
        max_tokens=1200,
        temperature=0.0,
        x402_settlement_mode=og.x402SettlementMode.INDIVIDUAL_FULL,
    )

    raw = completion.chat_output["content"].strip()
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if not m:
        raise ValueError(f"Could not parse JSON from LLM response: {raw[:200]}")

    parsed = json.loads(m.group())
    parsed["tee_signature"]    = completion.tee_signature
    parsed["tee_timestamp"]    = completion.tee_timestamp
    parsed["transaction_hash"] = completion.transaction_hash
    parsed["wallet_address"]   = llm._wallet_account.address
    return parsed


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
