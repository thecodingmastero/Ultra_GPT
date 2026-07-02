from flask import Blueprint, current_app, jsonify, request

from backend.app.core.dependencies import get_market_data_service
from backend.app.services.market_data.base import MarketDataProviderError

market_bp = Blueprint("market", __name__, url_prefix="/api/market")

_DISCLAIMER = (
    "The Better Investor is for educational purposes only and "
    "does not provide personalized financial advice."
)


def _format_market_error_message(exc: MarketDataProviderError) -> str:
    lowered = str(exc).lower()
    if "api key" in lowered or "configured" in lowered:
        return "Market data is unavailable because FINNHUB_API_KEY is not configured."
    if "rate limit" in lowered:
        return "Market data is temporarily rate limited. Please retry shortly."
    return "Unable to fetch market data right now. Check the symbol or market data configuration."


@market_bp.get("/quote")
def get_quote():
    symbol = request.args.get("symbol", "").strip().upper()
    if not symbol:
        return jsonify({"error": "A symbol query parameter is required."}), 400

    try:
        quote = get_market_data_service().get_quote(symbol)
    except MarketDataProviderError as exc:
        current_app.logger.warning("Market quote lookup failed for %s: %s", symbol, exc)
        return jsonify({"error": _format_market_error_message(exc)}), 502

    return jsonify(quote)


@market_bp.get("/quote/<string:ticker>")
def get_quote_by_ticker(ticker: str):
    """Path-param variant of the quote endpoint: GET /api/market/quote/:ticker"""
    symbol = ticker.strip().upper()
    if not symbol:
        return jsonify({"error": "A ticker path parameter is required."}), 400

    try:
        quote = get_market_data_service().get_quote(symbol)
    except MarketDataProviderError as exc:
        current_app.logger.warning("Market quote lookup failed for %s: %s", symbol, exc)
        return jsonify({"error": _format_market_error_message(exc)}), 502

    return jsonify(quote)


@market_bp.get("/chart/<string:ticker>")
def get_chart(ticker: str):
    """OHLCV candle chart data for a symbol.

    Optional query params:
    - resolution: D (daily, default), W (weekly), M (monthly)
    - count: number of candles to return (default 30, max 365)
    """
    symbol = ticker.strip().upper()
    if not symbol:
        return jsonify({"error": "A ticker path parameter is required."}), 400

    resolution = request.args.get("resolution", "D").upper()
    if resolution not in ("D", "W", "M"):
        resolution = "D"
    try:
        count = max(1, min(365, int(request.args.get("count", 30))))
    except (TypeError, ValueError):
        count = 30

    try:
        chart = get_market_data_service().get_chart(symbol, resolution=resolution, count=count)
    except MarketDataProviderError as exc:
        current_app.logger.warning("Chart lookup failed for %s: %s", symbol, exc)
        return jsonify({"error": _format_market_error_message(exc)}), 502

    return jsonify({
        **chart,
        "disclaimer": _DISCLAIMER,
    })


@market_bp.get("/profile")
def get_profile():
    symbol = request.args.get("symbol", "").strip().upper()
    if not symbol:
        return jsonify({"error": "A symbol query parameter is required."}), 400

    try:
        profile = get_market_data_service().get_company_profile(symbol)
    except MarketDataProviderError as exc:
        current_app.logger.warning("Company profile lookup failed for %s: %s", symbol, exc)
        return jsonify({"error": _format_market_error_message(exc)}), 502

    return jsonify(profile)
