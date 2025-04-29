# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Command Reference
- Run script: `osxphotos run find_photo_clusters.py --window "1 min" --album "Photo Clusters"`
- Package management: `uv pip install <package>` instead of `pip install <package>`
- Python linting: `ruff check *.py`
- Python formatting: `ruff format *.py`
- Type checking: `mypy *.py`

## Code Style
- Imports: Standard library first, third-party next, local imports last, alphabetized within sections
- Line length: 100 characters max
- Docstrings: Use triple double quotes with clear description, parameters, and return values
- Type hints: Use typing module annotations for function parameters and return values
- Error handling: Use try/except with specific exceptions, provide descriptive error messages
- Function naming: snake_case (lowercase with underscores)
- Variables: Descriptive, snake_case naming
- Avoid global variables
- Helper functions should have clear, focused purposes
- Input validation with descriptive error messages