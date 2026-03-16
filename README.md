# CashCtrl Backend - Enterprise Financial Ecosystem

CashCtrl is a high-performance, secure, and mathematically precise financial backend built for modern personal and enterprise finance management. It follows industry standards such as **SOLID**, **ACID**, and **DRY**, ensuring a robust foundation for P2P lending, group expense management, and predictive analytics.

---

## 🚀 Vision & Objectives

CashCtrl aims to become the definitive open-source financial ledger, providing:

- **Financial Integrity**: Double-entry bookkeeping concepts and atomic transactions.
- **AI Intelligence**: Automated transaction entry from physical receipts.
- **Group Versatility**: Unequal split logic for complex social financial scenarios.
- **Developer First**: Clean, documented APIs with full Docker/K8s orchestration support.

---

## 🛠 Tech Stack

- **Framework**: Django 6.0 + Django REST Framework (DRF)
- **Database**: PostgreSQL (Production) / SQLite (Development)
- **Authentication**: `django-allauth` + JWT (JSON Web Tokens)
- **Task Queue**: Celery + Redis (for background jobs like PDF generation)
- **AI/Vision**: Pytesseract + Pillow for Receipt OCR
- **Documentation**: OpenAPI 3.0 via `drf-spectacular`
- **Orchestration**: Docker & Kubernetes (Helm-ready manifests)

---

## ✨ Key Features

### 1. Account & Transaction Core

- **Multi-currency Support**: Intelligent exchange rate engine for global usage.
- **Categorization**: Multi-level hierarchical categories for granular tracking.
- **Audit Trails**: Immutable logs for every sensitive financial state change.

### 2. P2P Lending Engine

- **Loan Lifecycle**: Request -> Approval -> Disbursement -> Repayment.
- **Amortization**: Automatic generation of monthly installments with interest calculation.
- **Hardened Validation**: Borrowers must be KYC-verified before requesting credit.

### 3. Split Payment Engine (The Splitter)

- **Group Context**: Shared expenses within groups.
- **Mathematically Diverse**: Supports **Equal**, **Percentage-based**, and **Fixed-amount** splits.
- **Settlement Ledger**: Real-time "who-owes-who" calculations.

### 4. AI Perception (Vision)

- **Receipt Scanning**: Upload a photo of a receipt, and the system extracts the Amount, Merchant, and Date automatically using OCR.

### 5. Analytics & Forecasting

- **Predictive Spending**: Analysis of historical data to forecast future cash flow.
- **Detailed Reports**: Export your financial health to PDF/CSV.

---

## 🏃 Setup & Installation

### Local Development

1. **Clone the repository**:

   ```bash
   git clone <repo-url>
   cd cash-ctrl-backend
   ```

2. **Initialize Environment**:

   ```bash
   uv venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   uv sync
   ```

3. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and fill in your database and API keys.

4. **Run Migrations**:

   ```bash
   py manage.py migrate
   ```

5. **Start the Unified Entry Point**:

   ```bash
   py main.py --env dev --start-services
   ```

### High-Scale Testing

To seed the database with 500 users and 50,000 transactions for stress testing:

```bash
py manage.py seed_data
```

### Docker (Production Setup)

The stack is fully containerized with Nginx and Gunicorn.

```bash
docker-compose up --build
```

### Kubernetes Orchestration

Manifests are available in the `k8s/` directory for deploying to a cluster.

```bash
kubectl apply -f k8s/config.yaml
kubectl apply -f k8s/db.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/web.yaml
kubectl apply -f k8s/worker.yaml
```

---

## 📁 Project Structure

- `app/`: Project configuration, settings, and middleware.
- `users/`: Custom User model and authentication logic.
- `accounts/`: Balance tracking and currency management.
- `transactions/`: Core ledger and Receipt Scanning logic.
- `lending/`: P2P Loan management.
- `splits/`: Group expense engine.
- `integrations/`: Third-party SDKs (Truecaller, Cashfree, Setu).
- `audit/`: Immutable system activity logs.

---

## 📜 Git & Contributions

We follow the **Conventional Commits** specification. Please ensure every commit follows the format:
`feat(component): description` or `fix(component): description`.

## 🛡 Security

- **Throttling**: Rate limits on sensitive endpoints.
- **Scanning**: OCR temp files are automatically purged after processing.
- **Bcrypt Hashing**: Secure password storage by default.

---

Built with ❤️ by Subhanu Majumder
