import { useState } from 'react'
import { ArrowLeft, ArrowRight, Loader2, ShieldAlert } from 'lucide-react'

const CHAINS = ['Ethereum', 'BSC', 'Base', 'Solana', 'Polygon', 'Avalanche', 'Arbitrum', 'Other']
const STEPS = ['Basic Info', 'Tokenomics', 'Team & Contract']

const defaultForm = {
  token_name: '', token_symbol: '', chain: 'Ethereum',
  total_supply: '', token_price: '', hard_cap: '',
  team_allocation: 20, investor_allocation: 15, public_allocation: 20,
  ecosystem_allocation: 30, liquidity_allocation: 15,
  vesting_schedule: '', liquidity_locked: 'Unknown', lock_duration: '', dex: '',
  team_doxxed: 'Unknown', previous_projects: '', team_wallets: '',
  audited: 'Unknown', audit_firm: '', mint_function: 'Unknown',
  ownership_renounced: 'Unknown', additional_info: '',
}

function Label({ children, hint }) {
  return (
    <div className="flex items-center justify-between mb-1.5">
      <label className="text-sm font-medium text-slate-300">{children}</label>
      {hint && <span className="text-xs text-slate-500">{hint}</span>}
    </div>
  )
}

function Input({ value, onChange, placeholder, type = 'text', className = '' }) {
  return (
    <input type={type} value={value} onChange={onChange} placeholder={placeholder}
      className={`w-full px-3 py-2.5 rounded-lg text-sm text-white placeholder-slate-600 outline-none transition-all focus:ring-1 focus:ring-purple-500 ${className}`}
      style={{ background: '#0a1220', border: '1px solid #1e2d47' }} />
  )
}

function Select({ value, onChange, options }) {
  return (
    <select value={value} onChange={onChange}
      className="w-full px-3 py-2.5 rounded-lg text-sm text-white outline-none transition-all focus:ring-1 focus:ring-purple-500"
      style={{ background: '#0a1220', border: '1px solid #1e2d47' }}>
      {options.map(o => <option key={o} value={o}>{o}</option>)}
    </select>
  )
}

function NumberSlider({ value, onChange, label }) {
  const color = value > 30 ? '#ff6600' : value > 20 ? '#ffaa00' : '#6c3de0'
  return (
    <div>
      <div className="flex justify-between mb-1">
        <span className="text-xs text-slate-400">{label}</span>
        <span className="text-xs font-bold font-mono" style={{ color }}>{value}%</span>
      </div>
      <input type="range" min={0} max={100} value={value} onChange={onChange}
        className="w-full h-1.5 rounded-full appearance-none cursor-pointer"
        style={{ accentColor: color, background: `linear-gradient(to right, ${color} ${value}%, #1e2d47 ${value}%)` }} />
    </div>
  )
}

function Step1({ form, set }) {
  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label>Token Name *</Label>
          <Input value={form.token_name} onChange={e => set('token_name', e.target.value)} placeholder="e.g. MoonProtocol" />
        </div>
        <div>
          <Label>Symbol *</Label>
          <Input value={form.token_symbol} onChange={e => set('token_symbol', e.target.value)} placeholder="e.g. MOON" />
        </div>
      </div>
      <div>
        <Label>Chain</Label>
        <Select value={form.chain} onChange={e => set('chain', e.target.value)} options={CHAINS} />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label>Total Supply</Label>
          <Input value={form.total_supply} onChange={e => set('total_supply', e.target.value)} placeholder="e.g. 1,000,000,000" />
        </div>
        <div>
          <Label>Token Price (USD)</Label>
          <Input value={form.token_price} onChange={e => set('token_price', e.target.value)} placeholder="e.g. $0.001" />
        </div>
      </div>
      <div>
        <Label>Hard Cap (USD)</Label>
        <Input value={form.hard_cap} onChange={e => set('hard_cap', e.target.value)} placeholder="e.g. $500,000" />
      </div>
    </div>
  )
}

