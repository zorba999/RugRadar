import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from analyzer import run_analysis

st.set_page_config(
    page_title="Token Launch Risk Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stApp { background-color: #0e1117; }

    .risk-badge {
        display: inline-block;
        padding: 6px 18px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 1rem;
        letter-spacing: 1px;
    }
    .score-card {
        background: linear-gradient(135deg, #1a1f2e, #252d3d);
        border-radius: 16px;
        padding: 28px;
        text-align: center;
        border: 1px solid #2a3347;
    }
    .score-number {
        font-size: 4.5rem;
        font-weight: 900;
        line-height: 1;
    }
    .category-card {
        background: #1a1f2e;
        border-radius: 12px;
        padding: 16px;
        border: 1px solid #2a3347;
        margin-bottom: 10px;
    }
    .flag-item {
        padding: 8px 12px;
        border-radius: 8px;
        margin: 4px 0;
        font-size: 0.9rem;
    }
    .red-flag { background-color: #2d1515; border-left: 3px solid #ff4444; }
    .green-flag { background-color: #0f2d1a; border-left: 3px solid #00cc66; }
    .og-badge {
        background: linear-gradient(90deg, #6c3de0, #3d9be9);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .section-header {
        color: #8892a4;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)


def get_score_color(score: int) -> str:
    if score <= 20:
        return "#00cc66"
    elif score <= 40:
        return "#88cc00"
    elif score <= 60:
        return "#ffaa00"
    elif score <= 80:
        return "#ff6600"
    else:
        return "#ff2244"


def get_risk_badge_style(risk_level: str) -> str:
    colors = {
        "VERY LOW":  ("background:#0f2d1a; color:#00cc66; border:1px solid #00cc66;"),
        "LOW":       ("background:#1a2d0f; color:#88cc00; border:1px solid #88cc00;"),
        "MEDIUM":    ("background:#2d200f; color:#ffaa00; border:1px solid #ffaa00;"),
        "HIGH":      ("background:#2d150f; color:#ff6600; border:1px solid #ff6600;"),
        "CRITICAL":  ("background:#2d0f0f; color:#ff2244; border:1px solid #ff2244;"),
    }
    return colors.get(risk_level, colors["MEDIUM"])


def get_recommendation_style(rec: str) -> str:
    if "AVOID" in rec:
        return "color:#ff2244; font-weight:700; font-size:1.1rem;"
    elif "EXTREME" in rec:
        return "color:#ff6600; font-weight:700; font-size:1.1rem;"
    elif "CAUTION" in rec:
        return "color:#ffaa00; font-weight:700; font-size:1.1rem;"
    else:
        return "color:#00cc66; font-weight:700; font-size:1.1rem;"


def render_gauge(score: int) -> go.Figure:
    color = get_score_color(score)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#4a5568", "tickfont": {"color": "#8892a4"}},
            "bar": {"color": color, "thickness": 0.3},
            "bgcolor": "#1a1f2e",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 20],  "color": "#0a1a0f"},
                {"range": [20, 40], "color": "#1a2a0a"},
                {"range": [40, 60], "color": "#2a1a00"},
                {"range": [60, 80], "color": "#2a1000"},
                {"range": [80, 100], "color": "#1a0000"},
            ],
            "threshold": {"line": {"color": color, "width": 4}, "thickness": 0.8, "value": score},
        },
        number={"font": {"color": color, "size": 60}, "suffix": "/100"},
    ))
    fig.update_layout(
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        height=280,
        margin=dict(l=30, r=30, t=20, b=20),
        font={"color": "#e2e8f0"},
    )
    return fig


