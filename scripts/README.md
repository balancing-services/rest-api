# Release Automation Scripts

This directory contains automation scripts to simplify the release process for the Balancing Services REST API.

## Version Management

The version is stored in **one place only**: `openapi.yaml`. The Python client's `pyproject.toml` is generated from `pyproject.toml.draft` which contains an invalid TOML placeholder (`version = __VERSION__`) that prevents accidental publishing without proper generation. The Claude Code plugin manifest (`.claude-plugin/plugin.json`) carries a copy of the version because the manifest format requires a literal value; `bump-version.sh` stamps it from `openapi.yaml`.

## Scripts

### `bump-version.sh`

Bumps the version number in `openapi.yaml`, stamps it into `.claude-plugin/plugin.json`, and updates `CHANGELOG.md`.

**Usage:**
```bash
./scripts/bump-version.sh <version>
```

**Example:**
```bash
./scripts/bump-version.sh 1.2.0
```

**What it does:**
- Updates `openapi.yaml` (info.version field) - **single source of truth**
- Updates `.claude-plugin/plugin.json` (version field) to match
- Adds new version section to `CHANGELOG.md` with current date
- Shows next steps for committing and publishing

**Next steps after running:**
1. Review changes: `git diff`
2. Edit `CHANGELOG.md` to add release notes under the new version
3. Commit: `git add -A && git commit -m "Bump version to X.Y.Z"`
4. Run quality checks: `./clients/python/check.sh`
5. Publish: `cd clients/python && ./test-and-publish.sh`
