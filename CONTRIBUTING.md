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
2. Run the development environment initialization:

   ```bash
   uv venv
   uv pip install -r requirements.txt
   uv pip install -r requirements-test.txt
   ```

3. Set up your `.env.dev` file (You can copy `.env.example`).
4. Apply migrations and run the server:

   ```bash
   uv run python main.py --env dev
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
uv run ruff check .
uv run ruff format .
uv run pytest --cov=.
```

## Opening a Pull Request

1. Keep the PR focused on a single responsibility.
2. Link any relevant GitHub Issues.
3. Write a clear, descriptive title and summarize the implementation details.
4. Ensure the UI/Doc swagger endpoints reflect your new APIs if you added any.

Welcome to the CashCtrl Core Contributor network!
