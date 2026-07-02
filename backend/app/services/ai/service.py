from __future__ import annotations

from backend.app.services.ai.base import AIProvider
from backend.app.services.ai.policy import ASSISTANT_DISCLAIMER, AssistantPolicy
from backend.app.services.behavioral.signals import BehavioralSignalService


class AssistantService:
    def __init__(
        self,
        provider: AIProvider,
        policy: AssistantPolicy | None = None,
        behavioral_signal_service: BehavioralSignalService | None = None,
    ) -> None:
        self.provider = provider
        self.policy = policy or AssistantPolicy()
        self.behavioral_signal_service = behavioral_signal_service or BehavioralSignalService()

    def chat(self, message: str, history: list[dict[str, str]] | None = None) -> dict[str, str]:
        behavioral_signals = self.behavioral_signal_service.detect_signals(message)
        review = self.policy.review(message)
        if review.blocked:
            response = review.response or "I can only provide educational guidance."
        else:
            messages = [{"role": "system", "content": self.policy.system_prompt}, *(history or []), {"role": "user", "content": message}]
            response = self.provider.chat(messages)
        return {
            "response": self.policy.finalize(response),
            "disclaimer": ASSISTANT_DISCLAIMER,
            "behavioral_signals": behavioral_signals,
        }
