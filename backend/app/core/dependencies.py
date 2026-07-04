from __future__ import annotations

from flask import current_app

from backend.app.policies.guardrails import AssistantPolicy
from backend.app.providers.ai.stub_provider import StubAIProvider
from backend.app.providers.market_data.finnhub_provider import FinnhubMarketDataProvider
from backend.app.repositories.holdings_repository import HoldingsRepository
from backend.app.repositories.lessons_repository import LessonsRepository
from backend.app.services.ai.providers.openai_provider import OpenAIProvider
from backend.app.services.ai.service import AssistantService
from backend.app.services.behavioral.signals import BehavioralSignalService
from backend.app.services.market_data.service import MarketDataService
from backend.app.services.portfolio.analyzer import PortfolioAnalyzer


def get_ai_provider():
    provider = current_app.config.get("AI_PROVIDER_INSTANCE")
    if provider is not None:
        return provider

    provider_name = current_app.config.get("AI_PROVIDER", "stub")
    if provider_name == "openai":
        return OpenAIProvider(
            api_key=current_app.config.get("OPENAI_API_KEY", ""),
            model=current_app.config.get("OPENAI_MODEL", "gpt-4.1-mini"),
        )
    if provider_name == "stub":
        return StubAIProvider()
    raise ValueError(f"Unsupported AI provider: {provider_name}")


def get_market_data_provider():
    provider = current_app.config.get("MARKET_DATA_PROVIDER_INSTANCE")
    if provider is not None:
        return provider

    provider_name = current_app.config.get("MARKET_DATA_PROVIDER", "finnhub")
    if provider_name == "finnhub":
        return FinnhubMarketDataProvider(api_key=current_app.config.get("FINNHUB_API_KEY", ""))
    raise ValueError(f"Unsupported market data provider: {provider_name}")


def get_behavioral_signal_service() -> BehavioralSignalService:
    return BehavioralSignalService()


def get_assistant_service() -> AssistantService:
    return AssistantService(
        provider=get_ai_provider(),
        policy=AssistantPolicy(),
        behavioral_signal_service=get_behavioral_signal_service(),
    )


def get_market_data_service() -> MarketDataService:
    return MarketDataService(provider=get_market_data_provider())


def get_portfolio_analyzer() -> PortfolioAnalyzer:
    return PortfolioAnalyzer(market_data_service=get_market_data_service())


def get_holdings_repository() -> HoldingsRepository:
    return HoldingsRepository()


def get_lessons_repository() -> LessonsRepository:
    return LessonsRepository()
