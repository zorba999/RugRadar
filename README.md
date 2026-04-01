# 🔍 Token Launch Risk Analyzer

Verifiable AI-powered rug pull detection for IDO/presale token launches, built with the [OpenGradient SDK](https://docs.opengradient.ai/developers/sdk/).

## How It Works

1. Fill in token details (tokenomics, vesting, team, contract info) in the sidebar
2. The app sends the data to OpenGradient's LLM running inside a **TEE (Trusted Execution Environment)**
3. The LLM returns a structured **Rug Pull Risk Score (0-100)** with full breakdown
4. The JSON result is cryptographically verifiable and can be stored on-chain

## Features

- **Risk Score (0-100)** with gauge visualization
- **Radar chart** across 5 categories: Tokenomics, Vesting, Team, Liquidity, Contract
- **Red flags & Green flags** list
- **Recommendation**: AVOID / EXTREME CAUTION / PROCEED WITH CAUTION / RELATIVELY SAFE
- **Raw JSON** output ready to be hashed and stored on-chain

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env and add your private key
```

Your wallet needs **$OPG testnet tokens** on Base Sepolia.
Get them from: https://faucet.opengradient.ai

### 3. Run the app
```bash
streamlit run app.py
```

## Project Structure

```
├── app.py          # Streamlit UI
├── analyzer.py     # OpenGradient SDK integration
├── requirements.txt
├── .env.example
└── README.md
```
