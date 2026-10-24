from __future__ import annotations

import re


def parse_stop_words(raw: str | None) -> list[str]:
    if not raw or not raw.strip():
        return []
    parts = re.split(r"[,;\n]+", raw.lower())
    return [p.strip() for p in parts if p.strip()]


def review_matches_stop_words(review_text: str | None, stop_words_raw: str | None) -> bool:
    words = parse_stop_words(stop_words_raw)
    if not words:
        return False
    hay = (review_text or "").lower()
    return any(w in hay for w in words)
