from flask import Blueprint, jsonify, request

from backend.app.core.dependencies import get_assistant_service

assistant_bp = Blueprint("assistant", __name__, url_prefix="/api/assistant")


def _run_chat(message: str, history: list) -> tuple[dict, int]:
    result = get_assistant_service().chat(message=message, history=history)
    return result, 200


@assistant_bp.post("/chat")
def chat():
    data = request.get_json() or {}
    message = data.get("message", "").strip()
    history = data.get("history", [])

    if not message:
        return jsonify({"error": "A message is required."}), 400

    result = get_assistant_service().chat(message=message, history=history)
    return jsonify(result)


@assistant_bp.post("/query")
def query():
    """Phase 2A alias for /chat that accepts the same payload.

    Kept as a separate route so external integrations can use the canonical
    /api/ai/assistant/query path described in the Phase 2A spec while the
    legacy /api/assistant/chat path continues to work.
    """
    data = request.get_json() or {}
    message = data.get("message", "").strip()
    history = data.get("history", [])

    if not message:
        return jsonify({"error": "A message is required."}), 400

    result = get_assistant_service().chat(message=message, history=history)
    return jsonify(result)
