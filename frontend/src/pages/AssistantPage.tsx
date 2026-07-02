import { useState } from 'react'
import type { FormEvent } from 'react'
import { BehavioralCoachingSection } from '../components/common/BehavioralCoachingCard'
import { Button } from '../components/common/Button'
import { Card } from '../components/common/Card'
import { DisclaimerBanner } from '../components/common/DisclaimerBanner'
import { apiRequest } from '../services/http'

type Depth = 'simple' | 'deep'

type CoachingEntry = {
  signal: string
  confidence: number
  coaching: string
}

type ChatMessage = {
  role: 'user' | 'assistant'
  content: string
  coaching?: CoachingEntry[]
}

type ChatResponse = {
  response: string
  disclaimer: string
  behavioral_signals: string[]
  behavioral_coaching: CoachingEntry[]
  policy_metadata: {
    blocked: boolean
    depth: string
    disclaimer_appended: boolean
    block_reason: string | null
    flags: string[]
  }
}

const DEPTH_LABELS: Record<Depth, string> = {
  simple: 'Simple',
  deep: 'Deep Dive',
}

export function AssistantPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [draft, setDraft] = useState('')
  const [depth, setDepth] = useState<Depth>('simple')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!draft.trim()) {
      return
    }

    const nextMessages: ChatMessage[] = [
      ...messages,
      { role: 'user' as const, content: draft.trim() },
    ]
    setMessages(nextMessages)
    setDraft('')
    setError('')
    setLoading(true)

    try {
      const payload = await apiRequest<ChatResponse>('/api/assistant/chat', {
        method: 'POST',
        body: JSON.stringify({ message: draft.trim(), history: messages.map(({ role, content }) => ({ role, content })), depth }),
      })
      setMessages([
        ...nextMessages,
        {
          role: 'assistant',
          content: payload.response,
          coaching: payload.behavioral_coaching,
        },
      ])
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Unable to reach the assistant right now.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-stack">
      <DisclaimerBanner />

      <Card title="AI Investment Assistant" subtitle="Ask about concepts, portfolio trade-offs, and investing habits.">
        <div className="depth-toggle" role="group" aria-label="Explanation depth">
          <span className="depth-toggle__label">Explanation depth:</span>
          {(['simple', 'deep'] as Depth[]).map((d) => (
            <button
              key={d}
              type="button"
              className={`depth-toggle__btn${depth === d ? ' depth-toggle__btn--active' : ''}`}
              onClick={() => setDepth(d)}
              aria-pressed={depth === d}
            >
              {DEPTH_LABELS[d]}
            </button>
          ))}
        </div>

        <div className="chat-window">
          {messages.length === 0 && (
            <p className="muted">
              Try asking about diversification, ETFs, or how to think through a stock idea.
              Choose <strong>Simple</strong> for a plain-language answer or{' '}
              <strong>Deep Dive</strong> for detailed mechanics and academic context.
            </p>
          )}
          {messages.map((message, index) => (
            <div key={`${message.role}-${index}`}>
              <article className={`chat-bubble chat-bubble--${message.role}`}>
                <strong>{message.role === 'user' ? 'You' : 'Coach'}</strong>
                <p>{message.content}</p>
              </article>
              {message.role === 'assistant' && message.coaching && message.coaching.length > 0 && (
                <BehavioralCoachingSection coaching={message.coaching} />
              )}
            </div>
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
            {loading ? 'Thinking\u2026' : 'Send'}
          </Button>
        </form>
      </Card>
    </div>
  )
}
