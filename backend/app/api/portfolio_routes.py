from flask import Blueprint, jsonify, request

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
        return jsonify({"error": str(exc)}), 400
    except MarketDataProviderError as exc:
        return jsonify({"error": str(exc)}), 502

    return jsonify(analysis)
