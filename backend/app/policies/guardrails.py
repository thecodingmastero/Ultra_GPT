from __future__ import annotations

import re
from dataclasses import dataclass


ASSISTANT_DISCLAIMER = (
    "The Better Investor is for educational purposes only and does not provide personalized financial advice."
)

DIRECTIVE_PATTERN = re.compile(
    r"\b(should i buy|should i sell|what should i buy|what should i sell|recommend me|tell me what to buy|"
    r"best stock to buy|exact stock pick|hot stock|all in|guaranteed?)\b",
    re.IGNORECASE,
)

GUARANTEE_PATTERN = re.compile(r"\b(guarantee|risk[- ]?free|certain return|sure profit)\b", re.IGNORECASE)


@dataclass(slots=True)
class PolicyResult:
    blocked: bool
    response: str | None = None


class AssistantPolicy:
    system_prompt = (
        "You are The Better Investor AI Coach. Provide investing education only, never personalized advice. "
        "Do not provide buy/sell directives and never guarantee returns. "
        "Emphasize diversification, risk awareness, and long-term investing principles."
    )

    def review(self, message: str) -> PolicyResult:
        if DIRECTIVE_PATTERN.search(message) or GUARANTEE_PATTERN.search(message):
            return PolicyResult(
                blocked=True,
                response=(
                    "I can’t provide direct buy/sell instructions or guaranteed-return claims. "
                    "For educational planning, consider: (1) goals and time horizon, (2) diversification across holdings and sectors, "
                    "(3) risk tolerance and downside scenarios, and (4) long-term discipline over short-term market timing."
                ),
            )
        return PolicyResult(blocked=False)

    def finalize(self, response: str) -> str:
        base = response.strip()
        if "educational" not in base.lower() or "financial advice" not in base.lower():
            return f"{base}\n\n{ASSISTANT_DISCLAIMER}"
        return base
