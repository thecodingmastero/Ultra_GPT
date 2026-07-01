import { useState } from 'react'
import type { FormEvent } from 'react'
import { Button } from '../components/common/Button'
import { Card } from '../components/common/Card'
import { apiRequest } from '../services/http'

type AuthResponse = {
  token: string
  user: {
    full_name: string
    email: string
  }
}

export function RegisterPage() {
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    try {
      const payload = await apiRequest<AuthResponse>('/api/auth/register', {
        method: 'POST',
        body: JSON.stringify({ full_name: fullName, email, password }),
      })
      localStorage.setItem('better-investor-token', payload.token)
      setMessage(`Account created for ${payload.user.full_name}.`)
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Registration failed.')
    }
  }

  return (
    <Card title="Create an account" subtitle="Save portfolio drafts and continue your learning journey.">
      <form className="stack-sm" onSubmit={submit}>
        <input className="text-input" placeholder="Full name" value={fullName} onChange={(event) => setFullName(event.target.value)} />
        <input className="text-input" placeholder="Email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} />
        <input className="text-input" placeholder="Password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
        <Button type="submit">Register</Button>
        {message && <p className="muted">{message}</p>}
      </form>
    </Card>
  )
}
