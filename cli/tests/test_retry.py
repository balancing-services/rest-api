"""Tests for the retry wrapper (HTTP 429 handling)."""

from __future__ import annotations

import pytest
from conftest import StubResponse

from balancing_services_cli.retry import (
    DEFAULT_RETRY_AFTER,
    EXIT_CODE_RATE_LIMITED,
    call_with_retry,
    parse_retry_after,
)

# ── parse_retry_after tests ──────────────────────────────────────────────


def test_parse_retry_after_integer():
    assert parse_retry_after("5") == 5.0


def test_parse_retry_after_zero():
    assert parse_retry_after("0") == 0.0


def test_parse_retry_after_none():
    assert parse_retry_after(None) == DEFAULT_RETRY_AFTER


def test_parse_retry_after_invalid():
    assert parse_retry_after("not-a-number") == DEFAULT_RETRY_AFTER


def test_parse_retry_after_empty_string():
    assert parse_retry_after("") == DEFAULT_RETRY_AFTER


def test_parse_retry_after_negative_integer():
    """Negative values should be clamped to 0."""
    assert parse_retry_after("-5") == 0.0


# ── call_with_retry tests ────────────────────────────────────────────────


def test_no_retry_on_success():
    """200 response is returned immediately without retries."""
    call_count = 0

    def fetch_fn(**kwargs):
        nonlocal call_count
        call_count += 1
        return StubResponse(status_code=200, parsed="ok")

    result = call_with_retry(fetch_fn, _sleep=lambda _: None)
    assert result.status_code == 200
    assert result.parsed == "ok"
    assert call_count == 1


def test_retry_on_429_then_success():
    """429 followed by 200 should retry and return success."""
    call_count = 0

    def fetch_fn(**kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return StubResponse(status_code=429, headers={"Retry-After": "1"})
        return StubResponse(status_code=200, parsed="ok")

    result = call_with_retry(fetch_fn, _sleep=lambda _: None)
    assert result.status_code == 200
    assert call_count == 2


def test_429_without_retry_after_uses_default():
    """429 without Retry-After header should use DEFAULT_RETRY_AFTER."""
    sleep_values = []

    def fetch_fn(**kwargs):
        return StubResponse(status_code=429, headers={})

    with pytest.raises(SystemExit) as exc_info:
        call_with_retry(fetch_fn, max_retries=1, _sleep=lambda s: sleep_values.append(s))

    assert exc_info.value.code == EXIT_CODE_RATE_LIMITED
    assert sleep_values == [DEFAULT_RETRY_AFTER]


def test_retries_exhausted_exits_with_code_29():
    """After max_retries, should exit with EXIT_CODE_RATE_LIMITED."""
    call_count = 0

    def fetch_fn(**kwargs):
        nonlocal call_count
        call_count += 1
        return StubResponse(status_code=429, headers={"Retry-After": "1"})

    with pytest.raises(SystemExit) as exc_info:
        call_with_retry(fetch_fn, max_retries=3, _sleep=lambda _: None)

    assert exc_info.value.code == EXIT_CODE_RATE_LIMITED
    assert call_count == 4  # 1 initial + 3 retries


def test_invalid_retry_after_falls_back_to_default():
    """Invalid Retry-After value should use DEFAULT_RETRY_AFTER."""
    sleep_values = []
    call_count = 0

    def fetch_fn(**kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return StubResponse(status_code=429, headers={"Retry-After": "garbage"})
        return StubResponse(status_code=200, parsed="ok")

    result = call_with_retry(fetch_fn, _sleep=lambda s: sleep_values.append(s))
    assert result.status_code == 200
    assert sleep_values == [DEFAULT_RETRY_AFTER]


def test_stderr_output_contains_retry_message(capsys):
    """Stderr should contain a user-facing rate limit message."""
    call_count = 0

    def fetch_fn(**kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return StubResponse(status_code=429, headers={"Retry-After": "2"})
        return StubResponse(status_code=200, parsed="ok")

    call_with_retry(fetch_fn, _sleep=lambda _: None)
    captured = capsys.readouterr()
    assert "Rate limited" in captured.err
    assert "429" in captured.err
    assert "attempt 1/3" in captured.err


def test_non_429_error_not_retried():
    """Non-429 errors (e.g. 500) should be returned immediately without retry."""
    call_count = 0

    def fetch_fn(**kwargs):
        nonlocal call_count
        call_count += 1
        return StubResponse(status_code=500, content=b"Internal Server Error")

    result = call_with_retry(fetch_fn, _sleep=lambda _: None)
    assert result.status_code == 500
    assert call_count == 1


def test_kwargs_forwarded():
    """Keyword arguments should be forwarded to fetch_fn."""
    received_kwargs = {}

    def fetch_fn(**kwargs):
        received_kwargs.update(kwargs)
        return StubResponse(status_code=200)

    call_with_retry(fetch_fn, _sleep=lambda _: None, client="test-client", area="EE")
    assert received_kwargs["client"] == "test-client"
    assert received_kwargs["area"] == "EE"


def test_retries_exhausted_stderr_message(capsys):
    """Stderr should contain exhaustion message when retries are exhausted."""

    def fetch_fn(**kwargs):
        return StubResponse(status_code=429, headers={"Retry-After": "1"})

    with pytest.raises(SystemExit) as exc_info:
        call_with_retry(fetch_fn, max_retries=2, _sleep=lambda _: None)

    assert exc_info.value.code == EXIT_CODE_RATE_LIMITED
    captured = capsys.readouterr()
    assert "exhausted" in captured.err.lower()


def test_exit_code_constant():
    """EXIT_CODE_RATE_LIMITED should be 29 (mnemonic for 429)."""
    assert EXIT_CODE_RATE_LIMITED == 29
