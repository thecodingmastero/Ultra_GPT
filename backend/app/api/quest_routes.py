from datetime import UTC, datetime

from flask import Blueprint, jsonify, request

from backend.app.core.auth import auth_required, get_current_user_id
from backend.app.extensions import db
from backend.app.models.quest import Badge, ChallengeProgress, QuestProfile

quest_bp = Blueprint("quest", __name__, url_prefix="/api/quest")

_XP_PER_LEVEL = 100

# Badge award definitions: (min_xp_threshold, badge_name, description)
_BADGE_MILESTONES = [
    (10,  "First Steps",    "Earned your first XP in Investor Quest."),
    (50,  "Quick Learner",  "Accumulated 50 XP through quizzes and challenges."),
    (100, "Level Up",       "Reached 100 XP — you've leveled up your investing knowledge!"),
    (250, "Dedicated",      "Reached 250 XP — consistent effort leads to lasting knowledge."),
    (500, "Expert Investor","Reached 500 XP — an outstanding commitment to financial education."),
]


def _serialize_profile(profile: QuestProfile) -> dict:
    return {
        "user_id": profile.user_id,
        "level": profile.level,
        "xp": profile.xp,
        "xp_to_next_level": _XP_PER_LEVEL - (profile.xp % _XP_PER_LEVEL),
        "badges": [
            {"id": b.id, "name": b.name, "description": b.description, "earned_at": b.earned_at.isoformat()}
            for b in profile.badges
        ],
    }


def _check_and_award_badges(profile: QuestProfile) -> list[str]:
    """Award any milestone badges the user has now qualified for.

    Returns list of newly-awarded badge names (may be empty).
    """
    existing_badge_names = {b.name for b in profile.badges}
    newly_awarded: list[str] = []
    for min_xp, name, description in _BADGE_MILESTONES:
        if profile.xp >= min_xp and name not in existing_badge_names:
            badge = Badge(quest_profile_id=profile.id, name=name, description=description)
            db.session.add(badge)
            newly_awarded.append(name)
    return newly_awarded


def _get_or_create_profile(user_id: int) -> QuestProfile:
    profile = db.session.query(QuestProfile).filter_by(user_id=user_id).first()
    if profile is None:
        profile = QuestProfile(user_id=user_id)
        db.session.add(profile)
        db.session.flush()
    return profile


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
    """Submit a completed challenge and earn XP.

    Isolation rule: XP is ONLY awarded through challenge/quiz/simulation
    submissions here. Plain AI assistant chat does not award XP.
    """
    user_id = get_current_user_id()
    data = request.get_json() or {}
    challenge_id = str(data.get("challenge_id", "")).strip()

    if not challenge_id:
        return jsonify({"error": "challenge_id is required."}), 400

    profile = _get_or_create_profile(user_id)

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
                "new_badges": [],
                "profile": _serialize_profile(profile),
            }
        )

    xp_reward = int(data.get("xp_reward", 10))

    cp = existing or ChallengeProgress(quest_profile_id=profile.id, challenge_id=challenge_id)
    cp.completed = True
    cp.xp_awarded = xp_reward
    cp.completed_at = datetime.now(UTC)
    db.session.add(cp)

    profile.xp += xp_reward
    profile.level = 1 + (profile.xp // _XP_PER_LEVEL)

    new_badges = _check_and_award_badges(profile)
    db.session.commit()

    return jsonify(
        {
            "message": "Challenge submitted successfully.",
            "xp_awarded": xp_reward,
            "new_badges": new_badges,
            "profile": _serialize_profile(profile),
        }
    )


@quest_bp.post("/quiz/submit")
@auth_required
def submit_quiz():
    """Submit a completed quiz with a score and earn XP based on performance.

    Expected payload::

        {
            "quiz_id": "diversification-quiz",
            "score": 80,           // percentage 0-100
            "total_questions": 5,
            "correct_answers": 4
        }

    XP awarded scales with score:
    - 0-49%:  5 XP
    - 50-69%: 10 XP
    - 70-84%: 15 XP
    - 85-100%: 25 XP

    Isolation rule: this endpoint awards XP. AI assistant chat does NOT.
    """
    user_id = get_current_user_id()
    data = request.get_json() or {}
    quiz_id = str(data.get("quiz_id", "")).strip()

    if not quiz_id:
        return jsonify({"error": "quiz_id is required."}), 400

    try:
        score = max(0, min(100, int(data.get("score", 0))))
    except (TypeError, ValueError):
        return jsonify({"error": "score must be an integer between 0 and 100."}), 400

    # Derive a unique challenge_id so quiz attempts are idempotent per quiz_id
    challenge_id = f"quiz:{quiz_id}"

    profile = _get_or_create_profile(user_id)

    existing = (
        db.session.query(ChallengeProgress)
        .filter_by(quest_profile_id=profile.id, challenge_id=challenge_id)
        .first()
    )
    if existing and existing.completed:
        return jsonify(
            {
                "message": "Quiz already completed.",
                "xp_awarded": 0,
                "score": score,
                "new_badges": [],
                "profile": _serialize_profile(profile),
            }
        )

    if score >= 85:
        xp_reward = 25
    elif score >= 70:
        xp_reward = 15
    elif score >= 50:
        xp_reward = 10
    else:
        xp_reward = 5

    cp = existing or ChallengeProgress(quest_profile_id=profile.id, challenge_id=challenge_id)
    cp.completed = True
    cp.xp_awarded = xp_reward
    cp.completed_at = datetime.now(UTC)
    db.session.add(cp)

    profile.xp += xp_reward
    profile.level = 1 + (profile.xp // _XP_PER_LEVEL)

    new_badges = _check_and_award_badges(profile)
    db.session.commit()

    return jsonify(
        {
            "message": "Quiz submitted successfully.",
            "xp_awarded": xp_reward,
            "score": score,
            "new_badges": new_badges,
            "profile": _serialize_profile(profile),
        }
    )


@quest_bp.get("/challenges")
def list_challenges():
    """Return the catalogue of available challenges and quizzes."""
    challenges = [
        {
            "id": "investing-basics-quiz",
            "type": "quiz",
            "title": "Investing Basics Quiz",
            "description": "Test your understanding of goals, risk, and time horizons.",
            "xp_max": 25,
            "linked_lesson_slug": "investing-basics",
        },
        {
            "id": "diversification-quiz",
            "type": "quiz",
            "title": "Diversification Quiz",
            "description": "Prove you understand how spreading risk across holdings works.",
            "xp_max": 25,
            "linked_lesson_slug": "diversification",
        },
        {
            "id": "etfs-quiz",
            "type": "quiz",
            "title": "ETFs & Index Funds Quiz",
            "description": "Demonstrate knowledge of passive investing fundamentals.",
            "xp_max": 25,
            "linked_lesson_slug": "etfs-101",
        },
        {
            "id": "dca-challenge",
            "type": "challenge",
            "title": "Dollar-Cost Averaging Challenge",
            "description": "Set up a simulated DCA plan for a 12-month period.",
            "xp_max": 10,
            "linked_lesson_slug": "dollar-cost-averaging",
        },
        {
            "id": "behavioral-finance-quiz",
            "type": "quiz",
            "title": "Behavioral Finance Quiz",
            "description": "Identify common emotional investing mistakes.",
            "xp_max": 25,
            "linked_lesson_slug": "behavioral-finance",
        },
    ]
    return jsonify({"challenges": challenges})
