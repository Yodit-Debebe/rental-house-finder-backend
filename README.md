# Rental House Finder — Backend

Backend for a rental house finder platform, built as a **modular monolith**
using Domain-Driven Design and Hexagonal Architecture.

> **Status: in development.** The foundation (architecture, configuration,
> database, tests, CI) is complete, and the `identity` module is implemented:
> registration, login with token authentication, and a current-user endpoint.
> The remaining modules (property management, landlord, tenant, AI search)
> are still scaffolding.

## Tech stack

| Layer | Technology |
|---|---|
| Framework | Django 6.1 |
| API | Django REST Framework 3.18 (token authentication) |
| Database | PostgreSQL 16 via psycopg 3 |
| Config | `python-dotenv` (`.env` file) |
| Architecture | DDD + Hexagonal + Modular Monolith — see [ARCHITECTURE.md](ARCHITECTURE.md) |

## Project structure

```
config/                Project settings, root URL router, WSGI/ASGI entry points
manage.py              Django CLI (runserver, migrate, test, shell...)
identity/              Users, roles, authentication — implemented
property_management/   Rental property listings — scaffolding
landlord/              Landlord-side features — scaffolding
administration/        Back-office / admin features — scaffolding
tenant/                Tenant-side features — scaffolding
ai_search/             AI-powered search — scaffolding
shared/                Code used by 2+ modules (API helpers, base types, exceptions)
infrastructure/        Shared technical adapters (database, keycloak, kafka, storage)
ARCHITECTURE.md        Architecture rules — read this before adding code
docker-compose.yml     Local PostgreSQL for development
```

Inside every app, code follows the dependency rule
`interfaces → application → domain ← infrastructure`, organized as
`domain/`, `application/`, `infrastructure/` and `interfaces/`
(full rules in [ARCHITECTURE.md](ARCHITECTURE.md)).

## Getting started

### Prerequisites

- Python 3.12+
- Docker (optional — only if you don't already have PostgreSQL)
- Git

### 1. Clone and install

```bash
git clone https://github.com/Yodit-Debebe/rental-house-finder-backend.git
cd rental-house-finder-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set at least `DJANGO_SECRET_KEY` (generate one with):

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

| Variable | Purpose | Example |
|---|---|---|
| `DJANGO_SECRET_KEY` | Signs sessions/tokens — required, app refuses to start without it | random 50-char string |
| `DJANGO_DEBUG` | `True` only in development | `True` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hostnames the app may serve | `localhost,127.0.0.1` |
| `DJANGO_EMAIL_BACKEND` | Dev prints emails to the console | `django.core.mail.backends.console.EmailBackend` |
| `DB_NAME` / `DB_USER` / `DB_PASSWORD` / `DB_HOST` / `DB_PORT` | PostgreSQL connection | see `.env.example` |

### 3. Database — pick one option

**Option A: Docker (recommended for new team members)**

```bash
docker compose up -d
# then set DB_PASSWORD=change-me in .env to match docker-compose.yml
```

> If a PostgreSQL already runs on port 5432 on your machine, either stop it
> for this project or change the port mapping in `docker-compose.yml`
> (e.g. `"5433:5432"`) and set `DB_PORT=5433` in `.env`.

**Option B: existing PostgreSQL**

```bash
createdb rental_house_finder   # credentials go in .env
```

### 4. Run

```bash
python manage.py check          # verify configuration
python manage.py migrate        # create tables
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/admin/ for the admin site. The API is served under
`http://127.0.0.1:8000/api/` (see below).

## API

Base path: `/api/`

| Method | Endpoint | Auth | Description | Success | Errors |
|---|---|---|---|---|---|
| POST | `/api/identity/register/` | public | Create an account | `201` user | `400` invalid input · `409` email taken |
| POST | `/api/identity/login/` | public | Obtain an auth token | `200` `{token, user}` | `401` bad credentials |
| GET | `/api/identity/me/` | token | Current user | `200` user | `401` missing/invalid token |

Authenticated requests send the token in a header:

```
Authorization: Token <token>
```

Registration accepts `role` values `tenant` (default) and `landlord`; admin
accounts can only be created through `createsuperuser` / the admin site.

### Example

```bash
# 1. Register (password: at least 8 characters)
curl -X POST http://127.0.0.1:8000/api/identity/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","full_name":"Your Name","password":"a-strong-password","role":"tenant"}'

# 2. Log in and copy the token from the response
curl -X POST http://127.0.0.1:8000/api/identity/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"a-strong-password"}'

# 3. Fetch the current user with the token
curl http://127.0.0.1:8000/api/identity/me/ \
  -H "Authorization: Token <token>"
```

## Tests and checks

```bash
python manage.py test           # run the test suite
python manage.py check          # Django system checks
lint-imports                    # enforce ARCHITECTURE.md dependency rules
```

All of these run automatically in CI (`.github/workflows/ci.yml`).

## Notes for developers

- Never commit `.env` — it is git-ignored. Only `.env.example` goes to git.
- Read [ARCHITECTURE.md](ARCHITECTURE.md) before adding a new module or
  reaching into another module's code.
- In development, outgoing emails are printed to the terminal, not sent.
