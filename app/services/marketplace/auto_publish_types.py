from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

AutoPublishStatus = Literal["skipped", "published", "llm_failed", "api_failed"]


@dataclass(frozen=True, slots=True)
class AutoPublishOutcome:
    status: AutoPublishStatus
    reply_preview: str | None = None
