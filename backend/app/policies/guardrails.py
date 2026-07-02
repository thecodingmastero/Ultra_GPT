from __future__ import annotations

import re
from dataclasses import dataclass


ASSISTANT_DISCLAIMER = (
    "The Better Investor is for educational purposes only and does not provide personalized financial advice."
)

# Patterns that trigger an immediate block — direct buy/sell directives
DIRECTIVE_PATTERN = re.compile(
    r"\b(should i buy|should i sell|what should i buy|what should i sell|recommend me|tell me what to buy|"
    r"best stock to buy|exact stock pick|hot stock|all in|guaranteed?|"
    r"which stock(s)? should i|give me a stock tip|pick a stock for me|"
    r"what (stock|etf|fund) (should|do) i (buy|invest in|pick)|"
    r"just tell me what to (buy|sell|invest|do))\b",
    re.IGNORECASE,
)

# Patterns for guaranteed returns / risk-free language
GUARANTEE_PATTERN = re.compile(
    r"\b(guarantee|risk[- ]?free|certain return|sure profit|no[- ]?risk|"
    r"100%\s*(safe|guaranteed?|profit|return)|always (goes|goes up|win|profit))\b",
    re.IGNORECASE,
)

# Patterns that signal high-pressure / market-timing urgency
URGENCY_PATTERN = re.compile(
    r"\b(buy now|sell now|buy today|sell today|buy before (it|the|market)|"
    r"last chance to (buy|invest)|urgent (buy|sell)|act now|don't wait)\b",
    re.IGNORECASE,
)


@dataclass(slots=True)
class PolicyResult:
    blocked: bool
    response: str | None = None


class AssistantPolicy:
    system_prompt = (
        "You are The Better Investor AI Coach — an educational investing assistant. "
        "Your role is to help users learn investing concepts, not to give personalized financial advice. "
        "Never recommend specific buy or sell actions for individual securities. "
        "Never guarantee returns, suggest risk-free outcomes, or create urgency to act. "
        "Always emphasize: (1) diversification and spreading risk, (2) understanding time horizon and personal goals, "
        "(3) long-term discipline over short-term market timing, (4) consulting a licensed financial advisor "
        "for personalized decisions. Frame all responses around investor education. "
        "Slogan: Smarter Investing Starts Here."
    )

    _BLOCK_RESPONSE = (
        "I can’t provide direct buy/sell instructions or guaranteed-return claims. "
        "For educational planning, consider: (1) goals and time horizon, (2) diversification across holdings and sectors, "
        "(3) risk tolerance and downside scenarios, and (4) long-term discipline over short-term market timing."
    )

    _URGENCY_RESPONSE = (
        "I can’t encourage urgent buy/sell decisions — market timing is notoriously difficult and often leads to poor outcomes. "
        "A more resilient approach: define a clear investment plan, diversify broadly, and invest consistently over time "
        "rather than reacting to short-term signals."
    )

    def review(self, message: str) -> PolicyResult:
        if DIRECTIVE_PATTERN.search(message) or GUARANTEE_PATTERN.search(message):
            return PolicyResult(blocked=True, response=self._BLOCK_RESPONSE)
        if URGENCY_PATTERN.search(message):
            return PolicyResult(blocked=True, response=self._URGENCY_RESPONSE)
        return PolicyResult(blocked=False)

    def finalize(self, response: str) -> str:
        base = response.strip()
        if "educational" not in base.lower() and "financial advice" not in base.lower():
            return f"{base}\n\n{ASSISTANT_DISCLAIMER}"
        return base
