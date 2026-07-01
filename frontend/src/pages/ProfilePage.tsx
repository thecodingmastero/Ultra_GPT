import { Card } from '../components/common/Card'

export function ProfilePage() {
  return (
    <section className="card-grid">
      <Card title="Profile overview">
        <p>Protected profile data includes account details, saved portfolios, and lesson progress tracking.</p>
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
