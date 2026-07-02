from flask import Blueprint, jsonify, request

from backend.app.core.auth import auth_required, get_current_user_id
from backend.app.extensions import db
from backend.app.models.watchlist_item import WatchlistItem

watchlist_bp = Blueprint("watchlist", __name__, url_prefix="/api/watchlist")


def _serialize(item: WatchlistItem) -> dict:
    return {
        "id": item.id,
        "symbol": item.symbol,
        "added_at": item.added_at.isoformat(),
    }


@watchlist_bp.get("/items")
@auth_required
def list_watchlist_items():
    user_id = get_current_user_id()
    items = WatchlistItem.query.filter_by(user_id=user_id).order_by(WatchlistItem.added_at.desc()).all()
    return jsonify({"items": [_serialize(item) for item in items]})


@watchlist_bp.post("/items")
@auth_required
def add_watchlist_item():
    symbol = str((request.get_json() or {}).get("symbol", "")).strip().upper()
    if not symbol:
        return jsonify({"error": "symbol is required."}), 400

    existing = WatchlistItem.query.filter_by(user_id=get_current_user_id(), symbol=symbol).first()
    if existing is not None:
        return jsonify({**_serialize(existing), "created": False})

    item = WatchlistItem(user_id=get_current_user_id(), symbol=symbol)
    db.session.add(item)
    db.session.commit()
    return jsonify({**_serialize(item), "created": True}), 201


@watchlist_bp.delete("/items/<int:item_id>")
@auth_required
def delete_watchlist_item(item_id: int):
    item = WatchlistItem.query.filter_by(id=item_id, user_id=get_current_user_id()).first()
    if item is None:
        return jsonify({"error": "Watchlist item not found."}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({"deleted": True})