def render_radar(categories: dict) -> go.Figure:
    labels = ["Tokenomics", "Vesting", "Team", "Liquidity", "Contract"]
    keys = ["tokenomics", "vesting", "team", "liquidity", "contract"]
    scores = [categories.get(k, {}).get("score", 0) for k in keys]
    scores_closed = scores + [scores[0]]
    labels_closed = labels + [labels[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=scores_closed,
        theta=labels_closed,
        fill="toself",
        fillcolor="rgba(255, 68, 68, 0.15)",
        line=dict(color="#ff4444", width=2),
        name="Risk Score",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="#1a1f2e",
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(color="#8892a4", size=10), gridcolor="#2a3347"),
            angularaxis=dict(tickfont=dict(color="#e2e8f0", size=12), gridcolor="#2a3347"),
        ),
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        showlegend=False,
        height=320,
        margin=dict(l=50, r=50, t=30, b=30),
    )
    return fig


def render_category_bars(categories: dict):
    keys = ["tokenomics", "vesting", "team", "liquidity", "contract"]
    labels = ["Tokenomics", "Vesting", "Team", "Liquidity", "Contract"]
    for key, label in zip(keys, labels):
        cat = categories.get(key, {})
        score = cat.get("score", 0)
        findings = cat.get("findings", [])
        color = get_score_color(score)

        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{label}**")
            bar_html = f"""
            <div style="background:#1a1f2e; border-radius:6px; height:10px; margin:4px 0 8px 0;">
                <div style="background:{color}; width:{score}%; height:10px; border-radius:6px; transition:width 0.5s;"></div>
            </div>"""
            st.markdown(bar_html, unsafe_allow_html=True)
            for f in findings:
                st.markdown(f"<small style='color:#8892a4;'>• {f}</small>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<p style='text-align:right; color:{color}; font-weight:700; font-size:1.3rem;'>{score}</p>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color:#1a1f2e; margin:8px 0;'>", unsafe_allow_html=True)


