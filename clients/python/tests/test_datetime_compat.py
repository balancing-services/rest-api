"""
Guards the Python 3.10 datetime-parsing shim applied by generate.sh.

openapi-python-client emits ``datetime.datetime.fromisoformat(...)`` for
date-time fields, which on Python 3.10 cannot parse the RFC3339 "Z" UTC suffix
the API returns (fixed in 3.11). generate.sh rewrites those calls to normalize
"Z" -> "+00:00". These tests fail if a regeneration drops that shim.

Remove together with the generate.sh shim once we drop Python 3.10 support
(the next major version).
"""

from datetime import timedelta
from pathlib import Path

from balancing_services import models
from balancing_services.models import Period


def test_period_parses_z_suffixed_timestamps():
    """A 'Z' UTC timestamp deserializes to an aware UTC datetime.

    On Python 3.10 this fails without the shim, since ``fromisoformat`` rejects
    the trailing 'Z'.
    """
    period = Period.from_dict({"startAt": "2025-01-01T00:00:00Z", "endAt": "2025-01-01T01:00:00Z"})
    assert period.start_at.utcoffset() == timedelta(0)
    assert period.end_at.utcoffset() == timedelta(0)


def test_generated_datetime_parsing_is_py310_safe():
    """Every generated ``fromisoformat()`` call normalizes the trailing 'Z'.

    This is the only check that catches a dropped shim on Python 3.11+, where the
    underlying parsing bug is invisible.
    """
    models_dir = Path(models.__file__).parent
    offenders = [
        f"{path.name}:{lineno}: {line.strip()}"
        for path in sorted(models_dir.glob("*.py"))
        for lineno, line in enumerate(path.read_text().splitlines(), start=1)
        if "fromisoformat(" in line and '.replace("Z", "+00:00")' not in line
    ]
    assert not offenders, "un-normalized fromisoformat() calls found:\n" + "\n".join(offenders)
