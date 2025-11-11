# Contributing to English IA

Thank you for helping build a collaborative English coaching platform! This document explains how to propose changes, run the toolchain locally, and ship production-ready pull requests.

## Branch Strategy

- Trunk-based development on `main`.
- Short-lived branches named after the work type and scope, for example:
  - `feat/chat-highlights`
  - `fix/quiz-json-regression`
  - `chore/bump-deps`
  - `docs/poml-guide`

## Conventional Commits

We follow [Conventional Commits](https://www.conventionalcommits.org/) to automate changelogs and releases.

Examples:

- `feat(chat): add highlights to correction payload`
- `fix(quiz): handle missing rationale field`
- `chore(ci): add coverage summary to job output`

## Local Development

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt -r requirements-dev.txt
   ```
2. Start the API:
   ```bash
   uvicorn app.main:app --reload
   ```
3. Run the optional Streamlit demo:
   ```bash
   streamlit run web/streamlit_app.py
   ```
4. Execute the quality gates locally:
   ```bash
   ruff check .
   ruff format --check .
   pytest --cov=app
   bandit -r app
   ```
5. Install pre-commit hooks before committing:
   ```bash
   pre-commit install
   ```

## Opening Issues and Pull Requests

- Use the templates in `.github/ISSUE_TEMPLATE` for new issues.
- Fork (or branch) and open PRs against `main`.
- Include tests for behavioral changes.
- Keep PRs focused; use checklists to show readiness.
- The PR template will remind you to describe testing, documentation, and release notes.

## Release Process

- Releases are automated by [release-please](https://github.com/googleapis/release-please) via `.github/workflows/release.yml`.
- Conventional Commit messages drive semantic versioning and changelog entries.
- Once a release PR is merged, GitHub tags and GitHub Releases are created automatically.
