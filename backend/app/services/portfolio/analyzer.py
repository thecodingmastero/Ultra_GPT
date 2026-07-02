from __future__ import annotations

from collections.abc import Sequence

from backend.app.services.market_data.service import MarketDataService

# Maps each risk/topic area to relevant lesson slugs users can explore.
_TOPIC_LESSON_MAP: dict[str, list[str]] = {
    "concentration": ["diversification", "risk-management"],
    "sector": ["diversification", "etfs-101", "index-funds"],
    "small_portfolio": ["investing-basics", "diversification"],
    "volatility": ["risk-management", "behavioral-finance", "dollar-cost-averaging"],
}


def _learning_suggestions(flags: list[str], sector_count: int, position_count: int) -> list[dict]:
    """Return structured educational suggestions based on detected risk conditions."""
    suggestions: list[dict] = []
    seen_slugs: set[str] = set()

    def _add(slugs: list[str], reason: str) -> None:
        for slug in slugs:
            if slug not in seen_slugs:
                seen_slugs.add(slug)
                suggestions.append({"lesson_slug": slug, "reason": reason})

    for flag in flags:
        if "single holding" in flag or "top two" in flag:
            _add(_TOPIC_LESSON_MAP["concentration"], "Reduce concentration risk by spreading across more holdings.")
        if "sector" in flag:
            _add(_TOPIC_LESSON_MAP["sector"], "Explore sector diversification using ETFs or index funds.")
        if "fewer than three" in flag:
            _add(_TOPIC_LESSON_MAP["small_portfolio"], "A larger number of positions can reduce single-company risk.")

    if sector_count == 1 and position_count > 2:
        _add(_TOPIC_LESSON_MAP["sector"], "All holdings are in the same sector — consider broadening exposure.")

    return suggestions[:5]  # cap at 5 to keep response focused


class PortfolioAnalyzer:
    def __init__(self, market_data_service: MarketDataService) -> None:
        self.market_data_service = market_data_service

    def analyze(self, holdings: Sequence[dict]) -> dict:
        if not holdings:
            raise ValueError("At least one holding is required.")

        positions: list[dict] = []
        sector_values: dict[str, float] = {}
        total_value = 0.0
        for holding in holdings:
            symbol = holding["symbol"].strip().upper()
            quantity = float(holding["quantity"])
            if quantity <= 0:
                raise ValueError("Quantities must be greater than zero.")
            quote = self.market_data_service.get_quote(symbol)
            profile = self.market_data_service.get_company_profile(symbol)
            market_value = round(quantity * quote["current_price"], 2)
            total_value += market_value
            sector = profile.get("finnhub_industry") or "Unclassified"
            sector_values[sector] = sector_values.get(sector, 0.0) + market_value
            positions.append(
                {
                    "symbol": symbol,
                    "company_name": quote.get("company_name", symbol),
                    "sector": sector,
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
        sector_breakdown = sorted(
            (
                {"sector": sector, "market_value": round(value, 2), "weight": round(value / total_value, 4) if total_value else 0.0}
                for sector, value in sector_values.items()
            ),
            key=lambda item: item["weight"],
            reverse=True,
        )
        top_sector_weight = sector_breakdown[0]["weight"] if sector_breakdown else 0.0

        risk_flags: list[str] = []
        if top_weight >= 0.4:
            risk_flags.append("A single holding is above 40% of the portfolio, which suggests elevated concentration risk.")
        if top_two_weight >= 0.65:
            risk_flags.append("The top two holdings make up more than 65% of the portfolio, so diversification could be improved.")
        if top_sector_weight >= 0.6:
            risk_flags.append("A single sector is above 60% of the portfolio, which can increase exposure to one part of the market.")
        if len(positions) < 3:
            risk_flags.append("Owning fewer than three positions can make performance heavily dependent on a small number of companies.")

        # --- Volatility heuristic ---
        # Approximate portfolio volatility using a simplified intra-day range proxy.
        # This is an educational heuristic, not a statistically precise metric.
        total_weight_sq = sum(p["weight"] ** 2 for p in positions)
        # Herfindahl-Hirschman Index (HHI) as a concentration proxy (0 = perfectly spread, 1 = one holding)
        hhi = round(total_weight_sq, 4)
        volatility_label: str
        if hhi >= 0.5:
            volatility_label = "high"
            risk_flags.append(
                "Portfolio concentration (HHI) is high, suggesting above-average sensitivity to individual holding moves."
            )
        elif hhi >= 0.25:
            volatility_label = "moderate"
        else:
            volatility_label = "low"

        diversification_score = round(max(0.0, 1.0 - hhi) * 100, 1)

        feedback = (
            "Review whether each position has a clear role, compare your allocation against a diversified benchmark, "
            "and make sure your portfolio matches your time horizon and tolerance for volatility."
        )
        if not risk_flags:
            feedback = (
                "The portfolio appears reasonably spread for an MVP-level check, but continue monitoring diversification, "
                "costs, and how each holding fits a long-term plan."
            )

        learning_suggestions = _learning_suggestions(risk_flags, len(sector_values), len(positions))

        return {
            "summary": {
                "total_market_value": round(total_value, 2),
                "position_count": len(positions),
                "sector_count": len(sector_values),
                "diversification_score": diversification_score,
                "volatility_label": volatility_label,
                "hhi": hhi,
            },
            "positions": positions,
            "sector_breakdown": sector_breakdown,
            "risk_flags": risk_flags,
            "educational_feedback": feedback,
            "learning_suggestions": learning_suggestions,
        }
