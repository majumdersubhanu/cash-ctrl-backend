# Contributing to CashCtrl

Thank you for your interest in contributing to CashCtrl! We welcome all contributions, including bug reports, feature
requests, documentation improvements, and code patches.

## Tech Stack

* **Backend Framework**: Django 6.x & Django REST Framework
* **Database**: PostgreSQL
* **Caching & Queue**: Redis & Celery
* **Observability**: Flower, Prometheus, Grafana
* **Authentication**: Phone (OTP), Google OAuth2, Email/Password
* **Containerization**: Docker & Kubernetes
* **Code Quality**: Ruff (Linter & Formatter), Pytest (Testing)

## Getting Started Locally

### 1. Prerequisites

You need `uv` (the blazing fast Python package manager), `Docker`, and `Docker Compose` installed on your machine.

### 2. Setup

1. Fork and clone the repository.
2. Configure environmental variables at the root:

   ```bash
   cp .env.dev .env
   ```

3. Start the development environment containers:

   ```bash
   uv run docker compose up --build -d
   ```

4. Apply database migrations inside the running container:

   ```bash
   uv run docker compose exec web python manage.py migrate
   ```

## Development Workflow

### Branching

Always create a new branch for your work:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

### Commit Conventional

We strictly follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).

Format: `type(scope?): subject`

* `feat`: A new feature
* `fix`: A bug fix
* `docs`: Documentation only changes
* `chore`: Tooling, configs, or maintenance

### Testing & Linting

Before opening a Pull Request, ensure the codebase is clean and all tests pass. Our CI/CD pipeline will automatically
run these checks, but running them locally saves time!

```bash
# Lint & Format checks
uv run docker compose exec web ruff check .
uv run docker compose exec web ruff format . --check

# Run test suite with coverage
uv run docker compose exec web pytest --cov=.
```

## Opening a Pull Request

1. Keep the PR focused on a single responsibility.
2. Link any relevant GitHub Issues.
3. Write a clear, descriptive title and summarize the implementation details.
4. Ensure the UI/Doc swagger endpoints reflect your new APIs if you added any.

### 🛡️ Branch Protection & CI Gates

To merge a Pull Request into the main repository branch (`main` / `master`), the following strict merge gates must be satisfied:
- **Lint & Format**: The Ruff linter and formatter checks must pass cleanly.
- **Security Audit**: The `pip-audit` check must find **zero vulnerabilities** in project requirements.
- **Test Coverage**: All unit/integration tests must pass, and overall test coverage must be **at least 95%** (enforced by pytest-cov).

Welcome to the CashCtrl Core Contributor network!

