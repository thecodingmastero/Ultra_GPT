import { useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import { Button } from '../components/common/Button'
import { Card } from '../components/common/Card'
import { DisclaimerBanner } from '../components/common/DisclaimerBanner'
import { apiRequest } from '../services/http'

type HoldingInput = {
  symbol: string
  quantity: number
}

type AnalyzedPosition = {
  symbol: string
  company_name: string
  quantity: number
  price: number
  market_value: number
  weight: number
}

type PortfolioResponse = {
  summary: {
    total_market_value: number
    position_count: number
  }
  positions: AnalyzedPosition[]
  risk_flags: string[]
  educational_feedback: string
}

export function PortfolioPage() {
  const [holding, setHolding] = useState<HoldingInput>({ symbol: '', quantity: 1 })
  const [holdings, setHoldings] = useState<HoldingInput[]>([
    { symbol: 'AAPL', quantity: 2 },
    { symbol: 'VOO', quantity: 1 },
  ])
  const [analysis, setAnalysis] = useState<PortfolioResponse | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const totalQuantity = useMemo(() => holdings.reduce((sum, item) => sum + item.quantity, 0), [holdings])

  const addHolding = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!holding.symbol.trim() || holding.quantity <= 0) {
      return
    }
    setHoldings([...holdings, { symbol: holding.symbol.trim().toUpperCase(), quantity: holding.quantity }])
    setHolding({ symbol: '', quantity: 1 })
  }

  const analyze = async () => {
    setLoading(true)
    setError('')
    try {
      const payload = await apiRequest<PortfolioResponse>('/api/portfolio/analyze', {
        method: 'POST',
        body: JSON.stringify({ holdings }),
      })
      setAnalysis(payload)
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Analysis failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-stack">
      <DisclaimerBanner />
      <section className="two-column-grid">
        <Card title="Portfolio analyzer" subtitle="Add tickers and quantities for an educational review.">
          <form className="inline-form" onSubmit={addHolding}>
            <input
              aria-label="Ticker symbol"
              className="text-input"
              placeholder="Ticker"
              value={holding.symbol}
              onChange={(event) => setHolding({ ...holding, symbol: event.target.value })}
            />
            <input
              aria-label="Share quantity"
              className="text-input"
              min={1}
              step={1}
              type="number"
              value={holding.quantity}
              onChange={(event) => setHolding({ ...holding, quantity: Number(event.target.value) })}
            />
            <Button type="submit">Add holding</Button>
          </form>

          <div className="holding-list">
            {holdings.map((item, index) => (
              <div key={`${item.symbol}-${index}`} className="holding-row">
                <strong>{item.symbol}</strong>
                <span>{item.quantity} shares</span>
              </div>
            ))}
          </div>

          <p className="muted">Total entered shares: {totalQuantity}</p>
          {error && <p className="error-text">{error}</p>}
          <Button disabled={loading} onClick={analyze}>
            {loading ? 'Analyzing…' : 'Analyze portfolio'}
          </Button>
        </Card>

        <Card title="Educational feedback" subtitle="Position weights and concentration checks">
          {!analysis && <p className="muted">Run an analysis to review current weights, total value, and concentration flags.</p>}
          {analysis && (
            <div className="stack-sm">
              <p>
                Total market value: <strong>${analysis.summary.total_market_value.toLocaleString()}</strong>
              </p>
              <ul className="feature-list">
                {analysis.positions.map((position) => (
                  <li key={position.symbol}>
                    {position.symbol} · {Math.round(position.weight * 100)}% weight · ${position.market_value.toLocaleString()}
                  </li>
                ))}
              </ul>
              <div>
                <h3>Concentration flags</h3>
                <ul className="feature-list">
                  {analysis.risk_flags.map((flag) => (
                    <li key={flag}>{flag}</li>
                  ))}
                </ul>
              </div>
              <p>{analysis.educational_feedback}</p>
            </div>
          )}
        </Card>
      </section>
    </div>
  )
}
