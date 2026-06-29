import { Card } from '../components/common/Card'

const lessons = [
  'Stocks and how ownership works',
  'ETFs and index funds',
  'Bonds and risk trade-offs',
  'Diversification basics',
  'Dollar-cost averaging',
  'Behavioral finance and emotional discipline',
]

export function LearnPage() {
  return (
    <section className="card-grid">
      {lessons.map((lesson) => (
        <Card key={lesson} title={lesson}>
          <p>Short-form lesson content can expand here in Phase 2, with progress tracking and deeper educational modules.</p>
        </Card>
      ))}
    </section>
  )
}
