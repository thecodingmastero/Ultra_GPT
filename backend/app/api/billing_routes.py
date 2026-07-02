from flask import Blueprint, jsonify

billing_bp = Blueprint("billing", __name__, url_prefix="/api/billing")

_PLANS = [
    {
        "id": "free",
        "name": "Free",
        "price_monthly": 0.0,
        "price_label": "$0/month",
        "description": "Starter assistant usage, limited saved portfolios, and basic learning access.",
        "features": ["AI assistant (limited)", "1 saved portfolio", "Basic educational hub"],
    },
    {
        "id": "single",
        "name": "Single",
        "price_monthly": 10.0,
        "price_label": "$10/month",
        "description": "Expanded assistant usage, more saved portfolios, and deeper progress analytics.",
        "features": [
            "AI assistant (extended)",
            "Unlimited saved portfolios",
            "Full educational hub + progress tracking",
            "Portfolio concentration analysis",
        ],
    },
    {
        "id": "family",
        "name": "Family",
        "price_monthly": 0.0,
        "price_label": "Custom",
        "description": "Shared learning support and account-level access for households.",
        "features": ["Everything in Single", "Multiple household profiles", "Shared watchlists"],
    },
    {
        "id": "business",
        "name": "Business",
        "price_monthly": 0.0,
        "price_label": "Custom",
        "description": "Multi-user education access and future team features.",
        "features": ["Everything in Family", "Team dashboard", "Priority support"],
    },
]


@billing_bp.get("/plans")
def list_plans():
    return jsonify({"plans": _PLANS})
