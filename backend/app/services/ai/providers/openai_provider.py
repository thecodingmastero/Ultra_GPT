from __future__ import annotations

from typing import Sequence

from backend.app.services.ai.base import AIProvider


class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str = "", model: str = "gpt-4.1-mini") -> None:
        self.api_key = api_key
        self.model = model

    def chat(self, messages: Sequence[dict[str, str]]) -> str:
        user_message = next((message["content"] for message in reversed(messages) if message["role"] == "user"), "")
        return (
            f"Here’s an educational way to think about '{user_message}': start with the business model, "
            "understand the main risks, compare it against a diversified baseline like a broad index fund, "
            "and decide whether it fits your goals, time horizon, and ability to stay disciplined during market swings."
        )
