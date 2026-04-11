# Publishing Setup Guide

This project uses **OIDC Trusted Publishing** — no API tokens or secrets needed. GitHub Actions authenticates directly with PyPI/Test PyPI via short-lived tokens. You need to wire up three things: GitHub Environments, a Trusted Publisher on Test PyPI, and a Trusted Publisher on PyPI.

## How the workflows fire

| Event | Workflow job | Publishes to |
|-------|-------------|--------------|
| Push a `v*` tag | `test-pypi` job in `publish.yml` | test.pypi.org |
| Create a GitHub Release | `publish` job in `publish.yml` | pypi.org |

The `test.yml` CI workflow runs on every push to `main` and PRs but does **not** publish anywhere.

---

## Step 1 — GitHub: Create two Environments

Go to: **github.com/greyhoundforty/tengingarstjori → Settings → Environments**

### Environment: `test-pypi`
1. Click **New environment**, name it `test-pypi`
2. No protection rules needed (fires automatically on tag push)
3. No secrets or variables needed (Trusted Publishing handles auth)
4. Click **Save protection rules**

### Environment: `pypi`
1. Click **New environment**, name it `pypi`
2. Recommended: enable **Required reviewers**, add yourself
   - This gives you a manual gate before anything hits production PyPI
3. No secrets or variables needed
4. Click **Save protection rules**

---

## Step 2 — Test PyPI: Configure Trusted Publisher

> Your project already exists at https://test.pypi.org/project/tengingarstjori

1. Log in to **test.pypi.org**
2. Go to your project → **Manage** → **Publishing**
3. Under *Trusted Publishers*, click **Add a new publisher**
4. Fill in:

   | Field | Value |
   |-------|-------|
   | PyPI Project Name | `tengingarstjori` |
   | Owner | `greyhoundforty` |
   | Repository name | `tengingarstjori` |
   | Workflow filename | `publish.yml` |
   | Environment name | `test-pypi` |

5. Click **Add**

---

## Step 3 — PyPI: Create project and configure Trusted Publisher

> The project does not yet exist on production pypi.org. You must create it via a "pending publisher" before the first upload.

1. Log in to **pypi.org**
2. Go to **Your account → Publishing** (top-right menu)
3. Under *Add a new pending publisher*, fill in:

   | Field | Value |
   |-------|-------|
   | PyPI Project Name | `tengingarstjori` |
   | Owner | `greyhoundforty` |
   | Repository name | `tengingarstjori` |
   | Workflow filename | `publish.yml` |
   | Environment name | `pypi` |

4. Click **Add**

> A *pending publisher* lets PyPI create the project automatically on first upload. You do not need to pre-create it.

---

## Step 4 — Publish to Test PyPI

Once Steps 1–2 are done:

```bash
git tag v0.2.2
git push origin v0.2.2
```

This triggers the `test-pypi` job. Watch it at:
**github.com/greyhoundforty/tengingarstjori/actions**

After ~2 minutes, verify the new version at:
**https://test.pypi.org/project/tengingarstjori/**

Install and smoke-test it:
```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ tengingarstjori==0.2.2
tg --help
```

---

## Step 5 — Publish to PyPI (production)

Once Step 3 is done and Test PyPI looks good:

1. Go to **github.com/greyhoundforty/tengingarstjori/releases**
2. Click **Draft a new release**
3. Choose tag `v0.2.2` from the dropdown
4. Set release title, e.g. `v0.2.2 — New commands and workflow tools`
5. Add release notes (GitHub can auto-generate from commits)
6. Click **Publish release**

This triggers the `publish` job. If you added a required reviewer to the `pypi` environment, you will get an email to approve the deployment before it runs.

After ~3 minutes, verify at:
**https://pypi.org/project/tengingarstjori/**

---

## No API tokens required

This setup uses OIDC Trusted Publishing throughout. The workflow already has:

```yaml
permissions:
  id-token: write
```

and uses `pypa/gh-action-pypi-publish@release/v1` which handles the token exchange automatically. **Do not add `PYPI_API_TOKEN` or `TEST_PYPI_API_TOKEN` secrets** — they are not needed and would conflict.

---

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `invalid-publisher` | Environment name mismatch | Ensure the environment name in the workflow matches exactly what you entered on PyPI |
| `403 Forbidden` | Pending publisher not set up | Complete Step 3 before pushing a release |
| `File already exists` | Version already uploaded | Bump version in `pyproject.toml`, commit, retag |
| Deployment stuck "Waiting" | Required reviewer gate | Go to Actions → approve the pending deployment |
| `attestations: true` fails | Old PyPI project predates attestation support | Set `attestations: false` in `publish.yml` as a workaround |
