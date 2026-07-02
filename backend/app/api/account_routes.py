from flask import Blueprint, jsonify, request

from backend.app.core.auth import auth_required, get_current_user_id
from backend.app.extensions import db
from backend.app.models import User

account_bp = Blueprint("account", __name__, url_prefix="/api/account")


@account_bp.get("/me")
@auth_required
def me():
    user = db.session.get(User, get_current_user_id())
    if user is None:
        return jsonify({"error": "User not found."}), 404

    return jsonify(
        {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "saved_portfolios": len(user.portfolios),
            "watchlists": len(user.watchlists),
            "lesson_progress_entries": len(user.lesson_progress),
        }
    )


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

    return jsonify(
        {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "saved_portfolios": len(user.portfolios),
            "watchlists": len(user.watchlists),
            "lesson_progress_entries": len(user.lesson_progress),
        }
    )
