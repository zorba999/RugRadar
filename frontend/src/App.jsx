import { useState } from 'react'
import LandingPage from './components/LandingPage'
import AnalyzerWizard from './components/AnalyzerWizard'
import ResultsPage from './components/ResultsPage'

export default function App() {
  const [page, setPage] = useState('landing')
  const [result, setResult] = useState(null)
  const [tokenMeta, setTokenMeta] = useState(null)

  const handleResult = (data, meta) => {
    setResult(data)
    setTokenMeta(meta)
    setPage('results')
  }

  return (
    <div className="min-h-screen" style={{ background: '#080c14' }}>
      {page === 'landing' && <LandingPage onStart={() => setPage('analyzer')} />}
      {page === 'analyzer' && <AnalyzerWizard onResult={handleResult} onBack={() => setPage('landing')} />}
      {page === 'results' && <ResultsPage result={result} tokenMeta={tokenMeta} onReset={() => setPage('landing')} />}
    </div>
  )
}
