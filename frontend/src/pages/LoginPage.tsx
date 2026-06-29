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

export function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    try {
      const payload = await apiRequest<AuthResponse>('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      })
      localStorage.setItem('better-investor-token', payload.token)
      setMessage(`Welcome back, ${payload.user.full_name}.`)
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Login failed.')
    }
  }

  return (
    <Card title="Log in" subtitle="Access your learning profile and saved portfolio tools.">
      <form className="stack-sm" onSubmit={submit}>
        <input className="text-input" placeholder="Email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} />
        <input className="text-input" placeholder="Password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
        <Button type="submit">Login</Button>
        {message && <p className="muted">{message}</p>}
      </form>
    </Card>
  )
}
