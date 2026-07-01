# FPT Software Coding Standards

## Python Standards (Python 3.10+)

### Type Hints (REQUIRED)
- All function parameters and return types must have type hints
- Use Python 3.10+ syntax: `def func(x: str) -> int:` instead of `typing.Optional`
- Use `str | None` instead of `Optional[str]`
- Use `list[str]` instead of `List[str]` (no need to import from typing)

### Docstrings (REQUIRED)
- All public functions, classes, and modules must have docstrings
- Use Google style docstrings:
  ```python
  def calculate(x: int, y: int) -> int:
      """Calculate the sum of two integers.
      
      Args:
          x: First integer.
          y: Second integer.
          
      Returns:
          The sum of x and y.
          
      Raises:
          TypeError: If x or y are not integers.
      """
  ```

### PEP 8 Compliance
- Maximum line length: 120 characters
- Use 4 spaces for indentation (never tabs)
- Imports: stdlib → third-party → local, each group separated by blank line

## Security Standards (CRITICAL)

### NEVER Use These Patterns
1. **`subprocess.run(cmd, shell=True)`** — Command injection vulnerability. Always use `subprocess.run(args_list, shell=False)` with argument list.
2. **`eval(user_input)`** — Arbitrary code execution vulnerability. Use `ast.literal_eval()` for safe evaluation or proper parsers.
3. **`hashlib.md5(password)`** — Weak hashing for passwords. Use `bcrypt.hashpw()` with salt rounds >= 12, or `argon2id`.
4. **String concatenation in SQL queries** — SQL injection. Always use parameterized queries.
5. **Hardcoded secrets** — Use environment variables or secret management tools.

### Input Validation (REQUIRED)
- Validate type, range, and format at every entry point
- Use Pydantic models for schema validation
- Sanitize all user inputs before processing
- Never trust client-side validation alone

## Error Handling Standards
- Always use `try/except` with specific exceptions (never bare `except:`)
- Log errors with full context using structured logging
- Provide meaningful error messages (no raw stack traces to users)
- Use custom exception classes for domain-specific errors

## Testing Standards
- Minimum 80% code coverage
- Unit tests for all public methods
- Integration tests for API endpoints
- Test files named `test_<module>.py` in `tests/` directory
- Use `unittest` framework (Python standard library)
