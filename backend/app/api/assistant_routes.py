from flask import Blueprint, current_app, jsonify, request

from backend.app.core.dependencies import get_assistant_service

assistant_bp = Blueprint("assistant", __name__, url_prefix="/api/assistant")


@assistant_bp.post("/chat")
def chat():
    data = request.get_json() or {}
    message = data.get("message", "").strip()
    history = data.get("history", [])

    if not message:
        return jsonify({"error": "A message is required."}), 400

    result = get_assistant_service().chat(message=message, history=history)
    current_app.logger.info(
        "assistant.chat blocked=%s signals=%s message_len=%d",
        result.get("behavioral_signals") != [] or "can\u2019t provide" in result.get("response", ""),
        result.get("behavioral_signals", []),
        len(message),
    )
    return jsonify(result)


@assistant_bp.post("/query")
def query():
    """Phase 2A/3 alias for /chat that accepts the same payload."""
    data = request.get_json() or {}
    message = data.get("message", "").strip()
    history = data.get("history", [])

    if not message:
        return jsonify({"error": "A message is required."}), 400

    result = get_assistant_service().chat(message=message, history=history)
    current_app.logger.info(
        "assistant.query blocked=%s signals=%s message_len=%d",
        result.get("behavioral_signals") != [] or "can\u2019t provide" in result.get("response", ""),
        result.get("behavioral_signals", []),
        len(message),
    )
    return jsonify(result)
