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
  badges: { id: number; name: string; description: string | null; earned_at: string }[]
}

type Challenge = {
  id: string
  type: string
  title: string
  description: string
  xp_max: number
  linked_lesson_slug: string
}

type QuizResult = {
  message: string
  xp_awarded: number
  score: number
  new_badges: string[]
  profile: QuestProfile
}

export function InvestorQuestPage() {
  const [profile, setProfile] = useState<QuestProfile | null>(null)
  const [challenges, setChallenges] = useState<Challenge[]>([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState<string | null>(null)
  const [lastResult, setLastResult] = useState('')
  const [newBadges, setNewBadges] = useState<string[]>([])

  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      try {
        const challengePayload = await apiRequest<{ challenges: Challenge[] }>('/api/quest/challenges')
        setChallenges(challengePayload.challenges)
        if (isAuthenticated()) {
          const profileData = await apiRequest<QuestProfile>('/api/quest/profile', {
            headers: getAuthHeaders(),
          })
          setProfile(profileData)
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unable to load Investor Quest data.')
      } finally {
        setLoading(false)
      }
    }
    void loadData()
  }, [])

  const submitQuiz = async (quizId: string, score: number) => {
    if (!isAuthenticated()) return
    setSubmitting(quizId)
    setLastResult('')
    setNewBadges([])
    try {
      const data = await apiRequest<QuizResult>('/api/quest/quiz/submit', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ quiz_id: quizId, score }),
      })
      setProfile(data.profile)
      setNewBadges(data.new_badges)
      const xpMsg = data.xp_awarded > 0 ? ` (+${data.xp_awarded} XP)` : ' (already completed)'
      setLastResult(`${quizId}: ${data.message}${xpMsg} — Score: ${data.score}%`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to submit quiz.')
    } finally {
      setSubmitting(null)
    }
  }

  const submitChallenge = async (challengeId: string, xpReward: number) => {
    if (!isAuthenticated()) return
    setSubmitting(challengeId)
    setLastResult('')
    setNewBadges([])
    try {
      const data = await apiRequest<{ message: string; xp_awarded: number; new_badges: string[]; profile: QuestProfile }>(
        '/api/quest/challenge/submit',
        {
          method: 'POST',
          headers: getAuthHeaders(),
          body: JSON.stringify({ challenge_id: challengeId, xp_reward: xpReward }),
        },
      )
      setProfile(data.profile)
      setNewBadges(data.new_badges)
      const xpMsg = data.xp_awarded > 0 ? ` (+${data.xp_awarded} XP)` : ' (already completed)'
      setLastResult(`${challengeId}: ${data.message}${xpMsg}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to submit challenge.')
    } finally {
      setSubmitting(null)
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
              {' · '}
              <strong>XP:</strong> {profile.xp}
              {' · '}
              <span className="muted">{profile.xp_to_next_level} XP to next level</span>
            </p>
            {newBadges.length > 0 && (
              <p style={{ color: 'var(--color-accent, #c0f0f7)' }}>
                🏅 New badge{newBadges.length > 1 ? 's' : ''} earned: {newBadges.join(', ')}!
              </p>
            )}
            {lastResult && <p style={{ color: 'var(--color-brand-light, #3e9fcd)' }}>{lastResult}</p>}
            {profile.badges.length > 0 && (
              <div>
                <h3>Badges ({profile.badges.length})</h3>
                <ul className="feature-list">
                  {profile.badges.map((b) => (
                    <li key={b.id}>
                      <strong>{b.name}</strong>
                      {b.description && ` — ${b.description}`}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </Card>

      <section className="card-grid">
        {challenges.map((challenge) => (
          <Card
            key={challenge.id}
            title={challenge.title}
            subtitle={`${challenge.type === 'quiz' ? 'Quiz' : 'Challenge'} · up to ${challenge.xp_max} XP`}
          >
            <p>{challenge.description}</p>
            <p className="muted">Related lesson: {challenge.linked_lesson_slug}</p>
            <Button
              onClick={() =>
                challenge.type === 'quiz'
                  ? void submitQuiz(challenge.id, 85) // simulate a high-score submission for demo
                  : void submitChallenge(challenge.id, challenge.xp_max)
              }
              disabled={submitting === challenge.id}
            >
              {submitting === challenge.id
                ? 'Submitting…'
                : challenge.type === 'quiz'
                  ? 'Submit Quiz (Demo: 85%)'
                  : 'Complete Challenge'}
            </Button>
          </Card>
        ))}
      </section>
    </div>
  )
}
