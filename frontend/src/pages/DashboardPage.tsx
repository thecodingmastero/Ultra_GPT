import { Card } from '../components/common/Card'

export function DashboardPage() {
  return (
    <section className="card-grid">
      <Card title="Learning snapshot" subtitle="Track educational progress">
        <ul className="feature-list">
          <li>Review completed lessons and next modules</li>
          <li>Revisit risk management and diversification fundamentals</li>
        </ul>
      </Card>
      <Card title="Portfolio lab" subtitle="Explore concentration risk">
        <p>Use Portfolio Lab to run educational concentration analysis with your saved holdings.</p>
      </Card>
      <Card title="Ask AI" subtitle="Educational assistant">
        <p>The assistant explains concepts and guardrails responses away from direct financial advice.</p>
      </Card>
    </section>
  )
}
