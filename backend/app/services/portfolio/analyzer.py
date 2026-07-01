from __future__ import annotations

from collections.abc import Sequence

from backend.app.services.market_data.service import MarketDataService


class PortfolioAnalyzer:
    def __init__(self, market_data_service: MarketDataService) -> None:
        self.market_data_service = market_data_service

    def analyze(self, holdings: Sequence[dict]) -> dict:
        if not holdings:
            raise ValueError("At least one holding is required.")

        positions: list[dict] = []
        total_value = 0.0
        for holding in holdings:
            symbol = holding["symbol"].strip().upper()
            quantity = float(holding["quantity"])
            if quantity <= 0:
                raise ValueError("Quantities must be greater than zero.")
            quote = self.market_data_service.get_quote(symbol)
            market_value = round(quantity * quote["current_price"], 2)
            total_value += market_value
            positions.append(
                {
                    "symbol": symbol,
                    "company_name": quote.get("company_name", symbol),
                    "quantity": quantity,
                    "price": quote["current_price"],
                    "market_value": market_value,
                }
            )

        for position in positions:
            position["weight"] = round(position["market_value"] / total_value, 4) if total_value else 0.0

        positions.sort(key=lambda item: item["weight"], reverse=True)
        top_weight = positions[0]["weight"] if positions else 0.0
        top_two_weight = sum(position["weight"] for position in positions[:2])

        risk_flags: list[str] = []
        if top_weight >= 0.4:
            risk_flags.append("A single holding is above 40% of the portfolio, which suggests elevated concentration risk.")
        if top_two_weight >= 0.65:
            risk_flags.append("The top two holdings make up more than 65% of the portfolio, so diversification could be improved.")
        if len(positions) < 3:
            risk_flags.append("Owning fewer than three positions can make performance heavily dependent on a small number of companies.")

        feedback = (
            "Review whether each position has a clear role, compare your allocation against a diversified benchmark, "
            "and make sure your portfolio matches your time horizon and tolerance for volatility."
        )
        if not risk_flags:
            feedback = (
                "The portfolio appears reasonably spread for an MVP-level check, but continue monitoring diversification, "
                "costs, and how each holding fits a long-term plan."
            )

        return {
            "summary": {
                "total_market_value": round(total_value, 2),
                "position_count": len(positions),
            },
            "positions": positions,
            "risk_flags": risk_flags,
            "educational_feedback": feedback,
        }
