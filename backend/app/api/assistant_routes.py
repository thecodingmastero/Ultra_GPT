from flask import Blueprint, jsonify, request

from backend.app.core.dependencies import get_assistant_service, get_behavioral_signal_service

assistant_bp = Blueprint("assistant", __name__, url_prefix="/api/assistant")


@assistant_bp.post("/chat")
def chat():
    data = request.get_json() or {}
    message = data.get("message", "").strip()
    history = data.get("history", [])
    depth = data.get("depth", "simple")

    if not message:
        return jsonify({"error": "A message is required."}), 400
    if depth not in ("simple", "deep"):
        return jsonify({"error": "depth must be 'simple' or 'deep'."}), 400
    if not isinstance(history, list):
        return jsonify({"error": "history must be a list."}), 400

    result = get_assistant_service().chat(message=message, history=history, depth=depth)
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
    depth = data.get("depth", "simple")

    if not message:
        return jsonify({"error": "A message is required."}), 400
    if depth not in ("simple", "deep"):
        return jsonify({"error": "depth must be 'simple' or 'deep'."}), 400
    if not isinstance(history, list):
        return jsonify({"error": "history must be a list."}), 400

    result = get_assistant_service().chat(message=message, history=history, depth=depth)
    return jsonify(result)


@assistant_bp.post("/behavioral/analyze")
def behavioral_analyze():
    """Standalone behavioral coaching analysis endpoint.

    Accepts free-text input and returns detected investor behavioral signals
    with confidence scores and educational coaching guidance.

    Request body:
        message (str, required): The user text to analyze.

    Response:
        signals (list): Detected signals, each with:
            - signal (str): signal name
            - confidence (float): 0.0–1.0 confidence score
            - coaching (str): educational coaching guidance
        signal_names (list[str]): Signal names only (convenience field).
        analyzed (bool): Whether any signals were detected.
    """
    data = request.get_json() or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"error": "A message is required."}), 400

    service = get_behavioral_signal_service()
    signals = service.analyze(message)

    return jsonify(
        {
            "signals": [
                {
                    "signal": s.signal,
                    "confidence": s.confidence,
                    "coaching": s.coaching,
                }
                for s in signals
            ],
            "signal_names": [s.signal for s in signals],
            "analyzed": len(signals) > 0,
        }
    )
