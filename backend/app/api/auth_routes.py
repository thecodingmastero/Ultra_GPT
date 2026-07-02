from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from backend.app.core.security import hash_password, verify_password
from backend.app.extensions import db
from backend.app.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
def register():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    full_name = data.get("full_name", "").strip()
    password = data.get("password", "")

    if not email or not full_name or not password:
        return jsonify({"error": "full_name, email, and password are required."}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "A user with that email already exists."}), 409

    user = User(email=email, full_name=full_name, password_hash=hash_password(password))
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify(
        {
            "token": token,
            "user": {"id": user.id, "email": user.email, "full_name": user.full_name},
        }
    ), 201


@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    user = User.query.filter_by(email=email).first()
    if user is None or not verify_password(user.password_hash, password):
        return jsonify({"error": "Invalid email or password."}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify(
        {
            "token": token,
            "user": {"id": user.id, "email": user.email, "full_name": user.full_name},
        }
    )


@auth_bp.post("/logout")
def logout():
    return jsonify({"logged_out": True})
