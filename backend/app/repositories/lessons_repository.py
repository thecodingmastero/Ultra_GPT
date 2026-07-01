from __future__ import annotations

from datetime import UTC, datetime

from backend.app.extensions import db
from backend.app.models import Lesson, LessonProgress

DEFAULT_LESSONS = [
    {
        "slug": "investing-basics",
        "title": "Investing Basics",
        "topic": "Foundations",
        "summary": "Learn how risk, return, and time horizon work together.",
        "content": "Investing basics starts with goals, diversification, and staying consistent over long periods.",
    },
    {
        "slug": "diversification",
        "title": "Diversification",
        "topic": "Portfolio Construction",
        "summary": "Why spreading risk across holdings matters.",
        "content": "Diversification can reduce concentration risk by spreading exposure across companies, sectors, and asset types.",
    },
    {
        "slug": "behavioral-finance",
        "title": "Behavioral Finance",
        "topic": "Psychology",
        "summary": "Recognize common investing mistakes driven by emotion.",
        "content": "FOMO, panic selling, and overconfidence can harm long-term outcomes when decisions are reactive.",
    },
]


class LessonsRepository:
    def ensure_seed_data(self) -> None:
        if Lesson.query.count() > 0:
            return
        for lesson in DEFAULT_LESSONS:
            db.session.add(Lesson(**lesson))
        db.session.commit()

    def list_lessons(self) -> list[Lesson]:
        self.ensure_seed_data()
        return Lesson.query.order_by(Lesson.id.asc()).all()

    def get_lesson(self, lesson_id: int) -> Lesson | None:
        self.ensure_seed_data()
        return db.session.get(Lesson, lesson_id)

    def upsert_progress(self, user_id: int, lesson_id: int, completed: bool) -> LessonProgress:
        progress = LessonProgress.query.filter_by(user_id=user_id, lesson_id=lesson_id).first()
        if progress is None:
            progress = LessonProgress(user_id=user_id, lesson_id=lesson_id)
            db.session.add(progress)

        progress.completed = completed
        progress.completed_at = datetime.now(UTC) if completed else None
        db.session.commit()
        return progress
