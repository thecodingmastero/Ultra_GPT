from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.extensions import db


class Lesson(db.Model):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    topic: Mapped[str] = mapped_column(String(80), nullable=False)
    summary: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    progress_entries = relationship("LessonProgress", back_populates="lesson", cascade="all, delete-orphan")
