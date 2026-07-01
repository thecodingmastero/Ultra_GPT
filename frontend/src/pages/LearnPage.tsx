import { useEffect, useState } from 'react'

import { Card } from '../components/common/Card'
import { apiRequest } from '../services/http'

type Lesson = {
  id: number
  title: string
  topic: string
  summary: string
}

export function LearnPage() {
  const [lessons, setLessons] = useState<Lesson[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    const loadLessons = async () => {
      try {
        const payload = await apiRequest<{ lessons: Lesson[] }>('/api/lessons')
        setLessons(payload.lessons)
      } catch (requestError) {
        setError(requestError instanceof Error ? requestError.message : 'Unable to load lessons.')
      }
    }

    void loadLessons()
  }, [])

  if (error) {
    return (
      <section className="card-grid">
        <Card title="Educational Hub">
          <p className="error-text">{error}</p>
        </Card>
      </section>
    )
  }

  return (
    <section className="card-grid">
      {lessons.map((lesson) => (
        <Card key={lesson.id} title={lesson.title} subtitle={lesson.topic}>
          <p>{lesson.summary}</p>
        </Card>
      ))}
    </section>
  )
}
