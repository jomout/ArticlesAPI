# Articles API

A Django REST API for managing Articles with Authors, Tags, and Comments. It supports JWT authentication, robust filtering/search/ordering, pagination, and CSV export of articles. The project is containerized with Docker and ships with demo data and auto-created admin credentials for easy exploration.

## Implementation

- Article CRUD with ownership (only creator can update/delete)
- Comment CRUD with ownership (only author can update/delete)
- Authors and Tags are created/attached automatically from simple string arrays when creating/updating Articles
- Filtering, search, and ordering for Articles
  - Filter by year, month, author(s), tag(s), keyword (title/abstract)
  - Full-text style search on title and abstract via `?search=`
  - Ordering by `publication_date`, `created_at`, `identifier`, `title`
- Pagination (page size default 100; client-controlled up to 100)
- CSV export endpoint that respects filters or an explicit list of identifiers
- JWT authentication (access/refresh)
- Demo users and demo articles auto-loaded on startup

## Tech stack

- Python 3.12+/3.13 (container base)
- Django 5.2
- Django REST Framework 3.16
- django-filter
- djangorestframework-simplejwt (JWT)
- PostgreSQL
- Uvicorn (ASGI)
- Docker + docker compose

### Requirements

Requirements of the project are listed in `requirements.txt` and `pyproject.toml` file.

## Quickstart (Docker)

### Build and start the stack

```sh
docker compose up --build
```

This will:

- Start PostgreSQL
- Build and run the backend
- Apply migrations
- Create demo users and sample articles
- Create a superuser using environment variables
- Start Uvicorn at <http://localhost:8000>

### Visit the API and admin

- API root (DRF router): <http://localhost:8000/api/>
- Admin: <http://localhost:8000/admin/>

Default credentials are controlled via environment variables (see below). With the provided defaults in `docker-compose.yml`:

- Superuser: `admin` / `admin1234`
- Demo users: `demo_user1` / `demo_user1_1234`, `demo_user2` / `demo_user2_1234`

## Environment variables

The following are used by the stack (defaults shown from `docker-compose.yml`):

- Database
  - `POSTGRES_DB` (default `mydb`)
  - `POSTGRES_USER` (default `myuser`)
  - `POSTGRES_PASSWORD` (default `mypassword`)
  - `POSTGRES_HOST` (container internal, set to `db`)
  - `POSTGRES_PORT` (default `5432`)

- Django
  - `DJANGO_SECRET_KEY` (default `super-secret-key`)
  - `DJANGO_DEBUG` (default `1` / True)
  - `DJANGO_ALLOWED_HOSTS` (optional; defaults to `*` in settings if not provided)
  - Superuser bootstrap:
    - `DJANGO_SUPERUSER_USERNAME` (default `admin`)
    - `DJANGO_SUPERUSER_EMAIL` (default `admin@example.com`)
    - `DJANGO_SUPERUSER_PASSWORD` (default `admin1234`)

- Ports
  - `BACKEND_PORT` (default `8000` → host port)

## Data model

- `Author(id, name)`
- `Tag(id, name)`
- `Article(id, identifier, publication_date, title, abstract, created_by, created_at, updated_at)`
  - Explicit join tables:
    - `Authorship(article, author)` unique per pair
    - `ArticleTag(article, tag)` unique per pair
- `Comment(id, article, author, body, created_at, updated_at)`

Ownership rules:

- Articles: Only `created_by` can update/delete
- Comments: Only `author` can update/delete
- Unauthenticated users have read-only access

## Authentication (JWT)

- Obtain token: `POST /api/token/` with JSON `{ "username": "...", "password": "..." }`
- Refresh token: `POST /api/token/refresh/` with JSON `{ "refresh": "..." }`
- Use the `access` token in the Authorization header: `Authorization: Bearer <token>`

Example:

```sh
curl -sS -X POST http://localhost:8000/api/token/ \
  -H 'Content-Type: application/json' \
  -d '{"username": "demo_user1", "password": "demo_user1_1234"}'
```

Response:

```json
{ "access": "<jwt>", "refresh": "<jwt>" }
```

## Endpoints

Base path for resources: `/api/`

- Articles
  - `GET /api/articles/` list
  - `POST /api/articles/` create (auth required)
  - `GET /api/articles/{id}/` retrieve
  - `PUT/PATCH /api/articles/{id}/` update (owner only)
  - `DELETE /api/articles/{id}/` delete (owner only)
  - `GET /api/articles/export/` CSV export (see below)

- Comments
  - `GET /api/comments/` list
  - `POST /api/comments/` create (auth required)
  - `GET /api/comments/{id}/` retrieve
  - `PUT/PATCH /api/comments/{id}/` update (owner only)
  - `DELETE /api/comments/{id}/` delete (owner only)

