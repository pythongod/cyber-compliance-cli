#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

if len(sys.argv) != 2:
    print("Usage: scripts/bump_version.py <new-version>")
    raise SystemExit(1)

new_version = sys.argv[1].strip()
if not re.match(r"^\d+\.\d+\.\d+$", new_version):
    print("Version must match X.Y.Z")
    raise SystemExit(1)

pyproject = Path("pyproject.toml")
text = pyproject.read_text(encoding="utf-8")
text2 = re.sub(r'version = "[0-9]+\.[0-9]+\.[0-9]+"', f'version = "{new_version}"', text)
if text == text2:
    print("No version field updated")
    raise SystemExit(1)
pyproject.write_text(text2, encoding="utf-8")

changelog = Path("CHANGELOG.md")
if not changelog.exists():
    changelog.write_text("# Changelog\n\n", encoding="utf-8")

old = changelog.read_text(encoding="utf-8")
entry = f"## v{new_version}\n\n- TODO: summarize release changes\n\n"
if entry not in old:
    changelog.write_text(old + entry, encoding="utf-8")

print(f"Bumped to {new_version}")
