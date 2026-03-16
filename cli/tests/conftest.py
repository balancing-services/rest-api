"""Shared test fixtures."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class StubResponse:
    status_code: int
    headers: dict[str, str] = field(default_factory=dict)
    parsed: Any = None
    content: bytes = b""
