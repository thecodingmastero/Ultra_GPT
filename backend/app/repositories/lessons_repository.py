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
        "slug": "stocks-101",
        "title": "Stocks 101",
        "topic": "Stocks",
        "summary": "Understand what a stock represents and what drives stock returns.",
        "content": "Stocks represent ownership in businesses. Returns come from earnings growth, valuation, and time in the market.",
    },
    {
        "slug": "etfs-101",
        "title": "ETFs 101",
        "topic": "ETFs",
        "summary": "Learn how exchange-traded funds simplify diversification.",
        "content": "ETFs bundle many securities into one tradeable fund and can help reduce single-company risk.",
    },
    {
        "slug": "index-funds",
        "title": "Index Funds",
        "topic": "Index Funds",
        "summary": "Why passive index strategies are common long-term building blocks.",
        "content": "Index funds aim to track a broad market benchmark with low cost and broad diversification.",
    },
    {
        "slug": "bonds-basics",
        "title": "Bonds Basics",
        "topic": "Bonds",
        "summary": "How bonds can support portfolio stability and income goals.",
        "content": "Bonds are debt securities that can reduce portfolio volatility and provide income depending on duration and credit quality.",
    },
    {
        "slug": "diversification",
        "title": "Diversification",
        "topic": "Diversification",
        "summary": "Why spreading risk across holdings matters.",
        "content": "Diversification can reduce concentration risk by spreading exposure across companies, sectors, and asset types.",
    },
    {
        "slug": "risk-management",
        "title": "Risk Management",
        "topic": "Risk Management",
        "summary": "Build habits that help limit avoidable losses.",
        "content": "Risk management starts with position sizing, diversification, emergency reserves, and scenario planning.",
    },
    {
        "slug": "compound-growth",
        "title": "Compound Growth",
        "topic": "Compound Growth",
        "summary": "See how reinvestment and time can accelerate results.",
        "content": "Compounding works best with consistent contributions, reinvested returns, and a long-term time horizon.",
    },
    {
        "slug": "dollar-cost-averaging",
        "title": "Dollar-Cost Averaging",
        "topic": "Dollar-Cost Averaging",
        "summary": "Investing on a schedule to reduce timing pressure.",
        "content": "Dollar-cost averaging spreads purchases over time, reducing the emotional pressure of trying to time market highs and lows.",
    },
    {
        "slug": "behavioral-finance",
        "title": "Behavioral Finance",
        "topic": "Behavioral Finance",
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

    def list_progress_for_user(self, user_id: int) -> list[LessonProgress]:
        return LessonProgress.query.filter_by(user_id=user_id).order_by(LessonProgress.lesson_id.asc()).all()
