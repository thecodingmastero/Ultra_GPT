import { Card } from '../components/common/Card'

const plans = [
  { name: 'Free', price: '$0', details: 'Starter assistant usage, limited saved portfolios, basic learning access.' },
  { name: 'Single', price: '$10/month', details: 'Expanded assistant usage, more saved portfolios, and deeper progress analytics.' },
  { name: 'Family', price: 'Custom', details: 'Shared learning support and account-level access for households.' },
  { name: 'Business', price: 'Custom', details: 'Multi-user education access and future team features.' },
]

export function PricingPage() {
  return (
    <section className="card-grid">
      {plans.map((plan) => (
        <Card key={plan.name} title={plan.name} subtitle={plan.price}>
          <p>{plan.details}</p>
        </Card>
      ))}
    </section>
  )
}
