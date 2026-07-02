import { useEffect, useState } from 'react'
import { Button } from '../components/common/Button'
import { Card } from '../components/common/Card'
import { getAuthHeaders, isAuthenticated } from '../services/auth'
import { apiRequest } from '../services/http'

type QuestProfile = {
  user_id: number
  level: number
  xp: number
  xp_to_next_level: number
  badges: { id: number; name: string; description: string | null }[]
}

export function InvestorQuestPage() {
  const [profile, setProfile] = useState<QuestProfile | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [lastResult, setLastResult] = useState('')

  useEffect(() => {
    if (!isAuthenticated()) return
    const loadProfile = async () => {
      setLoading(true)
      try {
        const data = await apiRequest<QuestProfile>('/api/quest/profile', {
          headers: getAuthHeaders(),
        })
        setProfile(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unable to load quest profile.')
      } finally {
        setLoading(false)
      }
    }
    void loadProfile()
  }, [])

  const submitDemoChallenge = async () => {
    if (!isAuthenticated()) return
    setSubmitting(true)
    setLastResult('')
    try {
      const data = await apiRequest<{ message: string; xp_awarded: number; profile: QuestProfile }>(
        '/api/quest/challenge/submit',
        {
          method: 'POST',
          headers: getAuthHeaders(),
          body: JSON.stringify({ challenge_id: 'demo-quiz-1', xp_reward: 10 }),
        },
      )
      setProfile(data.profile)
      setLastResult(data.message + (data.xp_awarded > 0 ? ` (+${data.xp_awarded} XP)` : ''))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to submit challenge.')
    } finally {
      setSubmitting(false)
    }
  }

  if (!isAuthenticated()) {
    return (
      <div className="page-stack">
        <Card title="Investor Quest" subtitle="Gamified investing education">
          <p className="muted">Please log in to access your Investor Quest profile, earn XP, and collect badges.</p>
        </Card>
      </div>
    )
  }

  return (
    <div className="page-stack">
      <Card
        title="Investor Quest"
        subtitle="Level up your investing knowledge. XP is earned through quizzes, challenges, and simulations — not by chatting with the AI."
      >
        {loading && <p className="muted">Loading quest profile…</p>}
        {error && <p className="error-text">{error}</p>}
        {profile && (
          <div className="stack-sm">
            <p>
              <strong>Level:</strong> {profile.level}
            </p>
            <p>
              <strong>XP:</strong> {profile.xp} &mdash; {profile.xp_to_next_level} XP to next level
            </p>
            <p>
              <strong>Badges earned:</strong> {profile.badges.length}
            </p>
            {profile.badges.length > 0 && (
              <ul>
                {profile.badges.map((b) => (
                  <li key={b.id}>
                    <strong>{b.name}</strong>
                    {b.description && ` — ${b.description}`}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </Card>

      <Card title="Demo Challenge" subtitle="Phase 2A scaffold — full quiz engine coming in Phase 2C">
        <p className="muted">
          Complete challenges to earn XP. The full quiz engine, investing simulations, and achievement tracking are
          planned for Phase 2C.
        </p>
        {lastResult && <p style={{ color: 'var(--color-success)' }}>{lastResult}</p>}
        <Button onClick={() => void submitDemoChallenge()} disabled={submitting}>
          {submitting ? 'Submitting…' : 'Complete Demo Challenge (+10 XP)'}
        </Button>
      </Card>
    </div>
  )
}
