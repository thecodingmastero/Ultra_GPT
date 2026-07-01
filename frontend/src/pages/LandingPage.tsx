import { Link } from 'react-router-dom'
import { Button } from '../components/common/Button'
import { Card } from '../components/common/Card'
import { DisclaimerBanner } from '../components/common/DisclaimerBanner'

const highlights = [
  {
    title: 'Education-first AI assistant',
    text: 'Ask investing questions in plain language and get coach-style explanations centered on risk awareness and long-term thinking.',
  },
  {
    title: 'Portfolio learning support',
    text: 'Enter tickers and share counts to review position weights, concentration flags, and simple educational feedback.',
  },
  {
    title: 'Live market context',
    text: 'Check real-time Finnhub-powered quotes and daily market moves without losing sight of disciplined investing principles.',
  },
]

export function LandingPage() {
  return (
    <div className="page-stack">
      <section className="hero">
        <div>
          <p className="section-eyebrow">Modern investing education</p>
          <h2>The Better Investor helps you learn, reflect, and build stronger investing habits.</h2>
          <p>
            Learn core concepts, explore portfolio trade-offs, and stay grounded in diversification, risk management, and emotional discipline.
          </p>
          <div className="hero__actions">
            <Link to="/assistant">
              <Button>Try the assistant</Button>
            </Link>
            <Link to="/portfolio">
              <Button variant="secondary">Analyze a portfolio</Button>
            </Link>
          </div>
        </div>
        <Card title="MVP focus" subtitle="Phase 1 foundations">
          <ul className="feature-list">
            <li>React + TypeScript route scaffold</li>
            <li>Flask API with modular blueprints</li>
            <li>Swappable AI and market data providers</li>
            <li>Visible educational disclaimer and safety guardrails</li>
          </ul>
        </Card>
      </section>

      <DisclaimerBanner />

      <section className="card-grid">
        {highlights.map((highlight) => (
          <Card key={highlight.title} title={highlight.title}>
            <p>{highlight.text}</p>
          </Card>
        ))}
      </section>
    </div>
  )
}