function Step2({ form, set }) {
  const total = form.team_allocation + form.investor_allocation + form.public_allocation + form.ecosystem_allocation + form.liquidity_allocation
  const overLimit = total !== 100
  return (
    <div className="space-y-5">
      <div className="rounded-xl p-4 space-y-4" style={{ background: '#0a1220', border: '1px solid #1e2d47' }}>
        <p className="text-xs text-slate-500 uppercase tracking-widest font-semibold">Token Allocation</p>
        <NumberSlider label="Team / Founders" value={form.team_allocation} onChange={e => set('team_allocation', +e.target.value)} />
        <NumberSlider label="Private Investors" value={form.investor_allocation} onChange={e => set('investor_allocation', +e.target.value)} />
        <NumberSlider label="Public Sale / IDO" value={form.public_allocation} onChange={e => set('public_allocation', +e.target.value)} />
        <NumberSlider label="Ecosystem / Treasury" value={form.ecosystem_allocation} onChange={e => set('ecosystem_allocation', +e.target.value)} />
        <NumberSlider label="Liquidity" value={form.liquidity_allocation} onChange={e => set('liquidity_allocation', +e.target.value)} />
        <div className={`flex items-center justify-between text-sm font-mono pt-2 border-t ${overLimit ? 'border-red-500/30' : 'border-green-500/20'}`}
          style={{ borderColor: overLimit ? 'rgba(239,68,68,0.3)' : 'rgba(0,204,102,0.2)' }}>
          <span className="text-slate-500">Total</span>
          <span className={`font-bold ${overLimit ? 'text-red-400' : 'text-green-400'}`}>{total}% {overLimit ? '⚠ must be 100%' : '✓'}</span>
        </div>
      </div>

      <div>
        <Label hint="Optional">Vesting Schedule</Label>
        <textarea value={form.vesting_schedule} onChange={e => set('vesting_schedule', e.target.value)}
          placeholder="e.g. Team: 12mo cliff + 24mo linear. Investors: 6mo cliff + 12mo linear."
          rows={3} className="w-full px-3 py-2.5 rounded-lg text-sm text-white placeholder-slate-600 outline-none transition-all focus:ring-1 focus:ring-purple-500 resize-none"
          style={{ background: '#0a1220', border: '1px solid #1e2d47' }} />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label>Liquidity Locked?</Label>
          <Select value={form.liquidity_locked} onChange={e => set('liquidity_locked', e.target.value)} options={['Unknown', 'Yes', 'No']} />
        </div>
        <div>
          <Label>Lock Duration</Label>
          <Input value={form.lock_duration} onChange={e => set('lock_duration', e.target.value)} placeholder="e.g. 12 months" />
        </div>
      </div>

      <div>
        <Label>DEX</Label>
        <Input value={form.dex} onChange={e => set('dex', e.target.value)} placeholder="e.g. Uniswap v3" />
      </div>
    </div>
  )
}

function Step3({ form, set }) {
  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label>Team Doxxed?</Label>
          <Select value={form.team_doxxed} onChange={e => set('team_doxxed', e.target.value)}
            options={['Unknown', 'Yes - Fully', 'Yes - Partially', 'No - Anonymous']} />
        </div>
        <div>
          <Label>Previous Projects</Label>
          <Input value={form.previous_projects} onChange={e => set('previous_projects', e.target.value)} placeholder="e.g. None / ProjectX" />
        </div>
      </div>
      <div>
        <Label hint="Optional">Team Wallet Addresses</Label>
        <textarea value={form.team_wallets} onChange={e => set('team_wallets', e.target.value)}
          placeholder={'0x123...\n0x456...'}
          rows={2} className="w-full px-3 py-2.5 rounded-lg text-sm text-white placeholder-slate-600 outline-none transition-all focus:ring-1 focus:ring-purple-500 resize-none font-mono"
          style={{ background: '#0a1220', border: '1px solid #1e2d47' }} />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label>Contract Audited?</Label>
          <Select value={form.audited} onChange={e => set('audited', e.target.value)} options={['Unknown', 'Yes', 'No', 'In Progress']} />
        </div>
        <div>
          <Label>Audit Firm</Label>
          <Input value={form.audit_firm} onChange={e => set('audit_firm', e.target.value)} placeholder="e.g. CertiK" />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label>Mint Function?</Label>
          <Select value={form.mint_function} onChange={e => set('mint_function', e.target.value)} options={['Unknown', 'Yes', 'No']} />
        </div>
        <div>
          <Label>Ownership Renounced?</Label>
          <Select value={form.ownership_renounced} onChange={e => set('ownership_renounced', e.target.value)} options={['Unknown', 'Yes', 'No']} />
        </div>
      </div>

      <div>
        <Label hint="Optional">Additional Notes</Label>
        <textarea value={form.additional_info} onChange={e => set('additional_info', e.target.value)}
          placeholder="Whitepaper quality, social media presence, KYC status, anything else..."
          rows={3} className="w-full px-3 py-2.5 rounded-lg text-sm text-white placeholder-slate-600 outline-none transition-all focus:ring-1 focus:ring-purple-500 resize-none"
          style={{ background: '#0a1220', border: '1px solid #1e2d47' }} />
      </div>
    </div>
  )
}

