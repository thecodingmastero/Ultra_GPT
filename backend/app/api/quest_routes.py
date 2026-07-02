from flask import Blueprint, jsonify, request

from backend.app.core.auth import auth_required, get_current_user_id
from backend.app.extensions import db
from backend.app.models.quest import Badge, ChallengeProgress, QuestProfile

quest_bp = Blueprint("quest", __name__, url_prefix="/api/quest")

_XP_PER_LEVEL = 100


def _serialize_profile(profile: QuestProfile) -> dict:
    return {
        "user_id": profile.user_id,
        "level": profile.level,
        "xp": profile.xp,
        "xp_to_next_level": _XP_PER_LEVEL - (profile.xp % _XP_PER_LEVEL),
        "badges": [
            {"id": b.id, "name": b.name, "description": b.description}
            for b in profile.badges
        ],
    }


@quest_bp.get("/profile")
@auth_required
def get_quest_profile():
    user_id = get_current_user_id()
    profile = db.session.query(QuestProfile).filter_by(user_id=user_id).first()

    if profile is None:
        profile = QuestProfile(user_id=user_id)
        db.session.add(profile)
        db.session.commit()

    return jsonify(_serialize_profile(profile))


@quest_bp.post("/challenge/submit")
@auth_required
def submit_challenge():
    user_id = get_current_user_id()
    data = request.get_json() or {}
    challenge_id = str(data.get("challenge_id", "")).strip()

    if not challenge_id:
        return jsonify({"error": "challenge_id is required."}), 400

    profile = db.session.query(QuestProfile).filter_by(user_id=user_id).first()
    if profile is None:
        profile = QuestProfile(user_id=user_id)
        db.session.add(profile)
        db.session.flush()

    existing = (
        db.session.query(ChallengeProgress)
        .filter_by(quest_profile_id=profile.id, challenge_id=challenge_id)
        .first()
    )
    if existing and existing.completed:
        return jsonify(
            {
                "message": "Challenge already completed.",
                "xp_awarded": 0,
                "profile": _serialize_profile(profile),
            }
        )

    xp_reward = int(data.get("xp_reward", 10))
    from datetime import UTC, datetime

    cp = existing or ChallengeProgress(quest_profile_id=profile.id, challenge_id=challenge_id)
    cp.completed = True
    cp.xp_awarded = xp_reward
    cp.completed_at = datetime.now(UTC)
    db.session.add(cp)

    profile.xp += xp_reward
    profile.level = 1 + (profile.xp // _XP_PER_LEVEL)

    db.session.commit()

    return jsonify(
        {
            "message": "Challenge submitted successfully.",
            "xp_awarded": xp_reward,
            "profile": _serialize_profile(profile),
        }
    )
