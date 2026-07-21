# gcl_iam Agent Guide

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:

- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:

- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:

```text
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## Project layout

`gcl_iam/` is the distributable Python package. Core JWT, IAM-driver, policy,
and middleware code is kept in top-level modules such as `tokens.py`,
`drivers.py`, and `middlewares.py`; RESTAlchemy-facing components live in
`gcl_iam/api/`. Tests are colocated under `gcl_iam/tests/unit/` and
`gcl_iam/tests/functional/`. User documentation is mirrored in `docs/en/`,
`docs/ru/`, `docs/de/`, and `docs/zh/`; preserve equivalent structure and
examples when changing translated guides.

Project metadata and tool configuration are in `pyproject.toml`; tox commands
are defined in `tox.ini`. Dependency versions are locked in `uv.lock`.

## Setup, checks, and tests

Use Python 3.10+ and the uv-backed tox environments:

```bash
tox -e develop                 # create an editable development environment
tox -e py312                   # run the unit suite on Python 3.12
tox -e py312-functional        # run functional tests
tox -e ruff-check              # lint the repository
tox -e mypy                    # type-check gcl_iam
tox                             # run the configured matrix and coverage report
```

CI runs linting on Python 3.12 and both unit and functional suites across
Python 3.10–3.14. Run the narrowest relevant tox target locally before opening
a PR; run `tox -e ruff` only when intentional formatting changes are wanted,
as it rewrites files.

## Code Style and Naming Conventions

- **Language**: Python 3.10+
- **Formatter**: Ruff (format + linting)
- **Type Checking**: MyPy
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Tests**: Located in `gcl_iam/tests/unit` and `gcl_iam/tests/functional`
- **Comments for code**: write on english

## VCS Conventions

### Commit Message Format

```text
<type>(<scope>): <subject>

<body>

<footer>
```

**Example:**

```text
feat(repo): add HTTP server proxy driver

- Implement SimplePythonRepoDriver for file serving
- Add port configuration and error handling
- Include unit tests for driver lifecycle

Closes #123
```

### Pull Request Requirements

- **Title**: Use imperative, present tense: "Add feature", not "Added feature"
- **Description**: Clear summary of changes

## Additional Guidelines

### License

All source files must include Apache 2.0 license header:

```python
#    Copyright 2026 Genesis Corporation.
#    Licensed under the Apache License, Version 2.0 (the "License")
```