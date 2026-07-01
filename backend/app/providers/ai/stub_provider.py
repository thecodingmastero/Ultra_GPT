from __future__ import annotations

from typing import Sequence

from backend.app.providers.ai.base import AIProvider


class StubAIProvider(AIProvider):
    """Safe default provider used in MVP scaffolding."""

    def chat(self, messages: Sequence[dict[str, str]]) -> str:
        user_message = next((message["content"] for message in reversed(messages) if message["role"] == "user"), "")
        return (
            f"Here’s an educational way to think about '{user_message}': focus on your time horizon, diversification, risk tolerance, "
            "and long-term discipline before making any investing decision."
        )
