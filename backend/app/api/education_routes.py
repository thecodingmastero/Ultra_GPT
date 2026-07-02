from flask import Blueprint, jsonify, request

from backend.app.core.auth import auth_required, get_current_user_id
from backend.app.core.dependencies import get_lessons_repository

education_bp = Blueprint("education", __name__, url_prefix="/api/education")


@education_bp.get("/lessons")
def list_lessons():
    lessons = get_lessons_repository().list_lessons()
    return jsonify(
        {
            "lessons": [
                {
                    "id": lesson.id,
                    "slug": lesson.slug,
                    "title": lesson.title,
                    "topic": lesson.topic,
                    "summary": lesson.summary,
                }
                for lesson in lessons
            ]
        }
    )


@education_bp.post("/progress")
@auth_required
def record_progress():
    """Record lesson progress for the authenticated user.

    Persists completion state via the LessonsRepository so progress
    survives across sessions. Requires authentication.
    """
    data = request.get_json() or {}
    lesson_id = data.get("lesson_id")
    completed = bool(data.get("completed", True))

    if not lesson_id:
        return jsonify({"error": "lesson_id is required."}), 400

    try:
        lesson_id_int = int(lesson_id)
    except (TypeError, ValueError):
        return jsonify({"error": "lesson_id must be an integer."}), 400

    repository = get_lessons_repository()
    lesson = repository.get_lesson(lesson_id_int)
    if lesson is None:
        return jsonify({"error": "Lesson not found."}), 404

    progress = repository.upsert_progress(
        user_id=get_current_user_id(),
        lesson_id=lesson_id_int,
        completed=completed,
    )

    return jsonify(
        {
            "lesson_id": progress.lesson_id,
            "completed": progress.completed,
            "completed_at": progress.completed_at.isoformat() if progress.completed_at else None,
            "message": "Progress recorded.",
        }
    )
