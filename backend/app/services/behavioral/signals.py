from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Signal definitions: pattern, confidence weight, and coaching guidance.
# Coaching guidance is inspired by A Random Walk Down Wall Street and
# The 5 Mistakes Every Investor Makes — educational only, non-prescriptive.
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class _SignalDef:
    pattern: re.Pattern[str]
    confidence: float  # base confidence score 0.0–1.0
    coaching: str


_SIGNAL_DEFS: dict[str, _SignalDef] = {
    "panic_selling": _SignalDef(
        pattern=re.compile(
            r"\b(panic sell|sell everything|crash.*sell|market is crashing.*sell)\b",
            re.IGNORECASE,
        ),
        confidence=0.85,
        coaching=(
            "Panic selling often locks in losses and keeps investors out of the recovery. "
            "History shows that missing just a handful of the market's best days—which tend to "
            "follow its worst—dramatically reduces long-term returns. Consider whether your "
            "time horizon and overall allocation still match your goals before reacting to "
            "short-term volatility."
        ),
    ),
    "fomo": _SignalDef(
        pattern=re.compile(
            r"\b(fomo|missing out|everyone is buying|buy before it(?: is|'s) too late)\b",
            re.IGNORECASE,
        ),
        confidence=0.80,
        coaching=(
            "Fear of missing out is one of the most common reasons investors buy at peaks. "
            "By the time an opportunity feels 'obvious,' it is often already priced in. "
            "Maintaining a consistent, disciplined strategy—such as dollar-cost averaging—"
            "removes the pressure to time markets perfectly."
        ),
    ),
    "overconfidence": _SignalDef(
        pattern=re.compile(
            r"\b(can't lose|cannot lose|sure winner|easy money)\b",
            re.IGNORECASE,
        ),
        confidence=0.80,
        coaching=(
            "Overconfidence is the tendency to underestimate risk when things are going well. "
            "Every investment carries uncertainty. A sound approach includes stress-testing "
            "assumptions, keeping position sizes in check, and remembering that even "
            "professional fund managers rarely beat diversified index funds consistently."
        ),
    ),
    "chasing_hot_stocks": _SignalDef(
        pattern=re.compile(
            r"\b(hot stock|meme stock|next nvidia|to the moon)\b",
            re.IGNORECASE,
        ),
        confidence=0.75,
        coaching=(
            "Chasing recent winners (momentum chasing) has historically led to buying near "
            "peaks. Research consistently shows that last year's top performers often "
            "underperform in subsequent years. Focusing on broad diversification and "
            "long-term fundamentals tends to produce more reliable outcomes."
        ),
    ),
    "lack_of_diversification": _SignalDef(
        pattern=re.compile(
            r"\b(all in|one stock|single stock portfolio)\b",
            re.IGNORECASE,
        ),
        confidence=0.90,
        coaching=(
            "Concentrating a portfolio in a single stock or sector magnifies both gains and "
            "losses. Diversification across asset classes, sectors, and geographies is one of "
            "the few 'free lunches' in investing—it reduces unsystematic risk without "
            "necessarily reducing expected returns. Low-cost index funds make broad "
            "diversification easy to achieve."
        ),
    ),
}


@dataclass(slots=True)
class BehavioralSignal:
    """A detected behavioral bias with confidence and coaching guidance."""

    signal: str
    confidence: float
    coaching: str
    matches: list[str] = field(default_factory=list)


class BehavioralSignalService:
    """Detects common investor behavioral biases from free-text input.

    The heuristics are rule-based for Phase 3. The class is designed to be
    easily extended with ML-based classifiers in future phases.
    """

    def detect_signals(self, message: str) -> list[str]:
        """Return signal names only (backward-compatible with Phase 2 API)."""
        normalized = message.strip()
        if not normalized:
            return []
        return [name for name, defn in _SIGNAL_DEFS.items() if defn.pattern.search(normalized)]

    def analyze(self, message: str) -> list[BehavioralSignal]:
        """Return full behavioral analysis with confidence scores and coaching.

        Each detected signal includes:
        - signal name
        - confidence score (0.0–1.0)
        - educational coaching guidance
        - list of matched text fragments
        """
        normalized = message.strip()
        if not normalized:
            return []

        results: list[BehavioralSignal] = []
        for name, defn in _SIGNAL_DEFS.items():
            found = defn.pattern.findall(normalized)
            if found:
                # Boost confidence slightly when multiple phrases are matched
                bonus = min(0.1, 0.03 * (len(found) - 1))
                score = min(1.0, round(defn.confidence + bonus, 2))
                results.append(
                    BehavioralSignal(
                        signal=name,
                        confidence=score,
                        coaching=defn.coaching,
                        # findall with a single capturing group always returns list[str]
                        matches=list(found),
                    )
                )
                logger.info(
                    "behavioral_signal_detected",
                    extra={"signal": name, "confidence": score, "match_count": len(found)},
                )
        return results
