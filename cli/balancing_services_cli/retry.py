"""Retry wrapper for handling HTTP 429 (rate limiting) responses."""

from __future__ import annotations

import logging
import sys
import time
from collections.abc import Callable
from typing import Any

log = logging.getLogger(__name__)

EXIT_CODE_RATE_LIMITED = 29
DEFAULT_RETRY_AFTER = 1.0


def parse_retry_after(value: str | None) -> float:
    """Parse a Retry-After header value (integer seconds) into a float.

    Returns DEFAULT_RETRY_AFTER if the value is missing or unparseable.
    """
    if value is None:
        return DEFAULT_RETRY_AFTER
    try:
        return max(0.0, float(int(value)))
    except ValueError:
        return DEFAULT_RETRY_AFTER


def call_with_retry(
    fetch_fn: Callable[..., Any],
    *,
    max_retries: int = 3,
    _sleep: Callable[[float], Any] = time.sleep,
    **kwargs: Any,
) -> Any:
    """Call fetch_fn with automatic retry on HTTP 429 responses.

    Args:
        fetch_fn: The API function to call.
        max_retries: Maximum number of retries on 429 responses.
        _sleep: Sleep function (injectable for testing).
        **kwargs: Arguments forwarded to fetch_fn.

    Returns:
        The response from fetch_fn on success or non-429 error.

    Raises:
        SystemExit: With EXIT_CODE_RATE_LIMITED (29) if retries are exhausted.
    """
    for attempt in range(max_retries + 1):
        response = fetch_fn(**kwargs)
        if response.status_code != 429:
            return response
        if attempt == max_retries:
            break
        retry_after = parse_retry_after(response.headers.get("Retry-After") if hasattr(response, "headers") else None)
        print(
            f"Rate limited (HTTP 429). Retrying in {retry_after:.0f}s (attempt {attempt + 1}/{max_retries})...",
            file=sys.stderr,
        )
        _sleep(retry_after)

    print(
        "Rate limit retries exhausted. Exiting with code 29.",
        file=sys.stderr,
    )
    raise SystemExit(EXIT_CODE_RATE_LIMITED)
