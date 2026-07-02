import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Button } from '../components/common/Button'
import { Card } from '../components/common/Card'
import { getAuthHeaders } from '../services/auth'
import { apiRequest } from '../services/http'

type Profile = {
  id: number
  email: string
  full_name: string
  saved_portfolios: number
  watchlists: number
  lesson_progress_entries: number
  achievements: number
}

export function ProfilePage() {
  const [profile, setProfile] = useState<Profile | null>(null)
  const [fullName, setFullName] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const payload = await apiRequest<Profile>('/api/account/me', {
          headers: getAuthHeaders(),
        })
        setProfile(payload)
        setFullName(payload.full_name)
      } catch (requestError) {
        setError(requestError instanceof Error ? requestError.message : 'Unable to load profile.')
      }
    }

    void loadProfile()
  }, [])

  const saveProfile = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')
    setMessage('')
    try {
      const payload = await apiRequest<Profile>('/api/account/me', {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify({ full_name: fullName }),
      })
      setProfile(payload)
      setMessage('Profile updated.')
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Unable to update profile.')
    }
  }

  return (
    <section className="card-grid">
      <Card title="Profile overview">
        {error && <p className="error-text">{error}</p>}
        {!profile && !error && <p className="muted">Loading profile…</p>}
        {profile && (
          <form className="stack-sm" onSubmit={saveProfile}>
            <p className="muted">Email: {profile.email}</p>
            <input aria-label="Full name" className="text-input" value={fullName} onChange={(event) => setFullName(event.target.value)} />
            <Button type="submit">Save profile</Button>
            {message && <p className="muted">{message}</p>}
          </form>
        )}
      </Card>
      <Card title="Learning and portfolio activity">
        <ul className="feature-list">
          <li>Saved portfolios: {profile?.saved_portfolios ?? 0}</li>
          <li>Watchlists: {profile?.watchlists ?? 0}</li>
          <li>Lesson progress entries: {profile?.lesson_progress_entries ?? 0}</li>
          <li>Achievements: {profile?.achievements ?? 0}</li>
        </ul>
      </Card>
    </section>
  )
}
