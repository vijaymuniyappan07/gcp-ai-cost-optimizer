# Coding Policy for GCP AI Cost Optimizer

This document outlines the coding standards and practices for the GCP AI Cost Optimizer project. The primary development methodology is **Test-Driven Development (TDD)**.

---

## 1. Test-Driven Development (TDD)

- **Write tests before code**: For every new feature or bugfix, write a failing test first.
- **Red-Green-Refactor**:
  1. **Red**: Write a test that fails.
  2. **Green**: Write the minimum code to make the test pass.
  3. **Refactor**: Clean up code and tests, ensuring all tests still pass.
- **Test coverage**: Aim for high coverage, especially for business logic, API endpoints, and utility functions.
- **Test types**:
  - **Unit tests**: For individual functions, classes, and modules.
  - **Integration tests**: For API endpoints and service interactions.
  - **End-to-end tests**: For critical user flows (optional, but recommended).

---

## 2. Code Style & Quality

- **Language**: Python 3.9+.
- **Style guide**: Follow [PEP 8](https://peps.python.org/pep-0008/) for Python code.
- **Linting**: Use `flake8` or `pylint` for static analysis.
- **Formatting**: Use `black` for automatic code formatting.
- **Type hints**: Use type annotations and [PEP 484](https://peps.python.org/pep-0484/) type hints throughout the codebase.
- **Imports**: Organize imports using `isort`.

---

## 3. Documentation

- **Docstrings**: All public modules, classes, and functions must have docstrings (PEP 257).
- **README**: Keep project-level documentation up to date.
- **Inline comments**: Use sparingly, only where code is non-obvious.

---

## 4. Version Control

- **Commits**: Write clear, descriptive commit messages.
- **Branching**: Use feature branches for new features and bugfixes.
- **Pull Requests**: All code must be reviewed before merging to main.

---

## 5. Testing Tools

- **Testing framework**: Use `pytest` for all Python tests.
- **Mocking**: Use `unittest.mock` or `pytest-mock` for mocking dependencies.
- **Continuous Integration**: Run tests and linters on every push and pull request (e.g., GitHub Actions).

---

## 6. Security & Secrets

- **Secrets**: Never commit secrets or credentials. Use `.env` files and environment variables.
- **Dependencies**: Keep dependencies up to date and monitor for vulnerabilities.

---

## 7. Code Review

- **Peer review**: All code must be reviewed by at least one other contributor.
- **Checklist**:
  - Tests written and passing
  - Code style and formatting
  - Documentation updated
  - No secrets or sensitive data committed

---

## 8. Example TDD Workflow

1. Write a failing test for a new API endpoint in `tests/`.
2. Implement the endpoint in `backend/app/api/`.
3. Run tests and ensure the new test passes.
4. Refactor code for clarity and maintainability.
5. Commit and push changes.

---

**By following this policy, we ensure high code quality, maintainability, and reliability for the GCP AI Cost Optimizer project.**
