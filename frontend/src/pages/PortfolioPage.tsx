import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Button } from '../components/common/Button'
import { Card } from '../components/common/Card'
import { DisclaimerBanner } from '../components/common/DisclaimerBanner'
import { UpgradePrompt } from '../components/common/UpgradePrompt'
import { getAuthHeaders } from '../services/auth'
import { apiRequest } from '../services/http'
import { fetchUserPlan } from '../services/plan'

type Holding = {
  id: number
  symbol: string
  quantity: number
}

type AnalysisSummary = {
  total_market_value: number
  position_count: number
  sector_count: number
  diversification_score: number
  volatility_label: string
  hhi: number
}

type Learningsuggestion = {
  lesson_slug: string
  reason: string
}

type Concentration = {
  summary: AnalysisSummary
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
  learning_suggestions?: Learningsuggestion[]
}

const VOLATILITY_COLORS: Record<string, string> = {
  low: '#3e9fcd',
  moderate: '#428ce2',
  high: '#c0a000',
}

export function PortfolioPage() {
  const [symbol, setSymbol] = useState('')
  const [quantity, setQuantity] = useState(1)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [holdings, setHoldings] = useState<Holding[]>([])
  const [analysis, setAnalysis] = useState<Concentration | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [planId, setPlanId] = useState<string>('free')

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
      const msg = requestError instanceof Error ? requestError.message : ''
      // If 403, user is on free plan — silently suppress
      if (!msg.includes('not available on your current plan')) {
        setError(msg || 'Unable to load concentration analysis.')
      }
    }
  }

  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      setError('')
      try {
        const plan = await fetchUserPlan()
        setPlanId(plan?.plan_id ?? 'free')
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

  const isPaidPlan = planId !== 'free'

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

        <Card title="Concentration analysis" subtitle="Sector mix, volatility heuristic, and concentration risk flags">
          {!isPaidPlan && (
            <UpgradePrompt message="Full portfolio analytics — including sector breakdown, volatility scoring, and diversification insights — is available on the Single plan ($10/month)." />
          )}
          {isPaidPlan && !analysis && (
            <p className="muted">Add holdings to see an educational concentration analysis.</p>
          )}
          {isPaidPlan && analysis && (
            <div className="stack-sm">
              <p>
                Total market value: <strong>${analysis.summary.total_market_value.toLocaleString()}</strong>
                {' · '}
                {analysis.summary.position_count} position{analysis.summary.position_count !== 1 ? 's' : ''}
                {' · '}
                {analysis.summary.sector_count} sector{analysis.summary.sector_count !== 1 ? 's' : ''}
              </p>
              <p>
                Diversification score:{' '}
                <strong>{analysis.summary.diversification_score}%</strong>
                {' · '}
                Volatility:{' '}
                <strong style={{ color: VOLATILITY_COLORS[analysis.summary.volatility_label] ?? '#c0f0f7' }}>
                  {analysis.summary.volatility_label}
                </strong>
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
              {analysis.risk_flags.length > 0 && (
                <div>
                  <h3>Risk flags</h3>
                  <ul className="feature-list">
                    {analysis.risk_flags.map((flag) => (
                      <li key={flag}>{flag}</li>
                    ))}
                  </ul>
                </div>
              )}
              <p>{analysis.educational_feedback}</p>
              {analysis.learning_suggestions && analysis.learning_suggestions.length > 0 && (
                <div>
                  <h3>Suggested lessons</h3>
                  <ul className="feature-list">
                    {analysis.learning_suggestions.map((s) => (
                      <li key={s.lesson_slug}>
                        <strong>{s.lesson_slug}</strong>: {s.reason}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </Card>
      </section>
    </div>
  )
}
