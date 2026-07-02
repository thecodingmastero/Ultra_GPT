from flask import Blueprint, current_app, jsonify, request

from backend.app.core.dependencies import get_market_data_service
from backend.app.services.market_data.base import MarketDataProviderError

market_bp = Blueprint("market", __name__, url_prefix="/api/market")


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
    """Stub chart endpoint — full OHLCV data integration deferred to Phase 2B.

    Returns a placeholder response so the frontend can wire up the route now
    and replace the stub payload once the data provider supports candlestick
    chart data.
    """
    symbol = ticker.strip().upper()
    if not symbol:
        return jsonify({"error": "A ticker path parameter is required."}), 400

    return jsonify(
        {
            "symbol": symbol,
            "chart_data": [],
            "message": "Chart data integration is planned for Phase 2B.",
            "disclaimer": (
                "The Better Investor is for educational purposes only and "
                "does not provide personalized financial advice."
            ),
        }
    )


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
