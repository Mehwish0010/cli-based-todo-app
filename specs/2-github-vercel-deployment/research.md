# Research: GitHub and Vercel Deployment

**Feature**: 2-github-vercel-deployment
**Date**: 2026-01-02

## Decision 1: Web Framework Selection

**Context**: Need lightweight Python web framework compatible with Vercel serverless functions.

**Options Evaluated**:

| Framework | Pros | Cons | Verdict |
|-----------|------|------|---------|
| **Flask** | Simple, lightweight (~50KB), excellent Vercel support, minimal boilerplate | Less modern than FastAPI, manual typing | ✅ **SELECTED** |
| FastAPI | Modern, auto-docs, type hints, async | Heavier (~2MB), more complex for simple API | ❌ Rejected (overkill) |
| Django | Batteries included, admin panel | Very heavy (~8MB), overkill for demo | ❌ Rejected (too complex) |

**Decision**: Flask 3.0+
**Rationale**: Minimal overhead, proven Vercel compatibility, sufficient for demo API

## Decision 2: Python Version Compatibility

**Context**: Existing code uses Python 3.13; Vercel supports 3.9-3.11.

**Research**:
- Checked existing code for 3.13-specific features: None found
- Dependencies (datetime, dataclasses, enum) available in 3.11
- Vercel Python runtime: 3.9, 3.10, 3.11 officially supported

**Decision**: Target Python 3.11
**Verification**: Existing code fully compatible with 3.11
**Action**: Document 3.11+ requirement in README

## Decision 3: Frontend Approach

**Context**: Need web UI for Vercel deployment (CLI not web-accessible).

**Options Evaluated**:

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **Vanilla JS** | Zero dependencies, fast load, simple | Manual DOM manipulation | ✅ **SELECTED** |
| React | Component model, popular | Build step, framework overhead | ❌ Rejected (unnecessary) |
| Vue | Lightweight, reactive | Still requires build/CDN | ❌ Rejected (overkill) |

**Decision**: Single-page app with vanilla JavaScript + Fetch API
**Rationale**: Simple demo, no build complexity, instant load

## Decision 4: Deployment Configuration

**Context**: Configure Vercel for Python serverless functions.

**Research**:
- Vercel Python runtime uses WSGI server
- Supports Flask via `vercel.json` configuration
- Build command: `pip install -r requirements.txt`
- Entry point: `api/app.py` (must export Flask app)

**Decision**: Structure as Vercel Python serverless function
**Configuration**:
```json
{
  "version": 2,
  "builds": [
    { "src": "api/app.py", "use": "@vercel/python" }
  ],
  "routes": [
    { "src": "/api/(.*)", "dest": "api/app.py" },
    { "src": "/(.*)", "dest": "/static/$1" }
  ]
}
```

## Decision 5: State Management

**Context**: In-memory TodoStore won't persist across serverless function invocations.

**Options Evaluated**:

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **In-memory (demo mode)** | Zero setup, spec compliant | Resets on cold start | ✅ **SELECTED** |
| Add database | Persistent | Out of scope per spec | ❌ Rejected (future phase) |
| LocalStorage (client) | Survives reloads | Not multi-device | ⚠️ Optional enhancement |

**Decision**: Keep in-memory TodoStore with disclaimer
**Rationale**: Spec explicitly allows in-memory for demo; database is Phase III+
**Enhancement**: Optional client-side persistence via localStorage

## Decision 6: CI/CD Pipeline

**Context**: Need automated testing on pull requests.

**Decision**: GitHub Actions with Python 3.11 matrix
**Configuration**:
- Trigger: Pull request to main
- Jobs: Install deps → Run tests → Report results
- Fail PR if test success < 95%

**Workflow File**: `.github/workflows/test.yml`

## Decision 7: Documentation Structure

**Context**: Need comprehensive README for GitHub repository.

**Decision**: Single README.md with sections:
1. Project overview & features
2. Quick start (local setup)
3. Live demo link (Vercel URL)
4. Architecture overview
5. Development guide
6. Testing instructions
7. Contributing guide link
8. License

**Additional Files**:
- `LICENSE` - MIT license text
- `CONTRIBUTING.md` - SDD workflow, PR process
- `.github/ISSUE_TEMPLATE/` - Bug report, feature request

## Best Practices Applied

**Security**:
- No secrets in repository (FR-029)
- .gitignore excludes .env files
- Dependency pinning in requirements.txt

**Performance**:
- Static assets (CSS/JS) served directly by Vercel CDN
- API responses include Cache-Control headers
- Gzip compression enabled

**Maintainability**:
- Existing core logic unchanged (adapter pattern)
- Flask routes are thin wrappers
- Tests cover both CLI and API

## References

- Vercel Python documentation: https://vercel.com/docs/functions/runtimes/python
- Flask documentation: https://flask.palletsprojects.com/
- GitHub Actions Python: https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python
