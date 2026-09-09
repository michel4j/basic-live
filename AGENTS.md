# Agent Instructions

## Agent skills

### Issue tracker

GitHub Issues via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Canonical 5-role triage vocabulary. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout (`CONTEXT.md` and `docs/adr/` at repo root). See `docs/agents/domain.md`.


## Environment Setup and Execution

* **Activation:** Run `poetry env activate` within the project directory to activate the environment.
* **Dependency Installation:** Run `poetry install` to set up or sync the environment.
* **Preferred Invocation:** Always run commands prefixing them with `poetry run` (e.g., `poetry run pytest`, `poetry run python main.py`).
* **Do Not Use:** Avoid `poetry shell` because non-interactive agents cannot properly manage subshell sessions.
* **Environment Path Inspection:** Use `poetry env info --path` if an absolute path to the virtual environment python interpreter is required.

## Commands
- Run the test suite: `poetry run python -m unittest `
- Run a specific test file: `poetry run python -m unittest tests/test_xxx.py`