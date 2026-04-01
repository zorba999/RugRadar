import { useState } from 'react'
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, PolarRadiusAxis } from 'recharts'
import { RotateCcw, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react'

const SCORE_CONFIG = [
  { max: 20,  color: '#00cc66', label: 'VERY LOW',  bg: 'rgba(0,204,102,0.1)',   border: 'rgba(0,204,102,0.3)'   },
  { max: 40,  color: '#88cc00', label: 'LOW',        bg: 'rgba(136,204,0,0.1)',  border: 'rgba(136,204,0,0.3)'  },
  { max: 60,  color: '#ffaa00', label: 'MEDIUM',     bg: 'rgba(255,170,0,0.1)',  border: 'rgba(255,170,0,0.3)'  },
  { max: 80,  color: '#ff6600', label: 'HIGH',       bg: 'rgba(255,102,0,0.1)',  border: 'rgba(255,102,0,0.3)'  },
  { max: 101, color: '#ff2244', label: 'CRITICAL',   bg: 'rgba(255,34,68,0.1)',  border: 'rgba(255,34,68,0.3)'  },
]

const REC_CONFIG = {
  'AVOID':                  { color: '#ff2244', icon: '🚫' },
  'EXTREME CAUTION':        { color: '#ff6600', icon: '⚠️' },
  'PROCEED WITH CAUTION':   { color: '#ffaa00', icon: '🟡' },
  'RELATIVELY SAFE':        { color: '#00cc66', icon: '✅' },
}

function getConfig(score) {
  return SCORE_CONFIG.find(c => score < c.max) || SCORE_CONFIG[4]
}

function ScoreRing({ score }) {
  const { color } = getConfig(score)
  const r = 80
  const circ = 2 * Math.PI * r
  const dash = (score / 100) * circ

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width="200" height="200" className="-rotate-90">
        <circle cx="100" cy="100" r={r} fill="none" stroke="#1e2d47" strokeWidth="12" />
        <circle cx="100" cy="100" r={r} fill="none" stroke={color} strokeWidth="12"
          strokeDasharray={`${dash} ${circ}`} strokeLinecap="round"
          style={{ transition: 'stroke-dasharray 1s ease', filter: `drop-shadow(0 0 8px ${color})` }} />
      </svg>
      <div className="absolute text-center">
        <div className="text-5xl font-black" style={{ color }}>{score}</div>
        <div className="text-xs text-slate-500 font-mono mt-1">/ 100</div>
      </div>
    </div>
  )
}

function CategoryBar({ label, score }) {
  const { color } = getConfig(score)
  return (
    <div className="space-y-1.5">
      <div className="flex justify-between text-sm">
        <span className="text-slate-300 font-medium">{label}</span>
        <span className="font-bold font-mono" style={{ color }}>{score}</span>
      </div>
      <div className="h-2 rounded-full" style={{ background: '#1e2d47' }}>
        <div className="h-full rounded-full transition-all duration-700"
          style={{ width: `${score}%`, background: color, boxShadow: `0 0 6px ${color}60` }} />
      </div>
    </div>
  )
}

