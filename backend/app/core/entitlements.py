"""Centralized plan entitlement checks for The Better Investor.

Feature access matrix:
┌────────────────────────────┬──────┬────────┬────────┬──────────┐
│ Feature                    │ Free │ Single │ Family │ Business │
├────────────────────────────┼──────┼────────┼────────┼──────────┤
│ AI assistant (basic)       │  ✓   │   ✓    │   ✓    │    ✓     │
│ AI assistant (extended)    │      │   ✓    │   ✓    │    ✓     │
│ Saved portfolios (max)     │  1   │  ∞     │  ∞     │    ∞     │
│ Portfolio analytics (full) │      │   ✓    │   ✓    │    ✓     │
│ Educational hub (basic)    │  ✓   │   ✓    │   ✓    │    ✓     │
│ Educational hub (full)     │      │   ✓    │   ✓    │    ✓     │
│ Progress tracking          │      │   ✓    │   ✓    │    ✓     │
│ Investor Quest             │  ✓   │   ✓    │   ✓    │    ✓     │
│ Market data (basic quotes) │  ✓   │   ✓    │   ✓    │    ✓     │
│ Chart data                 │      │   ✓    │   ✓    │    ✓     │
│ Watchlist                  │      │   ✓    │   ✓    │    ✓     │
│ Family profiles            │      │        │   ✓    │    ✓     │
│ Team dashboard             │      │        │        │    ✓     │
└────────────────────────────┴──────┴────────┴────────┴──────────┘

Usage::

    from backend.app.core.entitlements import plan_required, Feature

    @portfolio_bp.get("/full-analysis")
    @auth_required
    @plan_required(Feature.PORTFOLIO_ANALYTICS_FULL)
    def full_analysis():
        ...
"""
from __future__ import annotations

from enum import Enum
from functools import wraps

from flask import jsonify

from backend.app.core.auth import get_current_user_id
from backend.app.extensions import db
from backend.app.models.subscription import SubscriptionStatus


class Feature(str, Enum):
    """Enumeration of gated product features."""
    AI_ASSISTANT_BASIC = "ai_assistant_basic"
    AI_ASSISTANT_EXTENDED = "ai_assistant_extended"
    PORTFOLIO_ANALYTICS_FULL = "portfolio_analytics_full"
    SAVED_PORTFOLIOS_UNLIMITED = "saved_portfolios_unlimited"
    EDUCATION_FULL = "education_full"
    PROGRESS_TRACKING = "progress_tracking"
    CHART_DATA = "chart_data"
    WATCHLIST = "watchlist"
    FAMILY_PROFILES = "family_profiles"
    TEAM_DASHBOARD = "team_dashboard"


# Maps plan id → set of features available on that plan
_PLAN_FEATURES: dict[str, set[Feature]] = {
    "free": {
        Feature.AI_ASSISTANT_BASIC,
    },
    "single": {
        Feature.AI_ASSISTANT_BASIC,
        Feature.AI_ASSISTANT_EXTENDED,
        Feature.PORTFOLIO_ANALYTICS_FULL,
        Feature.SAVED_PORTFOLIOS_UNLIMITED,
        Feature.EDUCATION_FULL,
        Feature.PROGRESS_TRACKING,
        Feature.CHART_DATA,
        Feature.WATCHLIST,
    },
    "family": {
        Feature.AI_ASSISTANT_BASIC,
        Feature.AI_ASSISTANT_EXTENDED,
        Feature.PORTFOLIO_ANALYTICS_FULL,
        Feature.SAVED_PORTFOLIOS_UNLIMITED,
        Feature.EDUCATION_FULL,
        Feature.PROGRESS_TRACKING,
        Feature.CHART_DATA,
        Feature.WATCHLIST,
        Feature.FAMILY_PROFILES,
    },
    "business": {
        Feature.AI_ASSISTANT_BASIC,
        Feature.AI_ASSISTANT_EXTENDED,
        Feature.PORTFOLIO_ANALYTICS_FULL,
        Feature.SAVED_PORTFOLIOS_UNLIMITED,
        Feature.EDUCATION_FULL,
        Feature.PROGRESS_TRACKING,
        Feature.CHART_DATA,
        Feature.WATCHLIST,
        Feature.FAMILY_PROFILES,
        Feature.TEAM_DASHBOARD,
    },
}

_UPGRADE_MESSAGES: dict[Feature, str] = {
    Feature.AI_ASSISTANT_EXTENDED: "Extended AI assistant is available on the Single plan ($10/month). Upgrade to unlock longer, deeper conversations.",
    Feature.PORTFOLIO_ANALYTICS_FULL: "Full portfolio analytics is available on the Single plan ($10/month). Upgrade for concentration, sector, and volatility insights.",
    Feature.SAVED_PORTFOLIOS_UNLIMITED: "Unlimited saved portfolios require the Single plan ($10/month). Free accounts can save one portfolio.",
    Feature.EDUCATION_FULL: "The full educational hub is available on the Single plan ($10/month). Upgrade to access all lessons and topics.",
    Feature.PROGRESS_TRACKING: "Progress tracking is available on the Single plan ($10/month). Upgrade to record completed lessons.",
    Feature.CHART_DATA: "Chart data is available on the Single plan ($10/month). Upgrade to view historical price charts.",
    Feature.WATCHLIST: "Watchlists are available on the Single plan ($10/month). Upgrade to save and monitor symbols.",
    Feature.FAMILY_PROFILES: "Family profiles are available on the Family plan. Upgrade to share learning across household accounts.",
    Feature.TEAM_DASHBOARD: "Team dashboard is available on the Business plan. Contact us for enterprise pricing.",
}


def get_user_plan_id(user_id: int) -> str:
    """Return the active plan id for *user_id*, defaulting to 'free'."""
    status = db.session.query(SubscriptionStatus).filter_by(user_id=user_id, is_active=True).first()
    if status is None or status.plan is None:
        return "free"
    return status.plan.name.lower()


def has_feature(user_id: int, feature: Feature) -> bool:
    """Return True if *user_id*'s active plan includes *feature*."""
    plan_id = get_user_plan_id(user_id)
    return feature in _PLAN_FEATURES.get(plan_id, set())


def plan_required(feature: Feature):
    """Route decorator that returns 403 with an upgrade prompt when the user's plan
    does not include *feature*.  Must be applied after ``@auth_required``."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user_id = get_current_user_id()
            if not has_feature(user_id, feature):
                upgrade_msg = _UPGRADE_MESSAGES.get(
                    feature,
                    "This feature is not available on your current plan. Please upgrade to unlock it.",
                )
                return jsonify({
                    "error": "Feature not available on your current plan.",
                    "upgrade_prompt": upgrade_msg,
                    "feature": feature.value,
                }), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
