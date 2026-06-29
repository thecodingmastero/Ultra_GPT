from flask import Blueprint, jsonify, request

from backend.app.core.dependencies import get_market_data_service
from backend.app.services.market_data.base import MarketDataProviderError

market_bp = Blueprint("market", __name__, url_prefix="/api/market")


@market_bp.get("/quote")
def get_quote():
    symbol = request.args.get("symbol", "").strip().upper()
    if not symbol:
        return jsonify({"error": "A symbol query parameter is required."}), 400

    try:
        quote = get_market_data_service().get_quote(symbol)
    except MarketDataProviderError as exc:
        return jsonify({"error": str(exc)}), 502

    return jsonify(quote)