export default function ResultsPage({ result, tokenMeta, onReset }) {
  const [showProof, setShowProof] = useState(false)

  const score = result?.rug_pull_score ?? 0
  const risk = result?.risk_level ?? 'UNKNOWN'
  const summary = result?.summary ?? ''
  const categories = result?.categories ?? {}
  const redFlags = result?.red_flags ?? []
  const greenFlags = result?.green_flags ?? []
  const recommendation = result?.recommendation ?? ''
  const teeSignature = result?.tee_signature
  const teeTimestamp = result?.tee_timestamp
  const txHash = result?.transaction_hash
  const walletAddress = result?.wallet_address

  const { color, bg, border } = getConfig(score)
  const recConf = Object.entries(REC_CONFIG).find(([k]) => recommendation.includes(k))?.[1] || { color: '#fff', icon: '❓' }

  const radarData = [
    { subject: 'Tokenomics', score: categories?.tokenomics?.score ?? 0 },
    { subject: 'Vesting',    score: categories?.vesting?.score ?? 0 },
    { subject: 'Team',       score: categories?.team?.score ?? 0 },
    { subject: 'Liquidity',  score: categories?.liquidity?.score ?? 0 },
    { subject: 'Contract',   score: categories?.contract?.score ?? 0 },
  ]

  return (
    <div className="min-h-screen grid-bg">
      <nav className="flex items-center justify-between px-8 py-5 border-b border-border">
        <div className="flex items-center gap-3">
          <span className="text-2xl">🔍</span>
          <span className="font-bold">RugRadar</span>
        </div>
        <button onClick={onReset}
          className="flex items-center gap-2 text-sm px-4 py-2 rounded-lg text-slate-400 hover:text-white transition-all"
          style={{ border: '1px solid #1e2d47' }}>
          <RotateCcw size={14} /> New Analysis
        </button>
      </nav>

      <div className="max-w-6xl mx-auto px-6 py-10">

        {/* Header */}
        <div className="rounded-2xl p-6 mb-6 flex flex-wrap items-center justify-between gap-4"
          style={{ background: '#0f1623', border: `1px solid ${border}` }}>
          <div>
            <h1 className="text-2xl font-black text-white">
              {tokenMeta?.name} <span className="text-slate-500 font-normal">${tokenMeta?.symbol}</span>
            </h1>
            <p className="text-sm text-slate-400 mt-1 max-w-xl">{summary}</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="px-4 py-2 rounded-full text-sm font-bold"
              style={{ background: bg, border: `1px solid ${border}`, color }}>
              {risk}
            </div>
            <div className="text-right">
              <div className="text-xs text-slate-500 mb-1">RECOMMENDATION</div>
              <div className="font-bold text-sm" style={{ color: recConf.color }}>
                {recConf.icon} {recommendation}
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* Score Ring */}
          <div className="rounded-2xl p-6 flex flex-col items-center justify-center"
            style={{ background: '#0f1623', border: '1px solid #1e2d47' }}>
            <p className="text-xs text-slate-500 uppercase tracking-widest font-semibold mb-6">Rug Pull Risk Score</p>
            <ScoreRing score={score} />
            <p className="text-xs text-slate-600 font-mono mt-4">0 = safe · 100 = definite rug</p>
          </div>

          {/* Radar Chart */}
          <div className="rounded-2xl p-6" style={{ background: '#0f1623', border: '1px solid #1e2d47' }}>
            <p className="text-xs text-slate-500 uppercase tracking-widest font-semibold mb-4">Risk Radar</p>
            <ResponsiveContainer width="100%" height={220}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="#1e2d47" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: '#8892a4', fontSize: 11 }} />
                <PolarRadiusAxis domain={[0, 100]} tick={false} axisLine={false} />
                <Radar dataKey="score" stroke="#ff4444" fill="#ff4444" fillOpacity={0.15} strokeWidth={2} />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          {/* Category Bars */}
          <div className="rounded-2xl p-6" style={{ background: '#0f1623', border: '1px solid #1e2d47' }}>
            <p className="text-xs text-slate-500 uppercase tracking-widest font-semibold mb-5">Category Scores</p>
            <div className="space-y-4">
              {['tokenomics', 'vesting', 'team', 'liquidity', 'contract'].map(k => (
                <CategoryBar key={k} label={k.charAt(0).toUpperCase() + k.slice(1)} score={categories?.[k]?.score ?? 0} />
              ))}
            </div>
          </div>
        </div>

        {/* Flags + Findings */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="rounded-2xl p-6" style={{ background: '#0f1623', border: '1px solid #1e2d47' }}>
            <p className="text-xs text-slate-500 uppercase tracking-widest font-semibold mb-4">🚩 Red Flags</p>
            {redFlags.length ? redFlags.map((f, i) => (
              <div key={i} className="flex items-start gap-3 px-3 py-2.5 rounded-lg mb-2 text-sm text-red-300"
                style={{ background: 'rgba(255,34,68,0.08)', borderLeft: '3px solid #ff2244' }}>
                <span className="mt-0.5 text-red-500 flex-shrink-0">✕</span>{f}
              </div>
            )) : <p className="text-sm text-slate-600">No red flags detected</p>}
          </div>
          <div className="rounded-2xl p-6" style={{ background: '#0f1623', border: '1px solid #1e2d47' }}>
            <p className="text-xs text-slate-500 uppercase tracking-widest font-semibold mb-4">✅ Green Flags</p>
            {greenFlags.length ? greenFlags.map((f, i) => (
              <div key={i} className="flex items-start gap-3 px-3 py-2.5 rounded-lg mb-2 text-sm text-green-300"
                style={{ background: 'rgba(0,204,102,0.08)', borderLeft: '3px solid #00cc66' }}>
                <span className="mt-0.5 text-green-500 flex-shrink-0">✓</span>{f}
              </div>
            )) : <p className="text-sm text-slate-600">No green flags detected</p>}
          </div>
        </div>

        {/* Category Findings */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
          {['tokenomics', 'vesting', 'team', 'liquidity', 'contract'].map(k => {
            const cat = categories?.[k] || {}
            const { color: c } = getConfig(cat.score ?? 0)
            return (
              <div key={k} className="rounded-xl p-4" style={{ background: '#0f1623', border: '1px solid #1e2d47' }}>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm font-semibold text-white capitalize">{k}</span>
                  <span className="text-sm font-bold font-mono" style={{ color: c }}>{cat.score ?? 0}/100</span>
                </div>
                {(cat.findings || []).map((f, i) => (
                  <p key={i} className="text-xs text-slate-400 mb-1.5">• {f}</p>
                ))}
              </div>
            )
          })}
        </div>

        {/* TEE Proof */}
        <div className="rounded-2xl overflow-hidden" style={{ border: '1px solid #1e2d47' }}>
          <button onClick={() => setShowProof(v => !v)}
            className="w-full flex items-center justify-between px-6 py-4 text-sm font-semibold text-slate-300 hover:text-white transition-colors"
            style={{ background: '#0f1623' }}>
            <div className="flex items-center gap-3">
              <span className="w-2 h-2 rounded-full bg-purple-400 animate-pulse" />
              🔐 TEE Cryptographic Proof — On-Chain Storable
            </div>
            {showProof ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>

          {showProof && (
            <div className="px-6 py-5 space-y-4" style={{ background: '#0a1220', borderTop: '1px solid #1e2d47' }}>
              <p className="text-xs text-slate-500 leading-relaxed">
                This analysis was executed inside a <span className="text-purple-400 font-semibold">Trusted Execution Environment (TEE)</span> on the OpenGradient network.
                The signature below proves the output was generated by a verified enclave and was not tampered with.
                Hash this JSON and store it on-chain as a verifiable community record.
              </p>
              {walletAddress && (
                <div className="rounded-xl p-4" style={{ background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.3)' }}>
                  <p className="text-xs text-slate-600 uppercase tracking-widest mb-2">⛓ Payment Wallet — Base Sepolia</p>
                  <p className="text-xs font-mono text-indigo-300 bg-black/30 px-3 py-2 rounded-lg break-all mb-2">{walletAddress}</p>
                  <div className="flex flex-wrap gap-3">
                    <a href={`https://sepolia.basescan.org/address/${walletAddress}#tokentxns`} target="_blank" rel="noreferrer"
                      className="inline-flex items-center gap-1.5 text-xs text-indigo-400 hover:text-indigo-300 transition-colors font-semibold">
                      🔍 OPG Token Transfers on BaseScan <ExternalLink size={12} />
                    </a>
                    {txHash && (
                      <a href={`https://sepolia.basescan.org/tx/${txHash}`} target="_blank" rel="noreferrer"
                        className="inline-flex items-center gap-1.5 text-xs text-indigo-400 hover:text-indigo-300 transition-colors font-semibold">
                        Tx Hash <ExternalLink size={12} />
                      </a>
                    )}
                  </div>
                </div>
              )}
              {teeTimestamp && (
                <div>
                  <p className="text-xs text-slate-600 uppercase tracking-widest mb-1">TEE Timestamp</p>
                  <p className="text-xs font-mono text-slate-400 bg-black/30 px-3 py-2 rounded-lg">{teeTimestamp}</p>
                </div>
              )}
              {teeSignature && (
                <div>
                  <p className="text-xs text-slate-600 uppercase tracking-widest mb-1">TEE Signature</p>
                  <p className="text-xs font-mono text-slate-400 bg-black/30 px-3 py-2 rounded-lg break-all">{teeSignature}</p>
                </div>
              )}
              <details className="text-xs">
                <summary className="cursor-pointer text-slate-500 hover:text-slate-300 transition-colors">View Raw JSON</summary>
                <pre className="mt-3 text-slate-400 bg-black/40 p-4 rounded-lg overflow-x-auto text-xs leading-relaxed font-mono">
                  {JSON.stringify(result, null, 2)}
                </pre>
              </details>
              <a href="https://docs.opengradient.ai/learn/onchain_inference/llm_execution.html"
                target="_blank" rel="noreferrer"
                className="inline-flex items-center gap-1.5 text-xs text-purple-400 hover:text-purple-300 transition-colors">
                Learn about TEE verification <ExternalLink size={12} />
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
