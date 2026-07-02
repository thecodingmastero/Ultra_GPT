import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Button } from '../components/common/Button'
import { Card } from '../components/common/Card'
import { DisclaimerBanner } from '../components/common/DisclaimerBanner'
import { getAuthHeaders } from '../services/auth'
import { apiRequest } from '../services/http'

type Holding = {
  id: number
  symbol: string
  quantity: number
}

type Concentration = {
  summary: {
    total_market_value: number
    position_count: number
  }
  top_positions: Array<{
    symbol: string
    market_value: number
    weight: number
  }>
  sector_breakdown: Array<{
    sector: string
    weight: number
  }>
  risk_flags: string[]
  educational_feedback: string
}

export function PortfolioPage() {
  const [symbol, setSymbol] = useState('')
  const [quantity, setQuantity] = useState(1)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [holdings, setHoldings] = useState<Holding[]>([])
  const [analysis, setAnalysis] = useState<Concentration | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const loadHoldings = async () => {
    const payload = await apiRequest<{ holdings: Holding[] }>('/api/holdings', {
      headers: getAuthHeaders(),
    })
    setHoldings(payload.holdings)
  }

  const loadAnalysis = async () => {
    try {
      const payload = await apiRequest<Concentration>('/api/portfolio/concentration', {
        headers: getAuthHeaders(),
      })
      setAnalysis(payload)
    } catch (requestError) {
      setAnalysis(null)
      setError(requestError instanceof Error ? requestError.message : 'Unable to load concentration analysis.')
    }
  }

  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      setError('')
      try {
        await loadHoldings()
        await loadAnalysis()
      } catch (requestError) {
        setError(requestError instanceof Error ? requestError.message : 'Unable to load holdings.')
      } finally {
        setLoading(false)
      }
    }
    void loadData()
  }, [])

  const submitHolding = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')
    setLoading(true)
    try {
      if (editingId) {
        await apiRequest<Holding>(`/api/holdings/${editingId}`, {
          method: 'PUT',
          headers: getAuthHeaders(),
          body: JSON.stringify({ symbol, quantity }),
        })
      } else {
        await apiRequest<Holding>('/api/holdings', {
          method: 'POST',
          headers: getAuthHeaders(),
          body: JSON.stringify({ symbol, quantity }),
        })
      }
      setSymbol('')
      setQuantity(1)
      setEditingId(null)
      await loadHoldings()
      await loadAnalysis()
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Unable to save holding.')
    } finally {
      setLoading(false)
    }
  }

  const editHolding = (holding: Holding) => {
    setEditingId(holding.id)
    setSymbol(holding.symbol)
    setQuantity(holding.quantity)
  }

  const deleteHolding = async (id: number) => {
    setError('')
    setLoading(true)
    try {
      await apiRequest<{ deleted: boolean }>(`/api/holdings/${id}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      })
      await loadHoldings()
      await loadAnalysis()
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Unable to delete holding.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-stack">
      <DisclaimerBanner />
      <section className="two-column-grid">
        <Card title="Portfolio holdings" subtitle="Add, edit, and remove holdings for your educational analysis.">
          <form className="inline-form" onSubmit={submitHolding}>
            <input
              aria-label="Ticker symbol"
              className="text-input"
              placeholder="Ticker"
              value={symbol}
              onChange={(event) => setSymbol(event.target.value.toUpperCase())}
            />
            <input
              aria-label="Share quantity"
              className="text-input"
              min={1}
              step={1}
              type="number"
              value={quantity}
              onChange={(event) => setQuantity(Number(event.target.value))}
            />
            <Button type="submit">{editingId ? 'Update holding' : 'Add holding'}</Button>
          </form>
          {error && <p className="error-text">{error}</p>}
          {loading && <p className="muted">Updating portfolio…</p>}
          <div className="holding-list">
            {holdings.map((item) => (
              <div key={item.id} className="holding-row">
                <span>
                  <strong>{item.symbol}</strong> · {item.quantity} shares
                </span>
                <span className="inline-form">
                  <Button variant="secondary" onClick={() => editHolding(item)}>
                    Edit
                  </Button>
                  <Button variant="secondary" onClick={() => deleteHolding(item.id)}>
                    Delete
                  </Button>
                </span>
              </div>
            ))}
          </div>
        </Card>

        <Card title="Concentration analysis" subtitle="Sector mix and concentration risk flags">
          {!analysis && <p className="muted">Add holdings to see an educational concentration analysis.</p>}
          {analysis && (
            <div className="stack-sm">
              <p>
                Total market value: <strong>${analysis.summary.total_market_value.toLocaleString()}</strong>
              </p>
              <div>
                <h3>Top positions</h3>
                <ul className="feature-list">
                  {analysis.top_positions.map((position) => (
                    <li key={position.symbol}>
                      {position.symbol} · {Math.round(position.weight * 100)}% · ${position.market_value.toLocaleString()}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h3>Sector breakdown</h3>
                <ul className="feature-list">
                  {analysis.sector_breakdown.map((sector) => (
                    <li key={sector.sector}>
                      {sector.sector} · {Math.round(sector.weight * 100)}%
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h3>Risk flags</h3>
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
