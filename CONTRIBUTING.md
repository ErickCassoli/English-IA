# Contributing to English IA

Thanks for helping build a local-first English coaching backend!

## Development workflow

1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt -r requirements-dev.txt
   pre-commit install
   ```
3. Run the API locally with:
   ```bash
   uvicorn app.main:app --reload
   ```
4. Before sending a pull request, ensure the quality gates pass:
   ```bash
   ruff check .
   bandit -r app
   pytest
   ```

## Commit style

Use Conventional Commits (e.g., `feat(api): add session finish endpoint`). Squash merges are fine, but avoid force pushes to shared branches.

## Reporting issues

Open an issue with steps to reproduce and expected vs. actual behaviour. Security concerns should follow the instructions in `SECURITY.md`.
