from flask import Blueprint, current_app, jsonify, request

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
        current_app.logger.warning("Market quote lookup failed for %s: %s", symbol, exc)
        return jsonify({"error": "Unable to fetch quote data right now. Check the symbol or market data configuration."}), 502

    return jsonify(quote)
