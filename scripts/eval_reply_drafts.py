#!/usr/bin/env python3
"""Smoke-eval: прогон sample-отзывов через генерацию (нужен OPENAI_API_KEY в .env)."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SAMPLES = ROOT / "evals" / "review_samples.json"


async def main() -> int:
    if not SAMPLES.is_file():
        print(f"Missing {SAMPLES}")
        return 1
    samples = json.loads(SAMPLES.read_text(encoding="utf-8"))
    from app.core.config import get_settings

    settings = get_settings()
    if not settings.openai_api_key.strip():
        print("OPENAI_API_KEY not set — skip LLM calls; samples loaded:", len(samples))
        for s in samples:
            print(f"  - {s['id']} ({s['marketplace']} {s.get('rating')}★)")
        return 0

    from app.services.llm import ToneProfileInput, generate_replies

    tone = ToneProfileInput(description="Вежливо, от имени бренда, лаконично")
    def _check(sample: dict, variants: list[str]) -> list[str]:
        expect = sample.get("expect") or {}
        errs: list[str] = []
        if not variants:
            return ["no variants"]
        for i, v in enumerate(variants):
            if expect.get("min_len") and len(v) < int(expect["min_len"]):
                errs.append(f"v{i+1} too short ({len(v)})")
            if expect.get("max_len") and len(v) > int(expect["max_len"]):
                errs.append(f"v{i+1} too long ({len(v)})")
            for word in expect.get("forbidden") or []:
                if word.lower() in v.lower():
                    errs.append(f"v{i+1} forbidden {word!r}")
        return errs

    ok = 0
    for s in samples:
        text = (s.get("text") or "").strip() or "Оценка без текста"
        try:
            variants = await generate_replies(
                text,
                s.get("rating"),
                tone,
                product_context=s.get("product") or "Товар",
            )
            errs = _check(s, variants)
            if errs:
                print(f"WARN {s['id']}: {', '.join(errs)}")
            else:
                print(f"OK {s['id']}: {len(variants)} variant(s)")
            ok += 1
        except Exception as exc:
            print(f"FAIL {s['id']}: {exc}")
    print(f"Done {ok}/{len(samples)}")
    return 0 if ok == len(samples) else 2


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
