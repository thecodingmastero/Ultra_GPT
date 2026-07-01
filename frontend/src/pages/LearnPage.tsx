import { useEffect, useMemo, useState } from 'react'
import { Button } from '../components/common/Button'
import { Card } from '../components/common/Card'
import { getAuthHeaders, isAuthenticated } from '../services/auth'
import { apiRequest } from '../services/http'

type Lesson = {
  id: number
  title: string
  topic: string
  summary: string
}

type LessonProgress = {
  lesson_id: number
  completed: boolean
}

export function LearnPage() {
  const [lessons, setLessons] = useState<Lesson[]>([])
  const [completedLessonIds, setCompletedLessonIds] = useState<number[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    const loadLessons = async () => {
      try {
        const payload = await apiRequest<{ lessons: Lesson[] }>('/api/lessons')
        setLessons(payload.lessons)
        if (isAuthenticated()) {
          const progressPayload = await apiRequest<{ progress: LessonProgress[]; completed_lesson_ids: number[] }>('/api/lessons/progress', {
            headers: getAuthHeaders(),
          })
          setCompletedLessonIds(progressPayload.completed_lesson_ids)
        }
      } catch (requestError) {
        setError(requestError instanceof Error ? requestError.message : 'Unable to load lessons.')
      }
    }

    void loadLessons()
  }, [])

  const completedCount = useMemo(() => completedLessonIds.length, [completedLessonIds])

  const markComplete = async (lessonId: number) => {
    setError('')
    try {
      await apiRequest(`/api/lessons/${lessonId}/progress`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ completed: true }),
      })
      if (!completedLessonIds.includes(lessonId)) {
        setCompletedLessonIds([...completedLessonIds, lessonId])
      }
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Unable to save lesson progress.')
    }
  }

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
    <section className="page-stack">
      {isAuthenticated() && (
        <Card title="Progress">
          <p>
            Completed lessons: <strong>{completedCount}</strong> / {lessons.length}
          </p>
        </Card>
      )}
      <section className="card-grid">
        {lessons.map((lesson) => {
          const completed = completedLessonIds.includes(lesson.id)
          return (
            <Card key={lesson.id} title={lesson.title} subtitle={lesson.topic}>
              <p>{lesson.summary}</p>
              {isAuthenticated() && (
                <Button variant="secondary" disabled={completed} onClick={() => markComplete(lesson.id)}>
                  {completed ? 'Completed' : 'Mark complete'}
                </Button>
              )}
            </Card>
          )
        })}
      </section>
    </section>
  )
}
