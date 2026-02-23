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