- Reference data (read-only)
  - `GET /api/authors/`
  - `GET /api/tags/`

- Auth
  - `POST /api/token/`
  - `POST /api/token/refresh/`

## Creating and reading Articles

When creating/updating articles, pass authors/tags as simple string arrays; the API will create missing Authors/Tags and connect them via explicit join tables.

Example create:

```sh
ACCESS_TOKEN="$(curl -sS -X POST http://localhost:8000/api/token/ -H 'Content-Type: application/json' -d '{"username": "demo_user1", "password": "demo_user1_1234"}' | jq -r .access)"

curl -sS -X POST http://localhost:8000/api/articles/ \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H 'Content-Type: application/json' \
  -d '{
    "identifier": "ART-900001",
    "publication_date": "2025-01-15",
    "title": "Neural Nets in Practice",
    "abstract": "A practical guide.",
    "authors": ["Ada Lovelace", "Alan Turing"],
    "tags": ["AI", "ML"]
  }'
```

Response will expand details for authors and tags:

```json
{
  "id": 1,
  "identifier": "ART-900001",
  "publication_date": "2025-01-15",
  "title": "Neural Nets in Practice",
  "abstract": "A practical guide.",
  "authors_detail": [{"id": 1, "name": "Ada Lovelace"}, {"id": 2, "name": "Alan Turing"}],
  "tags_detail": [{"id": 1, "name": "AI"}, {"id": 2, "name": "ML"}],
  "created_by": "demo_user1",
  "created_at": "...",
  "updated_at": "..."
}
```

## Filtering, search, ordering, pagination

Available for `GET /api/articles/`:

- Filters
  - `year` (number): `?year=2024`
  - `month` (number): `?month=9`
  - `author` (comma-separated names): `?author=Ada%20Lovelace,Alan%20Turing`
  - `tag` (comma-separated names): `?tag=AI,ML`
  - `keyword` (string; matches title or abstract): `?keyword=neural`

- Search (DRF `SearchFilter`)
  - `?search=practical` (title, abstract)

- Ordering
  - `?ordering=publication_date` or `?ordering=-created_at` (prefix with `-` for descending)
  - Fields: `publication_date`, `created_at`, `identifier`, `title`

- Pagination
  - Page number: `?page=2`
  - Page size: `?page_size=50` (max 100)

Examples:

```sh
curl -sS 'http://localhost:8000/api/articles/?year=2025&tag=AI&ordering=-publication_date&page_size=10'
```

## CSV export

`GET /api/articles/export/` returns a CSV file with columns:

`identifier, publication_date, title, abstract, authors, tags`

It respects the same filters as the list endpoint, and you can also restrict by identifiers:

- By filters:

```sh
curl -sS -L 'http://localhost:8000/api/articles/export/?year=2024&tag=AI' -o articles.csv
```

- By a list of IDs:

```sh
curl -sS -L 'http://localhost:8000/api/articles/export/?ids=ART-000001,ART-000002' -o selected.csv
```

## Demo data and admin

On container startup, the entrypoint will:

- Run migrations
- Create demo users: `demo_user1`, `demo_user2`
- Load 150 sample articles (owned by `demo_user1` by default)
- Create a superuser from env vars

You can also run these manually inside the backend container:

```sh
# in another terminal
docker compose exec backend python manage.py load_demo_users
docker compose exec backend python manage.py load_demo_articles --count 200 --username demo_user2
```

## Local development (without Docker)

If you prefer running locally, you’ll need PostgreSQL and Python 3.12+.

```sh
# 1) Create and configure a virtualenv, install deps
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install django django-filter djangorestframework djangorestframework-simplejwt psycopg[binary] uvicorn

# 2) Set env vars for DB and Django
export POSTGRES_DB=mydb
export POSTGRES_USER=myuser
export POSTGRES_PASSWORD=mypassword
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export DJANGO_SECRET_KEY=dev-secret
export DJANGO_DEBUG=True

# 3) Apply migrations and run
cd backend
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Note: The container images use `uv` to install dependencies; using `pip` locally is fine for development.

## Project layout

- `backend/app_api/` – Django project (settings, urls, ASGI/WSGI)
- `backend/core/` – App with models, serializers, views, filters, permissions, pagination, management commands
- `backend/entrypoint.prod.sh` – Container entrypoint; applies migrations, seeds demo data, starts Uvicorn
- `backend/Dockerfile` – Multi-stage build using `uv`
- `docker-compose.yml` – DB + backend stack
- `docs/` – Assignment PDF

## Notes

- Max page size is capped at 100 to prevent large payloads
- Unique constraints on `(article, author)` and `(article, tag)` pairs
- `created_by` and `author` fields are set server-side from the authenticated user

---

For complete cURL examples of every endpoint, see `README.curl.md`.
