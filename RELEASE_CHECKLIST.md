# Release Checklist (CLI)

## One-time GitHub/PyPI setup

1. Create PyPI project: `cyber-compliance-cli`.
2. In GitHub repo settings, create environment: `pypi`.
3. Restrict environment to tags matching `v*.*.*`.
4. In PyPI trusted publishing, add this GitHub repo/workflow:
   - workflow: `.github/workflows/publish-pypi.yml`
   - environment: `pypi`

## Per-release flow

1. Ensure tests pass locally:
   ```bash
   pytest -q
   ```
2. Bump version + changelog seed:
   ```bash
   python scripts/bump_version.py X.Y.Z
   ```
3. Update `CHANGELOG.md` entry content.
4. Commit:
   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "Release vX.Y.Z"
   git push
   ```
5. Tag + push tag:
   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```
6. Verify workflows:
   - GitHub Release workflow success
   - Publish to PyPI workflow success

## Rollback note

If a bad release is tagged, publish a fixed patch version (`X.Y.(Z+1)`).
Do not delete published PyPI versions.
