from flask import Blueprint, jsonify, request

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
def record_progress():
    """Generic progress stub — phase 2B will wire full lesson-progress logic."""
    data = request.get_json() or {}
    lesson_id = data.get("lesson_id")
    completed = bool(data.get("completed", True))

    if not lesson_id:
        return jsonify({"error": "lesson_id is required."}), 400

    return jsonify(
        {
            "lesson_id": lesson_id,
            "completed": completed,
            "message": "Progress recorded.",
        }
    )
