from flask import Blueprint, jsonify, request

from backend.app.core.auth import auth_required, get_current_user_id
from backend.app.core.dependencies import get_lessons_repository

lessons_bp = Blueprint("lessons", __name__, url_prefix="/api/lessons")


def _serialize_lesson(lesson, include_content: bool = False) -> dict:
    payload = {
        "id": lesson.id,
        "slug": lesson.slug,
        "title": lesson.title,
        "topic": lesson.topic,
        "summary": lesson.summary,
    }
    if include_content:
        payload["content"] = lesson.content
    return payload


@lessons_bp.get("")
def list_lessons():
    lessons = get_lessons_repository().list_lessons()
    return jsonify({"lessons": [_serialize_lesson(lesson) for lesson in lessons]})


@lessons_bp.get("/<int:lesson_id>")
def get_lesson(lesson_id: int):
    lesson = get_lessons_repository().get_lesson(lesson_id)
    if lesson is None:
        return jsonify({"error": "Lesson not found."}), 404
    return jsonify(_serialize_lesson(lesson, include_content=True))


@lessons_bp.post("/<int:lesson_id>/progress")
@auth_required
def track_lesson_progress(lesson_id: int):
    repository = get_lessons_repository()
    lesson = repository.get_lesson(lesson_id)
    if lesson is None:
        return jsonify({"error": "Lesson not found."}), 404

    data = request.get_json() or {}
    completed = bool(data.get("completed", True))
    progress = repository.upsert_progress(user_id=get_current_user_id(), lesson_id=lesson_id, completed=completed)

    return jsonify(
        {
            "lesson_id": progress.lesson_id,
            "user_id": progress.user_id,
            "completed": progress.completed,
            "completed_at": progress.completed_at.isoformat() if progress.completed_at else None,
        }
    )


@lessons_bp.get("/progress")
@auth_required
def list_lesson_progress():
    progress_entries = get_lessons_repository().list_progress_for_user(get_current_user_id())
    completed_lesson_ids = [entry.lesson_id for entry in progress_entries if entry.completed]
    return jsonify(
        {
            "progress": [
                {
                    "lesson_id": entry.lesson_id,
                    "completed": entry.completed,
                    "completed_at": entry.completed_at.isoformat() if entry.completed_at else None,
                }
                for entry in progress_entries
            ],
            "completed_lesson_ids": completed_lesson_ids,
        }
    )
