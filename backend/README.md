# 💸 CashCtrl API

CashCtrl is a production-grade personal finance tracker and P2P lending platform built with **FastAPI**, **SQLAlchemy 2.0**, and **Celery**. 

The application bridges the gap between individual finance management and social credit, featuring a unique **Vouch Score** system and an intelligent notification layer.

---

## ✨ Features

### 💹 Advanced Analytics & Reporting
- **Financial Health Audit**: Real-time snapshot of savings rates, emergency funds, and budget adherence.
- **Data Export**: Professional data portability with CSV and JSON export endpoints (`/api/v1/data/export/`).
- **FIRE Insights**: Predictive modeling for financial independence.

### 🤝 P2P Lending & Social
- **Trusted Connections**: Discover and connect with known contacts via a social discovery layer.
- **Lending Lifecycle**: Formalize loan requests, agreements, and repayments with automated installment tracking.
- **Vouch Score**: A dynamic social credit score reflecting reliability as a borrower or lender.
- **Persistence & Notifications**: Real-time alerts for loan requests, connection invites, and overdue payments.

### 🛡️ Production Hardening
- **Observability**: Structured JSON logging and custom tracing middleware.
- **Security**: 
  - Rate Limiting via `slowapi` (Redis-backed).
  - Multi-Factor Authentication (MFA) via TOTP.
  - JWT-based Auth with `fastapi-users`.
- **Database Stability**: Standardized for **Neon PostgreSQL** with intelligent URL parsing and disabled statement caching for pooling compatibility.
- **Background Workers**: Celery-based processing for recurring transactions, interest calculations, and overdue alerts.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.12, FastAPI
- **Database**: PostgreSQL (Production) / SQLite (Development)
- **Task Queue**: Celery with Redis
- **Migrations**: Alembic (Timezone-aware timestamps)
- **Environment**: Managed via `uv`

---

## 🚀 Quick Start

### 1. Installation
```bash
# Clone and enter
git clone <repository-url>
cd cash-ctrl

# Setup environment
uv venv
uv sync
```

### 2. Configuration
Create a `.env` file based on `.env.example`:
```env
ENVIRONMENT=dev # or 'prod'
DEV_DATABASE_URL=sqlite+aiosqlite:///./cashctrl.db
PROD_DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=...
```

### 3. Database Initialization
```bash
# Rebuild local database with the latest schema
uv run alembic upgrade head
```

### 4. Running the Application
The application uses a smart entry point `run.py` to handle environment switching.

```bash
# Development Mode (Defaults to local SQLite)
uv run run.py

# Production Mode (Forces Neon/PostgreSQL)
uv run run.py --prod
```

### 5. Services
```bash
# Celery Worker (New Terminal)
uv run celery -A app.worker.celery_app worker --loglevel=info solo
```
```pwsh
# Celery Beat (New Terminal)
uv run celery -A app.worker.celery_app beat --loglevel=info
```

---

## 🧪 Testing
```bash
uv run pytest
```

---

## 🗺️ Roadmap & Design
1.  **Service Pattern**: Business logic is centralized in `app/services/` (e.g., `P2PService`, `NotificationService`).
2.  **Notification Engine**: Decoupled events ensure users stay informed without blocking API response times.
3.  **Auditability**: Every transaction and loan event is tracked with timezone-aware precision.

---

## 📄 License
MIT License. See [LICENSE](LICENSE) for details.
