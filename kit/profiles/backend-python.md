---
title: Backend Python profile
summary: Python additions to the backend profile: python_version frontmatter, pytest and ruff checks, Python VS Code extensions.
keywords: [python, fastapi, django, backend, api]
status: confirmed
updated: 2026-11-11
extends: backend
---

# Profile: backend-python

Extends `backend`. Everything not listed here comes from `backend`.

## Extra frontmatter
package, endpoint, service, env (local/staging/prod), python_version, framework (fastapi/django/flask/other)

## Budgets
Code: max 400 lines per .py file. Docs: default budgets.

## Never do
- Install packages globally; use a virtual environment and record it in the README.
- Add a dependency without noting it in the requirements file.
- Commit .venv or credentials.

## DONE means
Handler implemented, `pytest` passes, `ruff check` is clean, documented, migration reversible or noted.

## Wrap-up additions
Record python version, new dependencies, env vars added, and the real output of `pytest` and `ruff check`.

## VS Code
### Extensions
- ms-python.python: Python language support
- ms-python.vscode-pylance: type checking and completion
- charliermarsh.ruff: lint and format
### Settings
- `"python.analysis.typeCheckingMode": "basic"`
- `"[python]": { "editor.formatOnSave": true }`
