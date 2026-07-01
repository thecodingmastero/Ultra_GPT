from __future__ import annotations

from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required


def auth_required(fn):
    @jwt_required()
    @wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    return wrapper


def get_current_user_id() -> int:
    identity = get_jwt_identity()
    if identity is None:
        raise ValueError("Missing JWT identity")
    return int(identity)


def auth_error_response(message: str = "Authentication is required."):
    return jsonify({"error": message}), 401
