import { Card } from '../components/common/Card'

export function AccountPage() {
  return (
    <section className="card-grid">
      <Card title="Account overview">
        <p>Protected account data will show profile details, saved portfolios, watchlists, and future learning progress once you log in.</p>
      </Card>
      <Card title="Saved items">
        <ul className="feature-list">
          <li>Saved portfolios</li>
          <li>Watchlists</li>
          <li>Assistant chat history</li>
        </ul>
      </Card>
    </section>
  )
}
