import { useState } from 'react'
import type { FormEvent } from 'react'
import { Button } from '../components/common/Button'
import { Card } from '../components/common/Card'
import { apiRequest } from '../services/http'

type QuoteResponse = {
  symbol: string
  company_name: string
  current_price: number
  daily_percent_change: number
}

export function MarketPage() {
  const [symbol, setSymbol] = useState('AAPL')
  const [quote, setQuote] = useState<QuoteResponse | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const lookupQuote = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setLoading(true)
    setError('')
    try {
      const payload = await apiRequest<QuoteResponse>(`/api/market/quote?symbol=${encodeURIComponent(symbol.trim().toUpperCase())}`)
      setQuote(payload)
    } catch (requestError) {
      setQuote(null)
      setError(requestError instanceof Error ? requestError.message : 'Unable to load quote data.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-stack">
      <Card title="Market dashboard" subtitle="Finnhub quote lookup for stocks and ETFs">
        <form className="inline-form" onSubmit={lookupQuote}>
          <input
            className="text-input"
            value={symbol}
            onChange={(event) => setSymbol(event.target.value)}
            placeholder="Enter a symbol"
          />
          <Button type="submit">{loading ? 'Loading…' : 'Get quote'}</Button>
        </form>
        {error && <p className="error-text">{error}</p>}
      </Card>

      {quote && (
        <Card title={quote.company_name} subtitle={quote.symbol}>
          <div className="quote-grid">
            <div>
              <p className="muted">Current price</p>
              <h3>${quote.current_price.toFixed(2)}</h3>
            </div>
            <div>
              <p className="muted">Daily move</p>
              <h3 className={quote.daily_percent_change >= 0 ? 'positive-text' : 'negative-text'}>
                {quote.daily_percent_change.toFixed(2)}%
              </h3>
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}
