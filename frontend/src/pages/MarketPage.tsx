import { useState } from 'react'
import type { FormEvent } from 'react'
import { Button } from '../components/common/Button'
import { Card } from '../components/common/Card'
import { DisclaimerBanner } from '../components/common/DisclaimerBanner'
import { apiRequest } from '../services/http'

type QuoteResponse = {
  symbol: string
  company_name: string
  current_price: number
  daily_percent_change: number
}

type ProfileResponse = {
  symbol: string
  company_name: string
  exchange: string
  finnhub_industry: string
}

export function MarketPage() {
  const [symbol, setSymbol] = useState('AAPL')
  const [quote, setQuote] = useState<QuoteResponse | null>(null)
  const [profile, setProfile] = useState<ProfileResponse | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const lookupQuote = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setLoading(true)
    setError('')
    try {
      const cleanedSymbol = encodeURIComponent(symbol.trim().toUpperCase())
      const [quotePayload, profilePayload] = await Promise.all([
        apiRequest<QuoteResponse>(`/api/market/quote?symbol=${cleanedSymbol}`),
        apiRequest<ProfileResponse>(`/api/market/profile?symbol=${cleanedSymbol}`),
      ])
      setQuote(quotePayload)
      setProfile(profilePayload)
    } catch (requestError) {
      setQuote(null)
      setProfile(null)
      setError(requestError instanceof Error ? requestError.message : 'Unable to load quote data.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-stack">
      <DisclaimerBanner />
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
          {profile && (
            <ul className="feature-list">
              <li>Exchange: {profile.exchange || 'N/A'}</li>
              <li>Sector: {profile.finnhub_industry || 'Unclassified'}</li>
            </ul>
          )}
        </Card>
      )}
    </div>
  )
}
