from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from analyzer import run_analysis

app = FastAPI(title="Token Launch Risk Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class TokenData(BaseModel):
    token_name: str
    token_symbol: str
    chain: str = "Ethereum"
    total_supply: Optional[str] = ""
    token_price: Optional[str] = ""
    hard_cap: Optional[str] = ""
    team_allocation: int = 0
    investor_allocation: int = 0
    public_allocation: int = 0
    ecosystem_allocation: int = 0
    liquidity_allocation: int = 0
    vesting_schedule: Optional[str] = ""
    liquidity_locked: Optional[str] = "Unknown"
    lock_duration: Optional[str] = ""
    dex: Optional[str] = ""
    team_doxxed: Optional[str] = "Unknown"
    previous_projects: Optional[str] = ""
    team_wallets: Optional[str] = ""
    audited: Optional[str] = "Unknown"
    audit_firm: Optional[str] = ""
    mint_function: Optional[str] = "Unknown"
    ownership_renounced: Optional[str] = "Unknown"
    additional_info: Optional[str] = ""


@app.post("/analyze")
def analyze(data: TokenData):
    try:
        result = run_analysis(data.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}
