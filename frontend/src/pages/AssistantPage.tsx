import { useState } from 'react'
import type { FormEvent } from 'react'
import { Button } from '../components/common/Button'
import { Card } from '../components/common/Card'
import { DisclaimerBanner } from '../components/common/DisclaimerBanner'
import { apiRequest } from '../services/http'

type ChatMessage = {
  role: 'user' | 'assistant'
  content: string
}

type ChatResponse = {
  response: string
  disclaimer: string
}

export function AssistantPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [draft, setDraft] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!draft.trim()) {
      return
    }

    const nextMessages = [...messages, { role: 'user' as const, content: draft.trim() }]
    setMessages(nextMessages)
    setDraft('')
    setError('')
    setLoading(true)

    try {
      const payload = await apiRequest<ChatResponse>('/api/assistant/chat', {
        method: 'POST',
        body: JSON.stringify({ message: draft.trim(), history: messages }),
      })
      setMessages([...nextMessages, { role: 'assistant', content: payload.response }])
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Unable to reach the assistant right now.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-stack">
      <DisclaimerBanner>
        <strong>Assistant policy:</strong> education only, no guaranteed returns, no direct buy or sell directives, and every answer should reinforce diversification, risk awareness, and emotional discipline.
      </DisclaimerBanner>

      <Card title="AI Investment Assistant" subtitle="Ask about concepts, portfolio trade-offs, and investing habits.">
        <div className="chat-window">
          {messages.length === 0 && <p className="muted">Try asking about diversification, ETFs, or how to think through a stock idea without relying on direct recommendations.</p>}
          {messages.map((message, index) => (
            <article key={`${message.role}-${index}`} className={`chat-bubble chat-bubble--${message.role}`}>
              <strong>{message.role === 'user' ? 'You' : 'Coach'}</strong>
              <p>{message.content}</p>
            </article>
          ))}
        </div>

        <form className="stack-sm" onSubmit={onSubmit}>
          <label className="field-label" htmlFor="assistant-message">
            Your question
          </label>
          <textarea
            id="assistant-message"
            className="text-input"
            rows={4}
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder="What makes diversification valuable for a long-term investor?"
          />
          {error && <p className="error-text">{error}</p>}
          <Button disabled={loading} type="submit">
            {loading ? 'Thinking…' : 'Send'}
          </Button>
        </form>
      </Card>
    </div>
  )
}
