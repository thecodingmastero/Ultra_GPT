from backend.app.api.account_routes import account_bp
from backend.app.api.assistant_routes import assistant_bp
from backend.app.api.auth_routes import auth_bp
from backend.app.api.health_routes import health_bp
from backend.app.api.lessons_routes import lessons_bp
from backend.app.api.market_routes import market_bp
from backend.app.api.portfolio_routes import portfolio_bp

BLUEPRINTS = [health_bp, auth_bp, account_bp, assistant_bp, portfolio_bp, market_bp, lessons_bp]
