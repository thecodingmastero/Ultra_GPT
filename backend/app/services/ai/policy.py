from __future__ import annotations

import re
from dataclasses import dataclass


ASSISTANT_DISCLAIMER = (
    "The Better Investor is for education only and does not provide personalized financial advice."
)

DIRECT_ADVICE_PATTERN = re.compile(
    r"\b(should i buy|should i sell|what should i buy|recommend me|tell me what to buy|"
    r"guarantee|sure thing|best stock to buy|exact stock pick|hot stock)\b",
    re.IGNORECASE,
)


@dataclass(slots=True)
class PolicyResult:
    blocked: bool
    response: str | None = None


class AssistantPolicy:
    system_prompt = (
        "You are The Better Investor AI Coach. You provide investing education, not financial advice. "
        "Never guarantee returns or tell users exactly what to buy or sell. Focus on diversification, "
        "risk management, long-term investing, and emotional discipline."
    )

    def review(self, message: str) -> PolicyResult:
        if DIRECT_ADVICE_PATTERN.search(message):
            return PolicyResult(
                blocked=True,
                response=(
                    "I can’t give direct buy or sell instructions. Instead, use this educational framework: "
                    "(1) define your goal and time horizon, (2) review diversification across companies, sectors, "
                    "and asset types, (3) compare valuation, earnings quality, and balance-sheet risk, "
                    "and (4) decide how much volatility you can handle without reacting emotionally. "
                    "Long-term investing, diversification, and risk awareness usually matter more than a single stock pick."
                ),
            )
        return PolicyResult(blocked=False)

    def finalize(self, response: str) -> str:
        base = response.strip()
        if "education only" not in base.lower():
            return f"{base}\n\n{ASSISTANT_DISCLAIMER}"
        return base
