# FPT Software Secure-First Approach

## Overview
FleziPT enforces a **Secure-First approach** and Responsible AI compliance across all development activities. Security is not an afterthought — it is built into every phase of the SDLC.

## Password Hashing
- **NEVER use**: `hashlib.md5()`, `hashlib.sha1()` for passwords — these are cryptographically broken
- **ALWAYS use**: `bcrypt` with salt rounds >= 12, or `argon2id`
- Example:
  ```python
  import bcrypt
  
  def hash_password(password: str) -> str:
      """Hash password using bcrypt."""
      salt = bcrypt.gensalt(rounds=12)
      return bcrypt.hashpw(password.encode(), salt).decode()
  
  def verify_password(password: str, hashed: str) -> bool:
      """Verify password against bcrypt hash."""
      return bcrypt.checkpw(password.encode(), hashed.encode())
  ```

## Command Execution
- **NEVER use**: `subprocess.run(cmd, shell=True)` — allows command injection
- **ALWAYS use**: `subprocess.run(args_list, shell=False)` with argument list
- Validate and sanitize all inputs before passing to subprocess
- Example:
  ```python
  import subprocess
  
  def run_command(args: list[str]) -> str:
      """Safely execute a command with argument list."""
      result = subprocess.run(args, shell=False, capture_output=True, text=True)
      return result.stdout
  ```

## SQL Injection Prevention
- **NEVER use**: String concatenation or f-strings for SQL queries
- **ALWAYS use**: Parameterized queries with placeholders
- Example:
  ```python
  # WRONG: cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
  # RIGHT:
  cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
  ```

## Input Validation
- Validate type, range, format at every entry point
- Use Pydantic for schema validation
- Sanitize all user inputs before processing
- Never trust client-side validation alone

## Logging Security
- Never log sensitive data (passwords, tokens, PII, API keys)
- Use structured logging with JSON format
- Log security events (authentication failures, access denied, etc.)

## Dependency Security
- Pin all dependency versions in requirements.txt
- Run `safety audit` or `pip-audit` in CI/CD pipeline
- Keep dependencies up to date with security patches
- Review transitive dependencies for vulnerabilities
