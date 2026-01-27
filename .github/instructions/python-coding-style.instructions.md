---
applyTo: "**/*.py"
---

# Python Coding Style Instructions (Best Practices)

These instructions guide GitHub Copilot when generating or editing Python code in this repository.

## Priority Order
1. Follow existing project conventions and configuration first (e.g., `pyproject.toml`, `.editorconfig`, linter/formatter configs, existing patterns in nearby files).
2. If no local convention exists, follow these instructions.
3. Prefer clarity and correctness over cleverness.

## Formatting & Layout
- Use **PEP 8** conventions as a baseline.
- Prefer an auto-formatter-compatible style (Black-like):
  - Use **4 spaces** per indentation level.
  - Prefer **implicit line wrapping** with parentheses/brackets/braces; avoid backslashes.
  - Keep lines reasonably short; if a repo configuration exists, obey it. Otherwise, target **88 characters** for code and **72 characters** for docstrings/comments.
- One statement per line; avoid compound statements like `if x: a(); b()`.
- Use blank lines to separate logical sections (imports, constants, types, functions/classes).

## Imports
- Group imports in this order, separated by a blank line:
  1) standard library
  2) third-party
  3) local application
- Prefer absolute imports unless the local package structure strongly benefits from explicit relative imports.
- Avoid wildcard imports (`from x import *`).

## Naming
- Modules/files: `lower_snake_case.py`
- Packages: `lower_snake_case`
- Classes/exceptions: `CapWords`, exceptions end with `Error` when appropriate
- Functions/variables: `lower_snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Use `self` / `cls` conventions.
- Avoid ambiguous single-letter names (except short-lived indices like `i`, `j` inside tight loops).

## Types & Interfaces
- Prefer explicit, readable interfaces:
  - Add type hints for public functions/methods and non-trivial internal ones.
  - Use modern typing (`list[str]`, `dict[str, int]`) when Python version allows.
  - Use `Optional[T]`/`T | None` correctly: distinguish `None` from falsy values.
- Prefer `Protocol`/duck typing where it improves testability and avoids tight coupling.
- Prefer small, cohesive data structures:
  - Use `@dataclass(frozen=True)` for value objects.
  - Use `@dataclass` for simple records; keep validation near construction.

## Docstrings & Comments
- Follow **PEP 257** conventions:
  - Use triple double quotes for docstrings.
  - First line: imperative summary ending with a period.
  - For multi-line docstrings: summary line, blank line, then details.
- Write docstrings for public modules, classes, functions, and methods.
- Comments should explain **why**, constraints, or non-obvious tradeoffs—not restate the code.

## Error Handling
- Catch specific exceptions; avoid bare `except:`.
- Keep `try` blocks minimal; place only the statements that can raise the expected exception inside them.
- Prefer raising domain-specific exceptions (custom exception classes) when it improves caller ergonomics.
- Preserve context with exception chaining when helpful: `raise NewError(...) from err`.

## Control Flow
- Prefer guard clauses and early returns to reduce nesting.
- Prefer `is None` / `is not None` for `None` checks.
- Prefer `match`/`case` (Python 3.10+) or dictionary dispatch for multi-branch logic when clearer.

## Functions & Classes
- Keep functions small and single-purpose; split if they:
  - exceed ~30–40 logical lines,
  - have many branches,
  - require extensive comments to follow.
- Keep classes cohesive:
  - Prefer composition over inheritance.
  - Make state private-by-convention (leading underscore) unless it is part of a stable public API.
  - Avoid exposing mutable internals; return copies/iterators when appropriate.

## Decorators
- Use decorators for cross-cutting concerns (logging, caching, retries, access control), not core business logic.
- Keep decorator behavior explicit and minimal; avoid surprising side effects.
- Preserve function metadata with `functools.wraps`.
- Prefer parameterized decorators when you need configuration.
- Keep decorator stacks short and ordered by intent (outermost runs last).
- Avoid decorators that change the return type unless clearly documented.

## Collections & Mutability
- Prefer iterables/generators for streaming behavior.
- Avoid mutating inputs unless clearly documented.
- When returning collections, prefer immutable views/tuples where it reduces accidental mutation.

## Concurrency (When Relevant)
- Prefer `async`/`await` with explicit boundaries; avoid mixing sync/async layers.
- Use context managers (`with`, `async with`) for resource safety.

## Tooling Defaults (If Repo Has No Preference)
- Formatting: Black
- Linting: Ruff (ruleset aligned with PEP 8 + import sorting)
- Type checking: MyPy or Pyright
- Tests: Pytest

## Performance & Security
- Do not micro-optimize prematurely; prefer correct and clear code.
- Use `pathlib` over manual path concatenation.
- Validate and sanitize external inputs (files, env vars, user input).
- Avoid `eval`/`exec`.
- Prefer parameterized queries and safe APIs when dealing with databases.

## Output Expectations For Copilot
- Generate code that is idiomatic, testable, and consistent with nearby files.
- If requirements are ambiguous, ask a clarifying question rather than guessing.

---

## References
- https://peps.python.org/pep-0008/
- https://peps.python.org/pep-0257/