function LoadingScreen({ token }) {
  const steps = [
    'Connecting to OpenGradient network...',
    'Routing to TEE enclave...',
    'Running Claude Sonnet inference...',
    'Verifying TEE signature...',
    'Parsing risk assessment...',
  ]
  const [current] = useState(0)

  return (
    <div className="flex flex-col items-center justify-center py-24 text-center">
      <div className="relative mb-8">
        <div className="w-24 h-24 rounded-full flex items-center justify-center animate-pulse-slow"
          style={{ background: 'rgba(108,61,224,0.2)', border: '2px solid rgba(108,61,224,0.5)' }}>
          <ShieldAlert size={40} className="text-purple-400" />
        </div>
        <div className="absolute inset-0 rounded-full animate-spin-slow"
          style={{ border: '2px solid transparent', borderTopColor: '#6c3de0', borderRightColor: 'transparent' }} />
      </div>
      <h3 className="text-xl font-bold text-white mb-2">Analyzing <span className="gradient-text">${token}</span></h3>
      <p className="text-sm text-slate-500 mb-8">Verifiable inference running inside TEE enclave</p>
      <div className="space-y-2 w-full max-w-xs">
        {steps.map((s, i) => (
          <div key={i} className={`flex items-center gap-3 text-xs px-4 py-2 rounded-lg transition-all ${i <= current ? 'text-slate-300' : 'text-slate-600'}`}
            style={{ background: i <= current ? 'rgba(108,61,224,0.1)' : 'transparent' }}>
            <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${i < current ? 'bg-green-400' : i === current ? 'bg-purple-400 animate-pulse' : 'bg-slate-700'}`} />
            {s}
          </div>
        ))}
      </div>
    </div>
  )
}

export default function AnalyzerWizard({ onResult, onBack }) {
  const [step, setStep] = useState(0)
  const [form, setForm] = useState(defaultForm)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const canProceed = step === 0 ? (form.token_name && form.token_symbol) : true

  const handleSubmit = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${import.meta.env.VITE_API_BASE || ''}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Analysis failed')
      }
      const data = await res.json()
      onResult(data, { name: form.token_name, symbol: form.token_symbol })
    } catch (e) {
      setError(e.message)
      setLoading(false)
    }
  }

  if (loading) return (
    <div className="min-h-screen grid-bg">
      <LoadingScreen token={form.token_symbol || form.token_name} />
    </div>
  )

  return (
    <div className="min-h-screen grid-bg flex flex-col">
      <nav className="flex items-center justify-between px-8 py-5 border-b border-border">
        <button onClick={onBack} className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors">
          <ArrowLeft size={16} /> Back
        </button>
        <div className="flex items-center gap-2">
          {STEPS.map((s, i) => (
            <div key={i} className="flex items-center gap-2">
              <button onClick={() => i < step && setStep(i)}
                className={`flex items-center gap-2 text-sm font-medium transition-colors ${i === step ? 'text-white' : i < step ? 'text-purple-400 cursor-pointer' : 'text-slate-600'}`}>
                <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold
                  ${i === step ? 'text-white' : i < step ? 'text-purple-400' : 'text-slate-700'}`}
                  style={{
                    background: i === step ? 'linear-gradient(135deg,#6c3de0,#3d9be9)' : i < step ? 'rgba(108,61,224,0.2)' : '#1e2d47',
                    border: i < step ? '1px solid rgba(108,61,224,0.4)' : 'none'
                  }}>
                  {i < step ? '✓' : i + 1}
                </span>
                <span className="hidden sm:inline">{s}</span>
              </button>
              {i < STEPS.length - 1 && <span className="text-slate-700 mx-1">—</span>}
            </div>
          ))}
        </div>
        <div className="w-16" />
      </nav>

      <div className="flex-1 flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-lg">
          <div className="rounded-2xl p-8" style={{ background: '#0f1623', border: '1px solid #1e2d47' }}>
            <h2 className="text-xl font-bold text-white mb-6">{STEPS[step]}</h2>

            {step === 0 && <Step1 form={form} set={set} />}
            {step === 1 && <Step2 form={form} set={set} />}
            {step === 2 && <Step3 form={form} set={set} />}

            {error && (
              <div className="mt-4 flex items-start gap-3 px-4 py-3 rounded-lg text-sm text-red-400"
                style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)' }}>
                <span className="mt-0.5">✕</span>
                <span>{error}</span>
              </div>
            )}

            <div className="flex gap-3 mt-8">
              {step > 0 && (
                <button onClick={() => setStep(s => s - 1)}
                  className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-slate-400 hover:text-white transition-all"
                  style={{ border: '1px solid #1e2d47' }}>
                  <ArrowLeft size={16} /> Back
                </button>
              )}
              <button
                onClick={() => step < 2 ? setStep(s => s + 1) : handleSubmit()}
                disabled={!canProceed}
                className="flex-1 flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold text-white transition-all hover:scale-105 active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:scale-100"
                style={{ background: 'linear-gradient(135deg,#6c3de0,#3d9be9)' }}>
                {step < 2 ? (<>Next <ArrowRight size={16} /></>) : (<>🔍 Analyze Token</>)}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
