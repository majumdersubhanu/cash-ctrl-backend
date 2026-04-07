# ☁️ Google Cloud Deployment Guide

This document provides a professional blueprint for deploying the CashCtrl ecosystem to **Google Cloud Platform (GCP)**,
ensuring high availability, security, and scalability.

## 🏗 High-Level Architecture

* **Compute**: [Google Cloud Run](https://cloud.google.com/run) (Serverless containers for API and Workers).
* **Database**: [Cloud SQL for PostgreSQL](https://cloud.google.com/sql/docs/postgres) (Managed relational database).
* **Cache & Message Broker**: [Memorystore for Redis](https://cloud.google.com/memorystore/docs/redis) (Managed Redis).
* **Static & Media Assets**: [Google Cloud Storage](https://cloud.google.com/storage) (Bucket-level persistence).
* **Secret Management**: [Secret Manager](https://cloud.google.com/secret-manager).
* **CI/CD**: [Cloud Build](https://cloud.google.com/build).

---

## 🛠 Step-by-Step Deployment

### 1. Infrastructure Provisioning

#### **Cloud SQL (PostgreSQL)**

1. Enable the Cloud SQL Admin API.
2. Create a PostgreSQL instance (v16+).
3. Create a database named `cashctrl`.
4. Create a user and generate a secure password.

#### **Memorystore (Redis)**

1. Create a Redis instance.
2. Note the **Primary Endpoint** IP (e.g., `10.x.x.x`).

#### **Cloud Storage**

1. Create a bucket for static/media files (e.g., `cash-ctrl-assets`).
2. Set appropriate IAM permissions for the bucket.

---

### 2. Secret Management

Create secrets in **Secret Manager** for sensitive environment variables:

* `CASH_CTRL_SECRET_KEY`
* `CASH_CTRL_DATABASE_URL` (format: `postgres://USER:PASSWORD@/DB_NAME?host=/cloudsql/PROJECT_ID:REGION:INSTANCE_ID`)
* `CASH_CTRL_REDIS_URL`
* `GOOGLE_OAUTH_CLIENT_ID`
* `GOOGLE_OAUTH_CLIENT_SECRET`

---

### 3. Containerization & Cloud Build

CashCtrl utilizes `cloudbuild.yaml` for automated deployment.

```yaml
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/cash-ctrl-web', '.']

  # Push to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/cash-ctrl-web']

  # Deploy to Cloud Run (Web)
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'cash-ctrl-api'
      - '--image'
      - 'gcr.io/$PROJECT_ID/cash-ctrl-web'
      - '--region'
      - 'us-central1'
      - '--set-env-vars'
      - 'DEBUG=False'
```

---

### 4. Running Migrations

Execute migrations on Cloud Run using a temporary job:

```bash
gcloud run jobs create cash-ctrl-migrate \
    --image gcr.io/$PROJECT_ID/cash-ctrl-web \
    --command "python" \
    --args "manage.py,migrate" \
    --region us-central1
```

---

## 🔒 Security Posture

1. **VPC Connector**: Ensure Cloud Run services are connected to a VPC to communicate with Memorystore and Cloud SQL via
   private IPs.
2. **IAM Roles**: Use a custom Service Account with minimal permissions (`Cloud SQL Client`,
   `Secret Manager Secret Accessor`).
3. **HTTPS**: Cloud Run provides managed SSL certificates by default.

---

Built with ❤️ for Google Cloud Platform
