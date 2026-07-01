from flask import Blueprint, current_app, jsonify, request

from backend.app.core.auth import auth_required, get_current_user_id
from backend.app.core.dependencies import get_holdings_repository, get_portfolio_analyzer
from backend.app.services.market_data.base import MarketDataProviderError

portfolio_bp = Blueprint("portfolio", __name__, url_prefix="/api")


def _serialize_holding(holding):
    return {
        "id": holding.id,
        "symbol": holding.symbol,
        "quantity": holding.quantity,
        "portfolio_id": holding.portfolio_id,
    }


@portfolio_bp.post("/portfolio/analyze")
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


@portfolio_bp.get("/portfolio/concentration")
@auth_required
def concentration_analysis():
    user_id = get_current_user_id()
    holdings = get_holdings_repository().list_for_user(user_id)
    if not holdings:
        return jsonify({"error": "No holdings found for concentration analysis."}), 404

    holding_input = [{"symbol": item.symbol, "quantity": item.quantity} for item in holdings]

    try:
        analysis = get_portfolio_analyzer().analyze(holding_input)
    except MarketDataProviderError as exc:
        current_app.logger.warning("Concentration analysis market data failure: %s", exc)
        return jsonify({"error": "Concentration analysis is temporarily unavailable."}), 502

    return jsonify(
        {
            "summary": analysis["summary"],
            "risk_flags": analysis["risk_flags"],
            "top_positions": analysis["positions"][:3],
            "educational_feedback": analysis["educational_feedback"],
        }
    )


@portfolio_bp.get("/holdings")
@auth_required
def list_holdings():
    user_id = get_current_user_id()
    holdings = get_holdings_repository().list_for_user(user_id)
    return jsonify({"holdings": [_serialize_holding(item) for item in holdings]})


@portfolio_bp.post("/holdings")
@auth_required
def create_holding():
    data = request.get_json() or {}
    symbol = str(data.get("symbol", "")).strip().upper()
    quantity = data.get("quantity")

    try:
        quantity_value = float(quantity)
    except (TypeError, ValueError):
        return jsonify({"error": "quantity must be a number greater than zero."}), 400

    if not symbol or quantity_value <= 0:
        return jsonify({"error": "symbol and quantity greater than zero are required."}), 400

    holding = get_holdings_repository().create_for_user(get_current_user_id(), symbol, quantity_value)
    return jsonify(_serialize_holding(holding)), 201


@portfolio_bp.put("/holdings/<int:holding_id>")
@auth_required
def update_holding(holding_id: int):
    repo = get_holdings_repository()
    holding = repo.get_for_user(get_current_user_id(), holding_id)
    if holding is None:
        return jsonify({"error": "Holding not found."}), 404

    data = request.get_json() or {}
    symbol = str(data.get("symbol", holding.symbol)).strip().upper()
    quantity = data.get("quantity", holding.quantity)

    try:
        quantity_value = float(quantity)
    except (TypeError, ValueError):
        return jsonify({"error": "quantity must be a number greater than zero."}), 400

    if not symbol or quantity_value <= 0:
        return jsonify({"error": "symbol and quantity greater than zero are required."}), 400

    updated = repo.update(holding, symbol=symbol, quantity=quantity_value)
    return jsonify(_serialize_holding(updated))


@portfolio_bp.delete("/holdings/<int:holding_id>")
@auth_required
def delete_holding(holding_id: int):
    repo = get_holdings_repository()
    holding = repo.get_for_user(get_current_user_id(), holding_id)
    if holding is None:
        return jsonify({"error": "Holding not found."}), 404

    repo.delete(holding)
    return jsonify({"deleted": True})
