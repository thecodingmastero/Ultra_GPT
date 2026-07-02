from flask import Blueprint, jsonify, request

from backend.app.core.auth import auth_required, get_current_user_id
from backend.app.core.entitlements import Feature, _PLAN_FEATURES, get_user_plan_id
from backend.app.extensions import db
from backend.app.models import User

account_bp = Blueprint("account", __name__, url_prefix="/api/account")


def _serialize_account(user: User) -> dict:
    watchlist_item_count = len(user.watchlist_items)
    watchlist_count = len(user.watchlists)
    if watchlist_count == 0 and watchlist_item_count > 0:
        watchlist_count = 1
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "saved_portfolios": len(user.portfolios),
        "watchlists": watchlist_count,
        "watchlist_items": watchlist_item_count,
        "lesson_progress_entries": len(user.lesson_progress),
        "achievements": len(user.quest_profile.badges) if user.quest_profile else 0,
    }


@account_bp.get("/me")
@auth_required
def me():
    user = db.session.get(User, get_current_user_id())
    if user is None:
        return jsonify({"error": "User not found."}), 404

    return jsonify(_serialize_account(user))


@account_bp.put("/me")
@auth_required
def update_me():
    user = db.session.get(User, get_current_user_id())
    if user is None:
        return jsonify({"error": "User not found."}), 404

    data = request.get_json() or {}
    full_name = str(data.get("full_name", user.full_name)).strip()
    if not full_name:
        return jsonify({"error": "full_name is required."}), 400

    user.full_name = full_name
    db.session.commit()

    return jsonify(_serialize_account(user))


@account_bp.get("/plan")
@auth_required
def get_plan():
    """Return the authenticated user's active subscription plan and feature entitlements."""
    user_id = get_current_user_id()
    plan_id = get_user_plan_id(user_id)
    features = [f.value for f in _PLAN_FEATURES.get(plan_id, set())]
    return jsonify({
        "plan_id": plan_id,
        "features": sorted(features),
    })
