from __future__ import annotations

from backend.app.extensions import db
from backend.app.models import Holding, Portfolio


class HoldingsRepository:
    @staticmethod
    def _default_portfolio_for_user(user_id: int) -> Portfolio:
        portfolio = Portfolio.query.filter_by(user_id=user_id, name="My Portfolio").first()
        if portfolio is None:
            portfolio = Portfolio(user_id=user_id, name="My Portfolio")
            db.session.add(portfolio)
            db.session.flush()
        return portfolio

    def list_for_user(self, user_id: int) -> list[Holding]:
        return (
            Holding.query.join(Portfolio, Holding.portfolio_id == Portfolio.id)
            .filter(Portfolio.user_id == user_id)
            .order_by(Holding.id.asc())
            .all()
        )

    def create_for_user(self, user_id: int, symbol: str, quantity: float) -> Holding:
        portfolio = self._default_portfolio_for_user(user_id)
        holding = Holding(portfolio_id=portfolio.id, symbol=symbol, quantity=quantity)
        db.session.add(holding)
        db.session.commit()
        return holding

    def get_for_user(self, user_id: int, holding_id: int) -> Holding | None:
        return (
            Holding.query.join(Portfolio, Holding.portfolio_id == Portfolio.id)
            .filter(Portfolio.user_id == user_id, Holding.id == holding_id)
            .first()
        )

    def update(self, holding: Holding, symbol: str, quantity: float) -> Holding:
        holding.symbol = symbol
        holding.quantity = quantity
        db.session.commit()
        return holding

    def delete(self, holding: Holding) -> None:
        db.session.delete(holding)
        db.session.commit()
