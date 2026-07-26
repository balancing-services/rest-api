#!/bin/bash

# Script to generate Python client from OpenAPI specification
# Uses uvx to run openapi-python-client without installing it

set -e

# Navigate to the script directory
cd "$(dirname "$0")"

# Check if OpenAPI spec exists
if [ ! -f "../../openapi.yaml" ]; then
    echo "Error: OpenAPI spec not found at ../../openapi.yaml"
    exit 1
fi

# Check if uvx is available
if ! command -v uvx &> /dev/null; then
    echo "Error: uvx is not installed. Please install uv first:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check if git working directory is clean (warning only)
if command -v git &> /dev/null && git rev-parse --git-dir > /dev/null 2>&1; then
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        echo "Warning: Git working directory has uncommitted changes"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Generation cancelled"
            exit 1
        fi
    fi
fi

# Remove existing generated code (if any)
if [ -d "balancing_services" ]; then
    echo "Removing existing generated code..."
    rm -rf balancing_services
fi

# Generate the client
echo "Generating Python client from OpenAPI spec..."
# Pin the generator version so regeneration is reproducible: an unpinned uvx
# silently upgrades to whatever is latest, which can churn the generated output
# (formatting, type shapes) independently of any spec change. Bump deliberately.
uvx openapi-python-client@0.29.0 generate \
    --path ../../openapi.yaml \
    --config config.yaml \
    --meta none

echo "Making literal-enum validators mypy-version-independent..."
python3 fix_enum_validator_casts.py

echo "Fixing types with Ruff..."
# Pin ruff (see config.yaml post_hooks) so generation is reproducible: an
# unpinned `uvx ruff` upgrades to whatever is latest and churns the output.
uvx ruff@0.16.0 check --fix balancing_services --exit-zero --quiet || true

# --- Python 3.10 compatibility shim ------------------------------------------
# openapi-python-client (>= 0.24) generates `datetime.datetime.fromisoformat()`
# for date-time fields. On Python 3.10 that call cannot parse the RFC3339 "Z"
# UTC suffix the API returns (e.g. 2025-01-01T00:00:00Z) — `fromisoformat()`
# only learned to accept "Z" in Python 3.11. Normalize the trailing "Z" to
# "+00:00" before parsing so the client keeps working on Python 3.10.
#
# This is no longer needed once we drop Python 3.10 support (planned for the
# next major version): delete this block then and the generated calls work
# as-is. The matching guard test lives in tests/test_datetime_compat.py.
echo "Patching datetime parsing for Python 3.10 compatibility..."
find balancing_services -name '*.py' -exec sed -i -E \
  -e 's/datetime\.datetime\.fromisoformat\(d\.pop\(("[^"]+")\)\)/datetime.datetime.fromisoformat(d.pop(\1).replace("Z", "+00:00"))/g' \
  -e 's/datetime\.datetime\.fromisoformat\(data\)/datetime.datetime.fromisoformat(data.replace("Z", "+00:00"))/g' \
  {} +

echo "Client generation complete!"
echo "Generated code is in: balancing_services/"
