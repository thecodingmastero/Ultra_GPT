type CoachingEntry = {
  signal: string
  confidence: number
  coaching: string
}

const SIGNAL_LABELS: Record<string, string> = {
  panic_selling: 'Panic Selling',
  fomo: 'FOMO',
  overconfidence: 'Overconfidence',
  chasing_hot_stocks: 'Chasing Hot Stocks',
  lack_of_diversification: 'Lack of Diversification',
}

function formatSignalLabel(signal: string): string {
  return SIGNAL_LABELS[signal] ?? signal.replace(/_/g, ' ')
}

function formatConfidence(confidence: number): string {
  return `${Math.round(confidence * 100)}% match`
}

type BehavioralCoachingCardProps = {
  entry: CoachingEntry
}

export function BehavioralCoachingCard({ entry }: BehavioralCoachingCardProps) {
  return (
    <div className="coaching-card" role="note" aria-label={`Behavioral coaching: ${formatSignalLabel(entry.signal)}`}>
      <div className="coaching-card__header">
        <span className="coaching-card__signal">⚠ {formatSignalLabel(entry.signal)}</span>
        <span className="coaching-card__confidence">{formatConfidence(entry.confidence)}</span>
      </div>
      <p className="coaching-card__text">{entry.coaching}</p>
    </div>
  )
}

type BehavioralCoachingSectionProps = {
  coaching: CoachingEntry[]
}

export function BehavioralCoachingSection({ coaching }: BehavioralCoachingSectionProps) {
  if (coaching.length === 0) return null

  return (
    <div className="coaching-section">
      <p className="coaching-section__title">Behavioral coaching</p>
      {coaching.map((entry) => (
        <BehavioralCoachingCard key={entry.signal} entry={entry} />
      ))}
    </div>
  )
}
