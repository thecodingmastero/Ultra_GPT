from __future__ import annotations

from pathlib import Path

from flask import Flask

from backend.app.api import BLUEPRINTS
from backend.app.config import Config
from backend.app.extensions import cors, db, jwt, migrate
from backend.app.models import (  # noqa: F401
    Badge,
    BehaviorEvent,
    ChallengeProgress,
    ChatMessage,
    ChatSession,
    Holding,
    Lesson,
    LessonProgress,
    Portfolio,
    QuestProfile,
    SubscriptionPlan,
    SubscriptionStatus,
    User,
    Watchlist,
    WatchlistItem,
)


def create_app(config_object: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object)

    Path(app.root_path).parents[1].joinpath("instance").mkdir(exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    @app.get("/")
    def healthcheck() -> dict[str, str]:
        return {"status": "ok", "app": "TheBetterInvestor"}

    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)

    return app
