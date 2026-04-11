#!/usr/bin/env python3
"""Bump the package version and sync test assertions."""

import subprocess
import sys
import tomllib

bump = sys.argv[1] if len(sys.argv) > 1 else "patch"
if bump not in ("patch", "minor"):
    print(f"Unknown bump type '{bump}'. Use 'patch' or 'minor'.")
    sys.exit(1)

with open("pyproject.toml", "rb") as f:
    current = tomllib.load(f)["project"]["version"]

parts = current.split(".")
if bump == "minor":
    parts[1] = str(int(parts[1]) + 1)
    parts[2] = "0"
else:
    parts[2] = str(int(parts[2]) + 1)
tag = ".".join(parts)

print(f"Bumping {bump}: {current} -> {tag}")

for path in ("pyproject.toml", "tests/test_cli.py"):
    with open(path) as f:
        content = f.read()
    with open(path, "w") as f:
        f.write(content.replace(current, tag))

subprocess.run(["pip", "install", "-e", ".", "-q"], check=True)
print("Done. Run 'tg --version' to verify.")
