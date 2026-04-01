import { Shield, Zap, Lock, ChevronRight, Github } from 'lucide-react'

const features = [
  { icon: Shield, title: 'TEE Verified', desc: 'Every analysis runs inside a Trusted Execution Environment — cryptographically tamper-proof.' },
  { icon: Zap, title: 'Instant Analysis', desc: 'LLM powered by OpenGradient network scores tokenomics, vesting, team, and contract in seconds.' },
  { icon: Lock, title: 'On-Chain Proof', desc: 'Results include tee_signature & tee_timestamp — storable on-chain as verifiable evidence.' },
]

const riskLevels = [
  { label: 'VERY LOW', color: '#00cc66', bg: 'rgba(0,204,102,0.1)' },
  { label: 'LOW', color: '#88cc00', bg: 'rgba(136,204,0,0.1)' },
  { label: 'MEDIUM', color: '#ffaa00', bg: 'rgba(255,170,0,0.1)' },
  { label: 'HIGH', color: '#ff6600', bg: 'rgba(255,102,0,0.1)' },
  { label: 'CRITICAL', color: '#ff2244', bg: 'rgba(255,34,68,0.1)' },
]

export default function LandingPage({ onStart }) {
  return (
    <div className="grid-bg min-h-screen">
      <nav className="flex items-center justify-between px-8 py-5 border-b border-border">
        <div className="flex items-center gap-3">
          <span className="text-2xl">🔍</span>
          <span className="font-bold text-lg">RugRadar</span>
          <span className="text-xs px-2 py-0.5 rounded-full font-mono font-semibold"
            style={{ background: 'rgba(108,61,224,0.2)', color: '#a78bfa', border: '1px solid rgba(108,61,224,0.4)' }}>
            Powered by OpenGradient TEE
          </span>
        </div>
        <a href="https://docs.opengradient.ai" target="_blank" rel="noreferrer"
          className="flex items-center gap-1 text-sm text-slate-400 hover:text-white transition-colors">
          Docs <ChevronRight size={14} />
        </a>
      </nav>

      <div className="max-w-5xl mx-auto px-6 pt-24 pb-16 text-center">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium mb-8"
          style={{ background: 'rgba(108,61,224,0.15)', border: '1px solid rgba(108,61,224,0.35)', color: '#a78bfa' }}>
          <span className="w-2 h-2 rounded-full bg-purple-400 animate-pulse" />
          OpenGradient Testnet · Base Sepolia
        </div>

        <h1 className="text-6xl font-black mb-6 leading-tight">
          <span className="gradient-text">Detect Rug Pulls</span>
          <br />
          <span className="text-white">Before They Happen</span>
        </h1>

        <p className="text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
          AI-powered token launch risk analysis secured by{' '}
          <span className="text-white font-semibold">Trusted Execution Environments</span>.
          Verifiable, tamper-proof, on-chain ready.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <button onClick={onStart}
            className="glow flex items-center gap-3 px-8 py-4 rounded-xl text-white font-bold text-lg transition-all hover:scale-105 active:scale-95"
            style={{ background: 'linear-gradient(135deg, #6c3de0, #3d9be9)' }}>
            Analyze a Token
            <ChevronRight size={20} />
          </button>
          <a href="https://docs.opengradient.ai/developers/sdk/" target="_blank" rel="noreferrer"
            className="flex items-center gap-2 px-8 py-4 rounded-xl font-semibold text-slate-300 hover:text-white transition-all hover:bg-white/5"
            style={{ border: '1px solid #1e2d47' }}>
            <Github size={18} />
            SDK Docs
          </a>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 pb-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {features.map(({ icon: Icon, title, desc }) => (
            <div key={title} className="rounded-2xl p-6 transition-all hover:border-purple-500/40"
              style={{ background: '#0f1623', border: '1px solid #1e2d47' }}>
              <div className="w-10 h-10 rounded-xl flex items-center justify-center mb-4"
                style={{ background: 'rgba(108,61,224,0.2)' }}>
                <Icon size={20} className="text-purple-400" />
              </div>
              <h3 className="font-bold text-white mb-2">{title}</h3>
              <p className="text-sm text-slate-400 leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 pb-24">
        <div className="rounded-2xl p-8" style={{ background: '#0f1623', border: '1px solid #1e2d47' }}>
          <p className="text-center text-sm text-slate-500 mb-6 uppercase tracking-widest font-semibold">Risk Scale</p>
          <div className="flex flex-wrap items-center justify-center gap-3">
            {riskLevels.map(({ label, color, bg }) => (
              <div key={label} className="flex items-center gap-2 px-4 py-2 rounded-full text-sm font-bold"
                style={{ background: bg, border: `1px solid ${color}40`, color }}>
                {label}
              </div>
            ))}
          </div>
          <p className="text-center text-xs text-slate-600 mt-6 font-mono">
            Score: 0 (safe) → 100 (definite rug) · Powered by Claude Sonnet via OpenGradient TEE
          </p>
        </div>
      </div>
    </div>
  )
}
