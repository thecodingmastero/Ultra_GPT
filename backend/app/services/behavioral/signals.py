from __future__ import annotations

import re


_SIGNAL_PATTERNS = {
    "panic_selling": re.compile(r"\b(panic sell|sell everything|crash.*sell|market is crashing.*sell)\b", re.IGNORECASE),
    "fomo": re.compile(r"\b(fomo|missing out|everyone is buying|buy before it is too late)\b", re.IGNORECASE),
    "overconfidence": re.compile(r"\b(can't lose|cannot lose|sure winner|easy money)\b", re.IGNORECASE),
    "chasing_hot_stocks": re.compile(r"\b(hot stock|meme stock|next nvidia|to the moon)\b", re.IGNORECASE),
    "lack_of_diversification": re.compile(r"\b(all in|one stock|single stock portfolio)\b", re.IGNORECASE),
}


class BehavioralSignalService:
    def detect_signals(self, message: str) -> list[str]:
        normalized = message.strip()
        if not normalized:
            return []
        return [signal for signal, pattern in _SIGNAL_PATTERNS.items() if pattern.search(normalized)]
