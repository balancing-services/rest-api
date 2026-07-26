#!/usr/bin/env python3
"""Post-process generated literal-enum validators to be mypy-version-independent.

openapi-python-client's literal_enums output generates, for each enum:

    def check_area(value: str) -> Area:
        if value in AREA_VALUES:
            return value
        raise TypeError(...)

The bare `return value` returns `str` where a `Literal[...]` is expected. mypy only accepts it
if it narrows `value` via the `value in AREA_VALUES` membership test — a feature added in mypy
2.x — so on mypy 1.x all 10 validators fail with [return-value]. Wrap the return in cast() so the
code type-checks on every mypy version. The project's mypy config sets neither
warn_redundant_casts nor warn_unused_ignores, so the cast is harmless on mypy 2.x where it is
technically redundant. Run from generate.sh after generation; `cast` is appended to the existing
`from typing import ...` line, which is already the ruff/isort canonical order (types before
lowercase names), so the output is stable regardless of the later ruff --fix pass.
"""
import pathlib
import re

MODELS = pathlib.Path(__file__).parent / "balancing_services" / "models"
CHECK_RE = re.compile(r"^def check_\w+\(value: str\) -> (\w+):$", re.M)

patched = []
for path in sorted(MODELS.glob("*.py")):
    src = path.read_text()
    m = CHECK_RE.search(src)
    if not m:
        continue
    type_name = m.group(1)
    if "return cast(" in src:
        continue  # already patched (idempotent)
    if not re.search(r"^from typing import .*\bcast\b", src, re.M):
        src = re.sub(
            r"^from typing import (.+)$",
            lambda mm: f"from typing import {mm.group(1)}, cast",
            src,
            count=1,
            flags=re.M,
        )
    new_src, n = re.subn(
        r"(\n    if value in \w+_VALUES:\n        )return value\n",
        rf"\g<1>return cast({type_name}, value)\n",
        src,
    )
    if n != 1:
        raise SystemExit(f"{path}: expected exactly one validator return, found {n}")
    path.write_text(new_src)
    patched.append(path.name)

print(f"Patched {len(patched)} literal-enum validator(s): {', '.join(patched)}")