st.markdown("""
<div style='display:flex; align-items:center; gap:12px; margin-bottom:8px;'>
    <h1 style='margin:0; font-size:1.8rem;'>🔍 Token Launch Risk Analyzer</h1>
    <span class='og-badge'>Powered by OpenGradient TEE</span>
</div>
<p style='color:#8892a4; margin-bottom:24px;'>Verifiable AI-powered rug pull detection — results cryptographically secured via Trusted Execution Environment</p>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 📋 Token Info")
    st.markdown("<p class='section-header'>Basic Info</p>", unsafe_allow_html=True)

    token_name = st.text_input("Token Name", placeholder="e.g. MoonProtocol")
    token_symbol = st.text_input("Token Symbol", placeholder="e.g. MOON")
    chain = st.selectbox("Chain", ["Ethereum", "BSC", "Base", "Solana", "Polygon", "Avalanche", "Arbitrum", "Other"])
    total_supply = st.text_input("Total Supply", placeholder="e.g. 1,000,000,000")
    token_price = st.text_input("Token Price (USD)", placeholder="e.g. $0.001")
    hard_cap = st.text_input("Hard Cap (USD)", placeholder="e.g. $500,000")

    st.markdown("---")
    st.markdown("<p class='section-header'>Tokenomics (%)</p>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        team_allocation = st.number_input("Team", 0, 100, 20, help="% allocated to team/founders")
        investor_allocation = st.number_input("Investors", 0, 100, 15, help="% for private investors")
        public_allocation = st.number_input("Public Sale", 0, 100, 20, help="% in IDO/presale")
    with col_b:
        ecosystem_allocation = st.number_input("Ecosystem", 0, 100, 30, help="% for treasury/rewards")
        liquidity_allocation = st.number_input("Liquidity", 0, 100, 15, help="% for DEX liquidity")

    total_pct = team_allocation + investor_allocation + public_allocation + ecosystem_allocation + liquidity_allocation
    if total_pct != 100:
        st.warning(f"⚠️ Allocations sum to {total_pct}% (should be 100%)")

    st.markdown("---")
    st.markdown("<p class='section-header'>Vesting & Liquidity</p>", unsafe_allow_html=True)

    vesting_schedule = st.text_area(
        "Vesting Schedule",
        placeholder="e.g. Team: 12mo cliff, 24mo linear. Investors: 6mo cliff, 12mo linear. Public: 20% TGE, 4mo linear.",
        height=90,
    )
    liquidity_locked = st.selectbox("Liquidity Locked?", ["Unknown", "Yes", "No"])
    lock_duration = st.text_input("Lock Duration", placeholder="e.g. 12 months")
    dex = st.text_input("DEX", placeholder="e.g. Uniswap v3")

    st.markdown("---")
    st.markdown("<p class='section-header'>Team & Contract</p>", unsafe_allow_html=True)

    team_doxxed = st.selectbox("Team Doxxed?", ["Unknown", "Yes - Fully", "Yes - Partially", "No - Anonymous"])
    previous_projects = st.text_input("Previous Projects", placeholder="e.g. None / ProjectX (failed)")
    team_wallets = st.text_area("Team Wallet Addresses (optional)", placeholder="0x123...\n0x456...", height=70)

    audited = st.selectbox("Smart Contract Audited?", ["Unknown", "Yes", "No", "In Progress"])
    audit_firm = st.text_input("Audit Firm", placeholder="e.g. CertiK, PeckShield")
    mint_function = st.selectbox("Mint Function Exists?", ["Unknown", "Yes", "No"])
    ownership_renounced = st.selectbox("Ownership Renounced?", ["Unknown", "Yes", "No"])

    st.markdown("---")
    additional_info = st.text_area(
        "Additional Info / Notes",
        placeholder="Whitepaper quality, social media presence, KYC, anything else...",
        height=80,
    )

    analyze_btn = st.button("🔍 Analyze Token", type="primary", use_container_width=True)


if analyze_btn:
    if not token_name or not token_symbol:
        st.error("❌ Please enter at least the token name and symbol.")
    else:
        form_data = {
            "token_name": token_name,
            "token_symbol": token_symbol,
            "chain": chain,
            "total_supply": total_supply,
            "token_price": token_price,
            "hard_cap": hard_cap,
            "team_allocation": team_allocation,
            "investor_allocation": investor_allocation,
            "public_allocation": public_allocation,
            "ecosystem_allocation": ecosystem_allocation,
            "liquidity_allocation": liquidity_allocation,
            "vesting_schedule": vesting_schedule,
            "liquidity_locked": liquidity_locked,
            "lock_duration": lock_duration,
            "dex": dex,
            "team_doxxed": team_doxxed,
            "previous_projects": previous_projects,
            "team_wallets": team_wallets,
            "audited": audited,
            "audit_firm": audit_firm,
            "mint_function": mint_function,
            "ownership_renounced": ownership_renounced,
            "additional_info": additional_info,
        }

        with st.spinner("🧠 Analyzing via OpenGradient TEE... (verifiable inference in progress)"):
            try:
                result = run_analysis(form_data)
                st.session_state["result"] = result
                st.session_state["token_name"] = token_name
                st.session_state["token_symbol"] = token_symbol
            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                st.info("Make sure your OG_PRIVATE_KEY is set in the .env file and funded with $OPG testnet tokens.")


if "result" in st.session_state:
    result = st.session_state["result"]
    t_name = st.session_state.get("token_name", "Token")
    t_symbol = st.session_state.get("token_symbol", "???")

    score = result.get("rug_pull_score", 0)
    risk_level = result.get("risk_level", "UNKNOWN")
    summary = result.get("summary", "")
    categories = result.get("categories", {})
    red_flags = result.get("red_flags", [])
    green_flags = result.get("green_flags", [])
    recommendation = result.get("recommendation", "N/A")

    score_color = get_score_color(score)
    badge_style = get_risk_badge_style(risk_level)
    rec_style = get_recommendation_style(recommendation)

    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#1a1f2e,#252d3d); border-radius:16px; padding:20px 28px; border:1px solid #2a3347; margin-bottom:20px;'>
        <div style='display:flex; align-items:center; gap:16px; flex-wrap:wrap;'>
            <div>
                <h2 style='margin:0; font-size:1.5rem;'>{t_name} <span style='color:#8892a4; font-weight:400;'>(${t_symbol})</span></h2>
                <p style='color:#8892a4; margin:4px 0 0 0; font-size:0.85rem;'>OpenGradient TEE Verified Analysis</p>
            </div>
            <div style='margin-left:auto; display:flex; align-items:center; gap:12px;'>
                <span class='risk-badge' style='{badge_style}'>{risk_level}</span>
                <span style='color:{score_color}; font-size:2.5rem; font-weight:900;'>{score}/100</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("<p class='section-header'>Rug Pull Risk Score</p>", unsafe_allow_html=True)
        st.plotly_chart(render_gauge(score), use_container_width=True)

        st.markdown(f"""
        <div style='background:#1a1f2e; border-radius:12px; padding:16px; border:1px solid #2a3347; margin-top:8px;'>
            <p class='section-header'>Recommendation</p>
            <p style='{rec_style}'>{recommendation}</p>
            <p style='color:#cbd5e0; font-size:0.9rem; margin-top:8px;'>{summary}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("<p class='section-header'>Risk Radar by Category</p>", unsafe_allow_html=True)
        st.plotly_chart(render_radar(categories), use_container_width=True)

    st.markdown("---")

    col3, col4 = st.columns([3, 2])

    with col3:
        st.markdown("<p class='section-header'>Category Breakdown</p>", unsafe_allow_html=True)
        render_category_bars(categories)

    with col4:
        st.markdown("<p class='section-header'>Red Flags 🚩</p>", unsafe_allow_html=True)
        if red_flags:
            for flag in red_flags:
                st.markdown(f"<div class='flag-item red-flag'>🚩 {flag}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:#8892a4;'>No red flags detected</p>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p class='section-header'>Green Flags ✅</p>", unsafe_allow_html=True)
        if green_flags:
            for flag in green_flags:
                st.markdown(f"<div class='flag-item green-flag'>✅ {flag}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:#8892a4;'>No green flags detected</p>", unsafe_allow_html=True)

    st.markdown("---")
    with st.expander("📄 Raw JSON Result (On-Chain Storable)"):
        st.json(result)
        st.markdown("""
        <p style='color:#8892a4; font-size:0.8rem;'>
        💡 This JSON result was generated inside a TEE (Trusted Execution Environment) via OpenGradient's network. 
        The hash of this result can be stored on-chain as a verifiable, tamper-proof record for the community to reference.
        </p>
        """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div style='background:#1a1f2e; border-radius:16px; padding:48px; text-align:center; border:1px solid #2a3347;'>
        <div style='font-size:4rem; margin-bottom:16px;'>🔍</div>
        <h3 style='color:#e2e8f0;'>Fill in the token details in the sidebar to get started</h3>
        <p style='color:#8892a4;'>The AI will analyze tokenomics, vesting, team, liquidity, and contract security — all verified via OpenGradient TEE</p>
        <br>
        <div style='display:flex; justify-content:center; gap:32px; flex-wrap:wrap;'>
            <div style='text-align:center;'>
                <div style='font-size:1.5rem;'>🧠</div>
                <p style='color:#8892a4; font-size:0.85rem;'>LLM Analysis via TEE</p>
            </div>
            <div style='text-align:center;'>
                <div style='font-size:1.5rem;'>🔐</div>
                <p style='color:#8892a4; font-size:0.85rem;'>Cryptographic Verification</p>
            </div>
            <div style='text-align:center;'>
                <div style='font-size:1.5rem;'>⛓️</div>
                <p style='color:#8892a4; font-size:0.85rem;'>On-Chain Storable Result</p>
            </div>
            <div style='text-align:center;'>
                <div style='font-size:1.5rem;'>🚩</div>
                <p style='color:#8892a4; font-size:0.85rem;'>Red Flag Detection</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
