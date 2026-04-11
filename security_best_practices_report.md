# Security Best Practices Report — tengingarstjori

**Date:** 2026-04-11
**Version:** 0.2.2
**Language/Stack:** Python 3.10+, Click CLI, Pydantic, Rich

---

## Executive Summary

The codebase demonstrates solid security fundamentals: file permissions are set atomically with `os.open()`, SSH config injection is mitigated via Pydantic validators, and subprocess calls use list form (no shell injection). Two findings warrant attention before a PyPI release, and several tooling gaps should be closed. No critical vulnerabilities were found.

---

## Findings by Severity

### MEDIUM

#### M-01 — `ProxyCommand` via `extra_options` can execute arbitrary shell commands

**File:** `src/tengingarstjori/models.py:56–69`, `src/tengingarstjori/models.py:337–338`
**Impact:** If a user (or a tampered `connections.json`) sets `extra_options: {ProxyCommand: "/bin/bash -c ..."}`, SSH will execute that shell command every time the host is connected to via `tg connect`. Newline injection is blocked, but the SSH `ProxyCommand` directive accepts arbitrary commands on a single line.

The `extra_options` dict is written verbatim to the SSH config block:
```python
# models.py:337-338
for key, value in self.extra_options.items():
    lines.append(f"    {key} {value}")
```

**Recommendation:** Add a denylist (or allowlist) for dangerous SSH directives in `validate_extra_options`. At minimum, reject `ProxyCommand`, `LocalCommand`, `Match exec`, and `PermitLocalCommand`.

---

### LOW

#### L-01 — `StrictHostKeyChecking=no` in health check disables MITM protection

**File:** `src/tengingarstjori/cli.py:1828`

```python
"-o", "StrictHostKeyChecking=no",
```

This flag is passed unconditionally during `tg health`. It silently accepts any host key, defeating SSH's MITM protection for that check.

**Recommendation:** Remove this flag or make it opt-in (`--insecure`). The default should be `StrictHostKeyChecking=accept-new` at most, or omit the option entirely to respect the user's SSH config.

---

#### L-02 — Main SSH config rewrite uses `open()` instead of `os.open()` with mode

**File:** `src/tengingarstjori/config_manager.py:126`

```python
with open(self.main_ssh_config, "w") as f:
    f.write(new_content)
```

All other sensitive file writes use `os.open(..., 0o600)`, but `_ensure_include_line()` rewrites `~/.ssh/config` with plain `open()`. On existing files this preserves permissions, but if the file was somehow removed between the existence check (line 118) and this write, it would be created with the process umask instead of `0o600`.

**Recommendation:** Use the same `os.open` + `os.fdopen` pattern used in `_save_connections()` and `_update_ssh_config()`.

---

### INFORMATIONAL

#### I-01 — No dependency vulnerability scanning in the lint/CI pipeline

`bandit` is listed as an optional dev dependency and called in `mise run lint`, but there is no tool scanning the dependency graph for known CVEs. `rich`, `pydantic`, and `click` are low-risk but any PyPI release should have an automated check.

**Recommendation:** Add `pip-audit` to the `lint` or `dev` optional-dependencies group and to `mise run lint`.

#### I-02 — No secret/credential scanning before publish

No tool checks for accidentally committed secrets (API keys, tokens) in the git history or staged files before a PyPI push.

**Recommendation:** Add `gitleaks` or `trufflehog` as a pre-publish step.

#### I-03 — `bandit` not pinned as a hard dev dependency

`bandit` is referenced in `mise run lint` but is not in `pyproject.toml`'s `dev` or `lint` extras, making it optional and easy to skip.

**Recommendation:** Add `bandit>=1.7.0` to the `lint` extras in `pyproject.toml`.

---

## Recommended Local Tools to Add

| Tool | Purpose | Install |
|------|---------|---------|
| `pip-audit` | Scans installed deps for CVEs (PyPA official) | `pip install pip-audit` |
| `bandit` | SAST for Python (already used, needs pinning) | `pip install bandit` |
| `gitleaks` | Secret scanning in git history/staged files | `brew install gitleaks` |
| `semgrep` | Deep SAST with community Python rules | `pip install semgrep` |
| `ruff` | Fast linter (superset of flake8, has security rules) | `pip install ruff` |

For a PyPI release, **`pip-audit`** and **`gitleaks`** are the highest-value additions — they catch things `bandit` does not (supply-chain CVEs and credential leaks).

---

## Summary Table

| ID | Severity | File | Description |
|----|----------|------|-------------|
| M-01 | Medium | models.py:56-69, 337-338 | `ProxyCommand` allowed via `extra_options` |
| L-01 | Low | cli.py:1828 | `StrictHostKeyChecking=no` unconditional |
| L-02 | Low | config_manager.py:126 | SSH config rewrite uses bare `open()` |
| I-01 | Info | pyproject.toml | No CVE scanning for dependencies |
| I-02 | Info | — | No secret scanning pre-publish |
| I-03 | Info | pyproject.toml | `bandit` not in hard dev deps |
