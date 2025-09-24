# Articles API – cURL Examples

This guide shows end-to-end cURL examples for every endpoint and common usage pattern supported by the API.

Base URL (when running with docker compose):

- <http://localhost:8000>

Prereq: The API must be running. See the main `README.md` for setup instructions.

Tip: Several examples use `jq` to parse JSON. If you don’t have `jq`, you can copy the values manually.

## 1) Authentication (JWT)

Obtain tokens (access + refresh):

```sh
curl -sS -X POST http://localhost:8000/api/token/ \
  -H 'Content-Type: application/json' \
  -d '{"username": "demo_user1", "password": "demo_user1_1234"}' | jq
```

Export the access and refresh tokens to environment variables (requires `jq`):

```sh
TOKENS_JSON="$(curl -sS -X POST http://localhost:8000/api/token/ \
  -H 'Content-Type: application/json' \
  -d '{"username": "demo_user1", "password": "demo_user1_1234"}' | jq .)"

ACCESS_TOKEN="$(echo "$TOKENS_JSON" | jq -r .access)"
REFRESH_TOKEN="$(echo "$TOKENS_JSON" | jq -r .refresh)"
```

Refresh the access token:

```sh
ACCESS_TOKEN="$(curl -sS -X POST http://localhost:8000/api/token/refresh/ \
  -H 'Content-Type: application/json' \
  -d '{"refresh": "'"${REFRESH_TOKEN}"'"}' | jq -r .access)"
echo "New ACCESS_TOKEN acquired"
```

## 2) Articles

### 2.1 List articles (basic)

```sh
curl -sS http://localhost:8000/api/articles/ | jq
```

### 2.2 List articles with filtering

- By year:

```sh
curl -sS 'http://localhost:8000/api/articles/?year=2024' | jq
```

- By month:

```sh
curl -sS 'http://localhost:8000/api/articles/?month=9' | jq
```

- By author names (comma-separated):

```sh
curl -sS 'http://localhost:8000/api/articles/?author=Ada%20Lovelace,Alan%20Turing' | jq
```

- By tag names (comma-separated):

```sh
curl -sS 'http://localhost:8000/api/articles/?tag=AI,ML' | jq
```

- By keyword (matches title OR abstract):

```sh
curl -sS 'http://localhost:8000/api/articles/?keyword=neural' | jq
```

- Combine filters:

```sh
curl -sS 'http://localhost:8000/api/articles/?year=2025&tag=AI&author=Ada%20Lovelace' | jq
```

### 2.3 Search and ordering

- Search (title and abstract):

```sh
curl -sS 'http://localhost:8000/api/articles/?search=practical' | jq
```

- Ordering ascending by publication date:

```sh
curl -sS 'http://localhost:8000/api/articles/?ordering=publication_date' | jq
```

- Ordering descending by creation date:

```sh
curl -sS 'http://localhost:8000/api/articles/?ordering=-created_at' | jq
```

### 2.4 Pagination

- Second page with page size 50 (max 100):

```sh
curl -sS 'http://localhost:8000/api/articles/?page=2&page_size=50' | jq
```

### 2.5 Retrieve a single article by ID

```sh
curl -sS http://localhost:8000/api/articles/1/ | jq
```

Tip: to grab an ID from the list, you can:

```sh
FIRST_ID="$(curl -sS http://localhost:8000/api/articles/ | jq -r '.results[0].id')"
curl -sS "http://localhost:8000/api/articles/${FIRST_ID}/" | jq
```

### 2.6 Create an article (auth required)

Authors and Tags are passed as simple arrays of strings. Missing names will be created automatically.

```sh
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
  }' | jq
```

### 2.7 Update an article (owner only)

- Full update (PUT):

```sh
ARTICLE_ID=1
curl -sS -X PUT http://localhost:8000/api/articles/${ARTICLE_ID}/ \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H 'Content-Type: application/json' \
  -d '{
    "identifier": "ART-900001",
    "publication_date": "2025-01-16",
    "title": "Neural Nets in Practice - 2nd Edition",
    "abstract": "Updated abstract.",
    "authors": ["Ada Lovelace"],
    "tags": ["AI"]
  }' | jq
```

- Partial update (PATCH):

```sh
ARTICLE_ID=1
curl -sS -X PATCH http://localhost:8000/api/articles/${ARTICLE_ID}/ \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Neural Nets in Practice - Revised"
  }' | jq
```

### 2.8 Delete an article (owner only)

```sh
ARTICLE_ID=1
curl -sS -X DELETE http://localhost:8000/api/articles/${ARTICLE_ID}/ \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

### 2.9 Export articles to CSV

- Export by filters (respects same filters as list):

```sh
curl -sS 'http://localhost:8000/api/articles/export/?year=2024&tag=AI' -o articles.csv
```

- Export by explicit identifiers (comma-separated):

```sh
curl -sS 'http://localhost:8000/api/articles/export/?ids=ART-000001,ART-000002' -o selected.csv
```

## 3) Comments

### 3.1 List comments

```sh
curl -sS http://localhost:8000/api/comments/ | jq
```

- Ordering newest first (by created_at):

```sh
curl -sS 'http://localhost:8000/api/comments/?ordering=-created_at' | jq
```

### 3.2 Create a comment (auth required)

`article_id` is the numeric ID of the target Article. The `author` field is set automatically from the token.

```sh
curl -sS -X POST http://localhost:8000/api/comments/ \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H 'Content-Type: application/json' \
  -d '{
    "article_id": 1,
    "body": "Great article!"
  }' | jq
```

### 3.3 Update a comment (owner only)

```sh
COMMENT_ID=1
curl -sS -X PATCH http://localhost:8000/api/comments/${COMMENT_ID}/ \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H 'Content-Type: application/json' \
  -d '{
    "body": "Edited comment text"
  }' | jq
```

### 3.4 Delete a comment (owner only)

```sh
COMMENT_ID=1
curl -sS -X DELETE http://localhost:8000/api/comments/${COMMENT_ID}/ \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

## 4) Reference data (read-only)

### 4.1 List authors

```sh
curl -sS http://localhost:8000/api/authors/ | jq
```

### 4.2 List tags

```sh
curl -sS http://localhost:8000/api/tags/ | jq
```

## 5) Common issues

- 401 Unauthorized: Missing or invalid `Authorization: Bearer <token>` header for endpoints that require auth (create/update/delete).
- 403 Forbidden: You’re not the owner (Articles: `created_by`, Comments: `author`).
- 400 Bad Request: Invalid payload (e.g., missing required fields).
- Pagination caps at `page_size=100`.

---

For setup, additional details, and data model, see the main `README.md`.
