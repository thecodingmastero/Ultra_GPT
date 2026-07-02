from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.extensions import db


class QuestProfile(db.Model):
    """Tracks a user's overall gamified Investor Quest progress."""

    __tablename__ = "quest_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    user = relationship("User", back_populates="quest_profile")
    badges = relationship("Badge", back_populates="quest_profile", cascade="all, delete-orphan")
    challenge_progress = relationship("ChallengeProgress", back_populates="quest_profile", cascade="all, delete-orphan")


class Badge(db.Model):
    """An award earned by a user within Investor Quest."""

    __tablename__ = "badges"

    id: Mapped[int] = mapped_column(primary_key=True)
    quest_profile_id: Mapped[int] = mapped_column(ForeignKey("quest_profiles.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    earned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    quest_profile = relationship("QuestProfile", back_populates="badges")


class ChallengeProgress(db.Model):
    """Tracks a user's attempt at a specific Investor Quest challenge."""

    __tablename__ = "challenge_progress"

    id: Mapped[int] = mapped_column(primary_key=True)
    quest_profile_id: Mapped[int] = mapped_column(ForeignKey("quest_profiles.id"), nullable=False)
    challenge_id: Mapped[str] = mapped_column(String(80), nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    xp_awarded: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    quest_profile = relationship("QuestProfile", back_populates="challenge_progress")
