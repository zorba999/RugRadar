import asyncio
import json
import os
import re
from pathlib import Path
import opengradient as og
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

SYSTEM_PROMPT = """You are an expert Web3 security analyst specializing in detecting rug pulls, scams, and high-risk token launches. 
You analyze IDO/presale projects and provide a structured risk assessment.

You MUST respond with ONLY valid JSON in this exact format:
{
  "rug_pull_score": <integer 0-100>,
  "risk_level": "<VERY LOW | LOW | MEDIUM | HIGH | CRITICAL>",
  "summary": "<2-3 sentence overall assessment>",
  "categories": {
    "tokenomics": {
      "score": <integer 0-100>,
      "findings": ["<finding1>", "<finding2>"]
    },
    "vesting": {
      "score": <integer 0-100>,
      "findings": ["<finding1>", "<finding2>"]
    },
    "team": {
      "score": <integer 0-100>,
      "findings": ["<finding1>", "<finding2>"]
    },
    "liquidity": {
      "score": <integer 0-100>,
      "findings": ["<finding1>", "<finding2>"]
    },
    "contract": {
      "score": <integer 0-100>,
      "findings": ["<finding1>", "<finding2>"]
    }
  },
  "red_flags": ["<flag1>", "<flag2>"],
  "green_flags": ["<flag1>", "<flag2>"],
  "recommendation": "<AVOID | EXTREME CAUTION | PROCEED WITH CAUTION | RELATIVELY SAFE>"
}

Score meaning: 0 = no risk, 100 = definite rug pull. Be strict and conservative."""


def build_user_prompt(data: dict) -> str:
    return f"""Analyze this token launch for rug pull risk:

TOKEN: {data.get('token_name', 'N/A')} (${data.get('token_symbol', 'N/A')})
CHAIN: {data.get('chain', 'N/A')}
TOTAL SUPPLY: {data.get('total_supply', 'N/A')}
TOKEN PRICE: {data.get('token_price', 'N/A')}
HARD CAP: {data.get('hard_cap', 'N/A')}

TOKENOMICS BREAKDOWN:
- Team/Founders allocation: {data.get('team_allocation', 'N/A')}%
- Investors/Private sale: {data.get('investor_allocation', 'N/A')}%
- Public sale: {data.get('public_allocation', 'N/A')}%
- Ecosystem/Treasury: {data.get('ecosystem_allocation', 'N/A')}%
- Liquidity: {data.get('liquidity_allocation', 'N/A')}%

VESTING SCHEDULE:
{data.get('vesting_schedule', 'Not provided')}

LIQUIDITY:
- Locked: {data.get('liquidity_locked', 'Unknown')}
- Lock duration: {data.get('lock_duration', 'Unknown')}
- DEX: {data.get('dex', 'Unknown')}

TEAM INFO:
- Doxxed: {data.get('team_doxxed', 'Unknown')}
- Previous projects: {data.get('previous_projects', 'None mentioned')}
- Team wallet addresses: {data.get('team_wallets', 'Not provided')}

CONTRACT:
- Audited: {data.get('audited', 'Unknown')}
- Audit firm: {data.get('audit_firm', 'N/A')}
- Mint function: {data.get('mint_function', 'Unknown')}
- Ownership renounced: {data.get('ownership_renounced', 'Unknown')}

ADDITIONAL INFO:
{data.get('additional_info', 'None')}

Provide your JSON risk assessment now."""


async def analyze_token(data: dict) -> dict:
    private_key = os.getenv("OG_PRIVATE_KEY")
    if not private_key:
        raise ValueError("OG_PRIVATE_KEY not set in .env file")

    llm = og.LLM(private_key=private_key)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(data)},
    ]

    result = await llm.chat(
        model=og.TEE_LLM.CLAUDE_SONNET_4_6,
        messages=messages,
        max_tokens=1200,
        temperature=0.0,
    )

    raw_text = result.chat_output["content"].strip()

    json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    else:
        raise ValueError(f"Could not parse JSON from LLM response: {raw_text[:200]}")


def run_analysis(data: dict) -> dict:
    return asyncio.run(analyze_token(data))
