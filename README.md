<!-- markdownlint-disable MD033 -->
<!-- markdownlint-disable MD041 -->

<div align="center">
  <h1>💰 CashCtrl Backend</h1>
  <p><em>World-class, AI-Powered, and Mathematically Precise Financial Engine</em></p>

  <a href="https://github.com/subhanu/cash-ctrl-backend/actions"><img src="https://img.shields.io/badge/build-passing-brightgreen?style=flat-square" alt="Build Status"></a>
  <a href="https://www.djangoproject.com/"><img src="https://img.shields.io/badge/django-6.0.3-092E20?style=flat-square&logo=django" alt="Django Version"></a>
  <a href="https://www.django-rest-framework.org/"><img src="https://img.shields.io/badge/drf-3.16.1-red?style=flat-square" alt="DRF Version"></a>
  <a href="https://www.docker.com/"><img src="https://img.shields.io/badge/docker-ready-2496ED?style=flat-square&logo=docker" alt="Docker"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
</div>

<br />

CashCtrl is a high-performance, secure, and highly scalable financial backend built for modern personal and enterprise finance management. It rigorously adheres to industry standards such as **SOLID**, **ACID**, and **DRY**, ensuring an immutable and robust foundation for P2P lending, complex group expense management, and predictive analytics.

---

## 🚀 Vision & Ecosystem

CashCtrl aims to serve as the definitive open-source financial ledger API, abstracting away the immense complexity of multi-actor financial states.

- **Financial Integrity**: Double-entry bookkeeping concepts, atomic transactions, and an immutable audit trail.
- **AI Intelligence**: Automated transaction entry from physical receipts via Pytesseract Vision integration.
- **Group Versatility**: The "Splitter" engine supports unequal, percentage-based, and exact-amount splits for complex social financial scenarios.
- **Developer First**: Clean, heavily documented APIs featuring OpenAPI 3.0 via `drf-spectacular`, with out-of-the-box Docker/K8s orchestration support.

---

## 🛠 Tech Stack

- **Core Framework**: Django 6.0 + Django REST Framework (DRF)
- **Database**: PostgreSQL (Production) / SQLite (Development)
- **Authentication**: `django-allauth` + JWT (JSON Web Tokens)
- **Asynchronous Task Queue**: Celery + Redis (for background jobs, PDF generation, bulk processing)
- **AI/Vision Integration**: Pytesseract + Pillow for Receipt OCR Parsing
- **API Documentation**: OpenAPI 3.0 via `drf-spectacular` (Swagger/Redoc UI)
- **Deployment & Orchestration**: Docker, Docker Compose, Kubernetes (Helm-ready manifests)

---

## ✨ Enterprise Features

### 1. Account & Transaction Core

- **Multi-currency Support**: Intelligent exchange rate engine automatically bridging global usage.
- **Hierarchical Categorization**: Multi-level categories for highly granular tracking.
- **Audit Trails**: Immutable, system-level logs tracking every sensitive financial state change in the database.

### 2. P2P Lending Engine

- **Lifecycle Management**: Request -> Approval -> Disbursement -> Repayment.
- **Amortization Schedules**: Automatic generation of monthly installments with precise interest calculation.
- **Hardened Validation**: Borrowers must complete KYC verification before interacting with the credit system.

### 3. Split Payment Engine (The Splitter)

- **Group Contexts**: Dedicated shard for maintaining shared expenses within a specific group.
- **Mathematical Diversity**: Safely processes **Equal**, **Percentage-based**, and **Fixed-amount** splits with zero drift.
- **Settlement Ledger**: Real-time "who-owes-who" calculations with automated settlement resolution paths.

### 4. AI Perception (Vision Module)

- **Receipt Scanning**: Secure receipt photo upload workflow. The system extracts Amount, Merchant, and Date automatically using backend OCR. Temp files are securely expunged post-processing.

### 5. Analytics & Forecasting

- **Predictive Spending**: Time-series analysis of historical data to forecast future cash flow vectors.
- **Detailed Reports**: Automated financial health exports generated as asynchronous Celery tasks.

---

## 🏃 Setup & Installation

### Local Development (Native)

1. **Clone the repository**:

   ```bash
   git clone https://github.com/majumdersubhanu/cash-ctrl-backend
   cd cash-ctrl-backend
   ```

2. **Initialize Environment (using `uv`)**:

   ```bash
   uv venv
   # On Windows: .venv\Scripts\activate
   # On Linux/macOS: source .venv/bin/activate
   uv sync
   ```

3. **Configure Environment Variables**:
   Copy `.env.example` to `.env.dev` and tailor your database keys.

4. **Run Migrations & Seed Data**:

   ```bash
   python manage.py migrate
   python manage.py seed_data  # Generates 5k Users & 500k Transactions
   ```

5. **Start the Unified Entry Point**:

   ```bash
   python main.py --env dev --start-services
   ```

### Docker (Production Setup)

The stack is fully containerized inside a multi-stage, Linux-secure Dockerfile running Gunicorn behind Nginx. `docker-compose` spins up Redis, Celery Workers, Celery Beat, PostgreSQL, and the Web container automatically.

```bash
docker compose up --build -d
```

### Kubernetes Orchestration

Manifests are actively maintained in the `k8s/` directory for rolling out to a production cluster.

```bash
kubectl apply -f k8s/config.yaml
kubectl apply -f k8s/db.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/web.yaml
kubectl apply -f k8s/worker.yaml
```

---

## 📁 Project Structure

- `app/`: Project configuration, core settings, Celery setup, and security middleware.
- `users/`: Custom User model, email-based auth, and the massive data seeder.
- `accounts/`: Balance tracking, account types, and currency management.
- `transactions/`: Core atomic ledger operations and Vision/Receipt OCR Parsing.
- `lending/`: P2P Loan request orchestration and amortization schedules.
- `splits/`: Multi-actor group expense mathematical engine.
- `analytics/`: Budgets, savings goals, and time-series forecasting logic.
- `recurring/`: Celery Beat crontab-driven scheduled transaction generation.
- `onboarding/`: Identity verification and compliance (KYC) workflows.
- `integrations/`: Third-party API wrappers (Truecaller, Cashfree, Setu).
- `audit/`: The immovable object: append-only system activity logs.
- `notifications/`: User alerting and WebSocket/Email hook targets.

---

## 📖 API Documentation

The REST API is strictly typed and documented using the OpenAPI 3.0 specification.
When the server is running, you can interact with the endpoints through the beautiful, autogenerated UI interfaces:

- **Swagger UI**: `http://localhost:8000/api/docs/`
- **ReDoc**: `http://localhost:8000/api/redoc/`

---

## 📜 Git & Contributions

We strictly follow the **Conventional Commits** specification. Please ensure every commit follows the format:

- `feat(component): description`
- `fix(component): description`
- `perf(component): description`
- `docs(component): description`

## 🛡 Security Hardening

- **Throttling**: DRF rate limits on sensitive authentication and transaction mutating endpoints.
- **Scanning Contexts**: OCR payloads exist strictly in-memory or temporary encrypted volumes and are immediately purged.
- **Bcrypt Hashing**: Immutable Secure password storage by default.
- **Connection Pools**: Managed psycopg2 persistent connection pools handling ultra-high concurrency safely (`CONN_MAX_AGE`).

---

<p align="center">Built with ❤️ by Subhanu Majumder</p>
