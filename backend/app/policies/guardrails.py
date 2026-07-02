from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Literal

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ASSISTANT_DISCLAIMER = (
    "The Better Investor is for educational purposes only and does not provide personalized financial advice."
)

ExplainDepth = Literal["simple", "deep"]

# ---------------------------------------------------------------------------
# Prohibited-content patterns
# ---------------------------------------------------------------------------

DIRECTIVE_PATTERN = re.compile(
    r"\b(should i buy|should i sell|what should i buy|what should i sell|recommend me|tell me what to buy|"
    r"best stock to buy|exact stock pick|hot stock|all in|guaranteed?)\b",
    re.IGNORECASE,
)

GUARANTEE_PATTERN = re.compile(r"\b(guarantee|risk[- ]?free|certain return|sure profit)\b", re.IGNORECASE)

# ---------------------------------------------------------------------------
# Book-based guidance themes
# Inspired by: A Random Walk Down Wall Street (Malkiel)
#              The 5 Mistakes Every Investor Makes (Hanson)
# These themes are injected into every system prompt so that all AI
# responses reinforce research-backed educational principles.
# ---------------------------------------------------------------------------

_BOOK_GUIDANCE_THEMES = (
    "- Long-term perspective: short-term market movements are largely unpredictable; "
    "time in the market consistently beats timing the market.\n"
    "- Diversification: spread holdings across asset classes, sectors, and geographies "
    "to reduce unsystematic risk.\n"
    "- Low-cost index funds: actively managed funds rarely beat passive index funds after fees; "
    "minimize costs to maximize compounding.\n"
    "- Emotional discipline: panic selling, FOMO, and overconfidence are leading causes of "
    "underperformance; acknowledge emotions without acting on impulse.\n"
    "- Avoid market timing: no one reliably predicts market tops or bottoms; consistent, "
    "periodic investing (e.g. dollar-cost averaging) reduces timing risk."
)

# ---------------------------------------------------------------------------
# System prompts per depth level
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT_SIMPLE = (
    "You are The Better Investor AI Coach. "
    "Explain investing concepts clearly and simply for beginners. "
    "Use plain language, short sentences, and concrete examples. "
    "Never give direct buy/sell directives or guarantee returns. "
    "Always emphasise diversification, risk awareness, and long-term discipline.\n\n"
    "Educational principles to reinforce:\n"
    f"{_BOOK_GUIDANCE_THEMES}"
)

_SYSTEM_PROMPT_DEEP = (
    "You are The Better Investor AI Coach delivering a deep educational explanation. "
    "Go beyond surface-level concepts: explain the underlying mechanics, historical context, "
    "trade-offs, and relevant academic evidence where appropriate. "
    "Structure your response clearly (use numbered steps or headings if helpful). "
    "Never give direct buy/sell directives or guarantee returns. "
    "Always emphasise diversification, risk awareness, and long-term discipline.\n\n"
    "Educational principles to reinforce:\n"
    f"{_BOOK_GUIDANCE_THEMES}"
)

_SYSTEM_PROMPTS: dict[str, str] = {
    "simple": _SYSTEM_PROMPT_SIMPLE,
    "deep": _SYSTEM_PROMPT_DEEP,
}


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class PolicyResult:
    blocked: bool
    response: str | None = None
    reason: str | None = None


@dataclass(slots=True)
class PolicyMetadata:
    """Metadata about the policy decision attached to every AI response."""

    blocked: bool
    depth: str
    disclaimer_appended: bool
    block_reason: str | None = None
    flags: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Policy class
# ---------------------------------------------------------------------------

class AssistantPolicy:
    """Stateless guardrail layer for the AI assistant.

    Responsibilities:
    - Detect and block prohibited request types (direct directives, return guarantees).
    - Select the appropriate system prompt based on requested explanation depth.
    - Append the educational disclaimer to every response that lacks one.
    - Emit structured log entries for every policy decision (audit trail).

    Designed as a reusable middleware/service — not hardcoded in route handlers.
    """

    # Keep the legacy attribute for any code that reads it directly
    system_prompt: str = _SYSTEM_PROMPT_SIMPLE

    def get_system_prompt(self, depth: str = "simple") -> str:
        """Return the system prompt appropriate for the requested explanation depth."""
        return _SYSTEM_PROMPTS.get(depth, _SYSTEM_PROMPT_SIMPLE)

    def review(self, message: str) -> PolicyResult:
        """Inspect the user message and return a blocking decision if required."""
        directive_match = DIRECTIVE_PATTERN.search(message)
        guarantee_match = GUARANTEE_PATTERN.search(message)

        if directive_match or guarantee_match:
            reason = "directive" if directive_match else "guarantee"
            logger.info(
                "policy_block",
                extra={"reason": reason, "message_preview": message[:120]},
            )
            return PolicyResult(
                blocked=True,
                reason=reason,
                response=(
                    "I can’t provide direct buy/sell instructions or guaranteed-return claims. "
                    "For educational planning, consider: (1) goals and time horizon, (2) diversification across holdings and sectors, "
                    "(3) risk tolerance and downside scenarios, and (4) long-term discipline over short-term market timing."
                ),
            )

        logger.debug("policy_pass", extra={"message_preview": message[:120]})
        return PolicyResult(blocked=False)

    def finalize(self, response: str) -> tuple[str, bool]:
        """Append disclaimer if not already present; return (text, disclaimer_appended)."""
        base = response.strip()
        if "educational" not in base.lower() and "financial advice" not in base.lower():
            return f"{base}\n\n{ASSISTANT_DISCLAIMER}", True
        return base, False
