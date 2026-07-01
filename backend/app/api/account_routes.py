from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from backend.app.extensions import db
from backend.app.models import User

account_bp = Blueprint("account", __name__, url_prefix="/api/account")


@account_bp.get("/me")
@jwt_required()
def me():
    user = db.session.get(User, int(get_jwt_identity()))
    if user is None:
        return jsonify({"error": "User not found."}), 404

    return jsonify(
        {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "saved_portfolios": len(user.portfolios),
            "watchlists": len(user.watchlists),
        }
    )
