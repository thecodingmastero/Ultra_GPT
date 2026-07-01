from flask import Blueprint, current_app, jsonify, request

from backend.app.core.dependencies import get_portfolio_analyzer
from backend.app.services.market_data.base import MarketDataProviderError

portfolio_bp = Blueprint("portfolio", __name__, url_prefix="/api/portfolio")


@portfolio_bp.post("/analyze")
def analyze_portfolio():
    data = request.get_json() or {}
    holdings = data.get("holdings", [])

    try:
        analysis = get_portfolio_analyzer().analyze(holdings)
    except ValueError as exc:
        current_app.logger.info("Portfolio analysis validation failed: %s", exc)
        return jsonify({"error": "Invalid portfolio input. Provide at least one symbol and a quantity greater than zero."}), 400
    except MarketDataProviderError as exc:
        current_app.logger.warning("Portfolio analysis market data failure: %s", exc)
        return jsonify({"error": "Portfolio analysis is temporarily unavailable because market data could not be fetched."}), 502

    return jsonify(analysis)
