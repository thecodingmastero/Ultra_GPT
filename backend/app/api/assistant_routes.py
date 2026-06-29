from flask import Blueprint, jsonify, request

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
    return jsonify(result)
