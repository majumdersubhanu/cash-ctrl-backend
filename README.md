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

CashCtrl is a high-performance, secure, and highly scalable financial backend built for modern personal and enterprise
finance management. It rigorously adheres to industry standards such as **SOLID**, **ACID**, and **DRY**, ensuring an
immutable and robust foundation for P2P lending, complex group expense management, and predictive analytics.

---

## 🚀 Vision & Ecosystem

CashCtrl aims to serve as the definitive open-source financial ledger API, abstracting away the immense complexity of
multi-actor financial states.

- **Financial Integrity**: Double-entry bookkeeping concepts, atomic transactions, and an immutable audit trail.
- **AI Intelligence**: Automated transaction entry from physical receipts via Pytesseract Vision integration.
- **Group Versatility**: The "Splitter" engine supports unequal, percentage-based, and exact-amount splits for complex
  social financial scenarios.
- **Observability Built-in**: Real-time monitoring of task queues and system health via a professional observability
  stack.
- **Developer First**: Clean, heavily documented APIs featuring OpenAPI 3.0 via `drf-spectacular`, with out-of-the-box
  Docker/K8s orchestration support.

---

## 🛠 Tech Stack

- **Core Framework**: Django 6.0 + Django REST Framework (DRF)
- **Database**: PostgreSQL (Production) / Redis (Cache & Queue)
- **Authentication**: Phone (OTP) + Google OAuth2 + JWT
- **Observability**: Prometheus, Grafana, Flower
- **Asynchronous Task Queue**: Celery + Redis
- **AI/Vision Integration**: Pytesseract + Pillow for Receipt OCR Parsing
- **API Documentation**: OpenAPI 3.0 via `drf-spectacular` (Swagger/Redoc)
- **Environment**: Docker, Kubernetes, Google Cloud Platform (GCP)

---

## ✨ Enterprise Features

### 1. Account & Transaction Core

- **Multi-currency Support**: Intelligent exchange rate engine automatically bridging global usage.
- **Hierarchical Categorization**: Multi-level categories for highly granular tracking.
- **Audit Trails**: Immutable, system-level logs tracking every sensitive financial state change.

### 2. P2P Lending Engine

- **Lifecycle Management**: Request -> Approval -> Disbursement -> Repayment.
- **Amortization Schedules**: Automatic generation of monthly installments with precise interest calculation.
- **Verification Gates**: Borrowers must complete KYC verification before interacting with the credit engine.

### 3. Split Payment Engine (The Splitter)

- **Group Contexts**: Dedicated shard for maintaining shared expenses within a specific group.
- **Mathematical Diversity**: Safely processes **Equal**, **Percentage-based**, and **Fixed-amount** splits with zero
  drift.
- **Settlement Ledger**: Real-time "who-owes-who" calculations with automated resolution paths.

### 4. Hardened Multi-Method Authentication

- **Phone Auth**: Secure OTP-based registration and login via mobile verification.
- **Google OAuth**: One-tap social login integrated via `django-allauth`.
- **DualAuth Backend**: Custom authentication backend allowing login via Email OR Phone Number.

### 5. Advanced Monitoring & Observability

- **Flower**: Real-time monitoring and management of Celery distributed task queues.
- **Prometheus**: High-fidelity metric collection for application performance and resource utilization.
- **Grafana**: Professionally curated dashboards for visualizing system health and transaction velocity.

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
   uv sync
   ```

3. **Configure Environment Variables**:

   Copy `.env.example` to `.env.dev` and tailor your database and social auth keys.

4. **Run Migrations & Seed Data**:

   ```bash
   python manage.py migrate
   python manage.py seed_data
   ```

5. **Start the Unified Entry Point**:

   ```bash
   python main.py --env dev --start-services
   ```

### Docker (Production Setup)

The stack is fully containerized inside a multi-stage, Linux-secure Dockerfile running Gunicorn behind Nginx.
`docker-compose` spins up Redis, Celery Workers, Prometheus, Grafana, and Flower automatically.

```bash
docker compose up --build -d
```

### Google Cloud Deployment

CashCtrl is optimized for GCP deployment via Cloud Run and Cloud SQL.
See [DEPLOYMENT.md](DEPLOYMENT.md) for the full
orchestration guide.

---

## 📖 API Documentation

The REST API is strictly typed and documented using the OpenAPI 3.0 specification.

- **Swagger UI**: `http://localhost:8000/api/docs/`
- **ReDoc**: `http://localhost:8000/api/redoc/`

---

## 📜 Git & Contributions

We strictly follow **Conventional Commits** and maintain a forensic-grade git history.
See [CONTRIBUTING.md](CONTRIBUTING.md) for setup and PR
guidelines.

---

<p align="center">Built with ❤️ by Subhanu Majumder</p>
