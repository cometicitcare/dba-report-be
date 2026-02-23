# Buddhist Affairs MIS Dashboard — Backend API

FastAPI backend for the Buddhist Affairs Department Management Information System Dashboard.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI 0.129 |
| Database | PostgreSQL (asyncpg + SQLAlchemy 2) |
| Auth | JWT (python-jose) |
| Server | Uvicorn |
| Config | pydantic-settings |

---

## Quick Start (Local Development)

### 1. Prerequisites

- Python 3.11+
- PostgreSQL database (local or remote)
- `pip`

### 2. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your database credentials and choose a strong SECRET_KEY
```

Minimum required settings in `.env`:
```
DB_HOST=...
DB_PORT=5432
DB_NAME=...
DB_USER=...
DB_PASSWORD=...
SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
AUTH_USERNAME=report_admin
AUTH_PASSWORD=Report@Admin2024
```

### 4. Run database migrations / views

```bash
python run_migration.py
```

### 5. Start the server

```bash
python run.py
# or
uvicorn app.main:app --reload --port 8000
```

API is available at: `http://localhost:8000`  
Interactive docs: `http://localhost:8000/docs`

---

## Authentication

All API routes (except `/api/v1/auth/login`) require a valid Bearer JWT token.

### Login

```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=report_admin&password=Report@Admin2024
```

Response:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 28800
}
```

### Use the token

```http
GET /api/v1/section1
Authorization: Bearer eyJ...
```

Tokens expire after **8 hours** (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`).

---

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | `Buddhist Affairs MIS Dashboard` | Application display name |
| `DEBUG` | `false` | Enable debug mode |
| `DB_HOST` | `127.0.0.1` | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_NAME` | `pglocal` | Database name |
| `DB_USER` | `postgres` | Database user |
| `DB_PASSWORD` | — | Database password |
| `DATABASE_URL_OVERRIDE` | — | Full async DB URL (overrides individual fields) |
| `CORS_ORIGINS` | `http://localhost:3000,...` | Comma-separated allowed frontend origins |
| `AUTH_USERNAME` | `report_admin` | Dashboard login username |
| `AUTH_PASSWORD` | — | Dashboard login password |
| `SECRET_KEY` | **CHANGE ME** | JWT signing secret (min 32 chars) |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `480` | Token lifetime in minutes |

---

## Deploy to Railway

### Steps

1. **Create a new Railway project** and connect your Git repo  
   (deploy from the `backend/` directory, or set the root directory to `backend/`).

2. **Set environment variables** in Railway → Variables tab:

   | Variable | Value |
   |----------|-------|
   | `DB_HOST` | your Railway/external DB host |
   | `DB_PORT` | your DB port |
   | `DB_NAME` | your DB name |
   | `DB_USER` | your DB user |
   | `DB_PASSWORD` | your DB password |
   | `CORS_ORIGINS` | `https://YOUR-FRONTEND.up.railway.app` |
   | `AUTH_USERNAME` | `report_admin` |
   | `AUTH_PASSWORD` | your chosen password |
   | `SECRET_KEY` | strong random 32+ char string |
   | `ACCESS_TOKEN_EXPIRE_MINUTES` | `480` |
   | `DEBUG` | `false` |

   > **Tip:** If you attach a Railway PostgreSQL plugin, they inject `DATABASE_URL`  
   > automatically. Rename it to `DATABASE_URL_OVERRIDE` in the app config to use it.

3. Railway auto-detects Python via Nixpacks and uses `Procfile` as the start command:
   ```
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

4. After deploy, confirm health at: `https://YOUR-BACKEND.up.railway.app/`

---

## Project Structure

```
backend/
├── app/
│   ├── main.py          # FastAPI app, CORS, router registration
│   ├── config.py        # Settings loaded from .env
│   ├── database.py      # Async SQLAlchemy engine
│   ├── models/          # SQLAlchemy ORM models
│   ├── routers/
│   │   ├── auth.py      # Login endpoint + JWT dependency
│   │   ├── dashboard.py
│   │   ├── section1.py … section3.py
│   │   ├── temples.py
│   │   ├── lookups.py
│   │   └── persons.py
│   ├── schemas/         # Pydantic response schemas
│   └── services/        # Business logic
├── migrations/
│   └── create_views.sql # Materialized views / DB setup
├── requirements.txt
├── Procfile             # Railway start command
├── railway.json         # Railway deployment config
├── .env                 # Local secrets (git-ignored)
└── .env.example         # Template — safe to commit
```

---

## Security Notes

- `.env` is **git-ignored** — never commit it.
- In production, rotate `SECRET_KEY` and `AUTH_PASSWORD` regularly.
- The login endpoint uses credential comparison against env vars — no database required.
- All other API endpoints validate JWT on every request.
