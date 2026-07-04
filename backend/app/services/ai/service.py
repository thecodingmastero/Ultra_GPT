from __future__ import annotations

from backend.app.policies.guardrails import ASSISTANT_DISCLAIMER, AssistantPolicy, PolicyMetadata
from backend.app.providers.ai.base import AIProvider
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

    def chat(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
        depth: str = "simple",
    ) -> dict:
        """Process a user message and return an educational assistant response.

        Parameters
        ----------
        message:
            The user's question or statement.
        history:
            Prior conversation turns in ``[{"role": ..., "content": ...}]`` format.
        depth:
            Explanation depth — ``"simple"`` (default, beginner-friendly) or
            ``"deep"`` (detailed, covers mechanics and academic evidence).

        Returns
        -------
        dict with keys:
        - ``response``: the educational response text
        - ``disclaimer``: the standard educational-only disclaimer
        - ``behavioral_signals``: list of signal names (backward-compatible)
        - ``behavioral_coaching``: list of dicts with signal, confidence, coaching
        - ``policy_metadata``: dict describing the policy decision made
        """
        # Behavioral analysis
        behavioral_signals = self.behavioral_signal_service.detect_signals(message)
        behavioral_detail = self.behavioral_signal_service.analyze(message)

        # Policy review
        review = self.policy.review(message)
        depth_value = depth if depth in ("simple", "deep") else "simple"

        if review.blocked:
            raw_response = review.response or "I can only provide educational guidance."
            finalized, disclaimer_appended = self.policy.finalize(raw_response)
            policy_meta = PolicyMetadata(
                blocked=True,
                depth=depth_value,
                disclaimer_appended=disclaimer_appended,
                block_reason=review.reason,
                flags=behavioral_signals,
            )
        else:
            system_prompt = self.policy.get_system_prompt(depth_value)
            messages = [
                {"role": "system", "content": system_prompt},
                *(history or []),
                {"role": "user", "content": message},
            ]
            raw_response = self.provider.chat(messages)
            finalized, disclaimer_appended = self.policy.finalize(raw_response)
            policy_meta = PolicyMetadata(
                blocked=False,
                depth=depth_value,
                disclaimer_appended=disclaimer_appended,
                flags=behavioral_signals,
            )

        return {
            "response": finalized,
            "disclaimer": ASSISTANT_DISCLAIMER,
            "behavioral_signals": behavioral_signals,
            "behavioral_coaching": [
                {
                    "signal": s.signal,
                    "confidence": s.confidence,
                    "coaching": s.coaching,
                }
                for s in behavioral_detail
            ],
            "policy_metadata": {
                "blocked": policy_meta.blocked,
                "depth": policy_meta.depth,
                "disclaimer_appended": policy_meta.disclaimer_appended,
                "block_reason": policy_meta.block_reason,
                "flags": policy_meta.flags,
            },
        }
