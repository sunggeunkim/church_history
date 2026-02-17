# Tech Stack Research: Best Practices for Django + React + pgvector (2025-2026)

## Table of Contents
1. [Django 5.x Project Structure](#1-django-5x-project-structure)
2. [React 18 + Vite + TypeScript Setup](#2-react-18--vite--typescript-setup)
3. [pgvector with PostgreSQL 16 for RAG](#3-pgvector-with-postgresql-16-for-rag)
4. [DRF + React SPA Authentication](#4-drf--react-spa-authentication)
5. [Docker Compose Setup](#5-docker-compose-setup)
6. [License Audit](#6-license-audit-of-all-proposed-dependencies)
7. [Alternative Recommendations](#7-alternative-recommendations)

---

## 1. Django 5.x Project Structure

### Recommended Version: Django 5.2 LTS
- Released April 2, 2025. Long-term support until April 2028.
- Supports Python 3.10-3.14.
- Key new features: composite primary keys, automatic model imports in shell, `response.text` property.
- License: BSD-3-Clause (permissive).

### Best Practices for Production Structure

```
backend/
├── config/                  # Project configuration (renamed from default project name)
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py          # Shared settings
│   │   ├── development.py   # Dev overrides (DEBUG=True, etc.)
│   │   └── production.py    # Prod overrides (security, caching)
│   ├── urls.py              # Root URL configuration
│   ├── wsgi.py
│   └── asgi.py
├── apps/                    # All Django apps in dedicated directory
│   ├── __init__.py
│   ├── accounts/            # User auth & profiles
│   ├── content/             # Scraped content & embeddings
│   ├── eras/                # Church history eras
│   ├── chat/                # AI chat & RAG
│   ├── quiz/                # Tests & quizzes
│   ├── progress/            # Progress tracking
│   └── sharing/             # Social sharing
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── manage.py
├── pytest.ini               # or pyproject.toml
└── entrypoint.sh            # Docker entrypoint script
```

### Key Recommendations:
1. **Separate settings by environment** using a `settings/` package with `base.py`, `development.py`, and `production.py`. Use `DJANGO_SETTINGS_MODULE` env var to select.
2. **Use `python-decouple`** for environment variable management. All secrets via `.env` files.
3. **Group apps in `apps/` directory** for clean organization. Each app handles one domain.
4. **Use `config/` package** instead of the default project name for settings/URLs (cleaner separation).
5. **Split requirements** into base/dev/prod files. Dev includes testing and debugging tools.
6. **Create an `entrypoint.sh`** for Docker that waits for Postgres readiness before starting Django.

### Django Settings Best Practices:
```python
# base.py
import os
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='', cast=lambda v: [s.strip() for s in v.split(',')])

# Use apps/ prefix for custom apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    # ...
    'rest_framework',
    'corsheaders',
    'allauth',
    'apps.accounts',
    'apps.content',
    # etc.
]
```

---

## 2. React 18 + Vite + TypeScript Setup

### Recommended Versions:
- React 18 (MIT license)
- Vite 6.x (MIT license) - 40x faster builds than CRA
- TypeScript 5.x (Apache-2.0 license)

### Project Initialization:
```bash
npm create vite@latest frontend -- --template react-ts
```

### Recommended Folder Structure:
```
frontend/
├── public/                  # Static assets served as-is
├── src/
│   ├── assets/              # Images, fonts, static files
│   ├── components/          # Shared/reusable UI components
│   │   ├── ui/              # shadcn/ui components
│   │   └── layout/          # Layout components (Header, Sidebar, etc.)
│   ├── pages/               # Page-level components (routing entry points)
│   ├── hooks/               # Custom React hooks
│   ├── stores/              # Zustand state stores
│   ├── services/            # API clients (Axios instances)
│   ├── types/               # TypeScript type definitions
│   ├── utils/               # Helper functions
│   ├── lib/                 # Third-party lib configurations
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css            # Tailwind directives
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.ts
├── .eslintrc.cjs            # or eslint.config.js (flat config)
├── .prettierrc
└── vitest.config.ts
```

### Key Recommendations:
1. **Vite** is the gold standard for React builds in 2025/2026. Uses esbuild/SWC for dev, Rollup for production.
2. **Component organization:** Group by feature in `pages/`, shared components in `components/`. Each component can have its own directory with tests, styles, types co-located.
3. **State management with Zustand:** Minimal boilerplate, MIT licensed, zero dependencies, excellent performance. Create stores per domain (e.g., `authStore`, `chatStore`).
4. **shadcn/ui + Radix primitives:** Copy-paste model gives full ownership of components. MIT licensed. As of June 2025, migrated to unified `radix-ui` package.
5. **Dev tooling stack:**
   - ESLint (MIT) + Prettier (MIT) for linting/formatting
   - Vitest (MIT) + React Testing Library (MIT) for testing
   - Husky + lint-staged for pre-commit hooks
   - TypeScript ESLint for type-aware linting

### Vite Configuration for Django Backend:
```typescript
// vite.config.ts
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
});
```

---

## 3. pgvector with PostgreSQL 16 for RAG

### Overview:
pgvector is an open-source PostgreSQL extension (PostgreSQL License) for storing, querying, and indexing high-dimensional vectors. It eliminates the need for a separate vector database.

### RAG Pipeline Architecture:
```
1. Content Ingestion → Text Chunking → Embedding Generation → Store in pgvector
2. User Query → Query Embedding → Vector Similarity Search → Top-K Results → LLM Context → Response
```

### Schema Best Practices:
```sql
-- Enable the extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Content embeddings table
CREATE TABLE content_embeddings (
    id SERIAL PRIMARY KEY,
    content_source_id INTEGER REFERENCES content_sources(id),
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    embedding VECTOR(384),        -- Dimension depends on model
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- HNSW index for approximate nearest neighbor search
CREATE INDEX ON content_embeddings
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
```

### Key Recommendations:
1. **Use HNSW indexing** (Hierarchical Navigable Small World) for production. It provides approximate nearest-neighbor search with dramatically lower latency vs. exact search.
2. **Cosine similarity** (`vector_cosine_ops` / `<=>` operator) is the standard distance metric for language embeddings.
3. **Embedding model choice:**
   - `all-MiniLM-L6-v2` (384 dimensions) - good balance of speed and quality, Apache-2.0 license
   - `text-embedding-3-small` from OpenAI (1536 dimensions) - higher quality but requires API calls
   - For our project, `sentence-transformers` with `all-MiniLM-L6-v2` is recommended for self-hosted embeddings (Apache-2.0 license).
4. **Chunking strategy:** Experiment with 256-512 token chunks with 50-token overlap. Include metadata (source, era, topic) in each chunk.
5. **Scale:** pgvector handles ~100K documents well without special optimization. For larger workloads, consider pgvectorscale.
6. **Co-locate embeddings with metadata** in the same database for hybrid queries (semantic search + metadata filtering).

### Django Integration:
```python
# Using pgvector with Django ORM
from pgvector.django import VectorField, HnswIndex

class ContentEmbedding(models.Model):
    content_source = models.ForeignKey('ContentSource', on_delete=models.CASCADE)
    chunk_text = models.TextField()
    chunk_index = models.IntegerField()
    embedding = VectorField(dimensions=384)
    metadata = models.JSONField(default=dict)

    class Meta:
        indexes = [
            HnswIndex(
                name='embedding_hnsw_idx',
                fields=['embedding'],
                m=16,
                ef_construction=64,
                opclasses=['vector_cosine_ops'],
            ),
        ]
```

---

## 4. DRF + React SPA Authentication

### Recommended Stack:
- **django-allauth** (MIT) - Google OAuth social authentication
- **djangorestframework-simplejwt** (MIT) - JWT token management
- **dj-rest-auth** (MIT) - REST endpoints for auth flows

### Authentication Flow:
```
1. User clicks "Sign in with Google" in React
2. React redirects to Django OAuth endpoint
3. Django (allauth) handles OAuth flow with Google
4. On success, Django issues JWT access + refresh tokens
5. Tokens stored in httpOnly cookies (NOT localStorage)
6. React sends cookies automatically with each API request
7. Short-lived access tokens (15-60 min), longer refresh tokens (1-7 days)
```

### Security Best Practices (2025):
1. **Store tokens in httpOnly cookies** - prevents XSS attacks from accessing tokens. NEVER use localStorage for auth tokens.
2. **Short-lived access tokens** (15-60 minutes) to minimize risk of leaked tokens.
3. **Refresh token rotation** - issue new refresh token with each refresh request.
4. **HTTPS enforced** in production (Django `SECURE_SSL_REDIRECT = True`).
5. **CSRF protection** enabled for cookie-based auth.
6. **CORS whitelist** configured per environment.

### Django Settings:
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # For admin
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_COOKIE': 'access_token',
    'AUTH_COOKIE_HTTP_ONLY': True,
    'AUTH_COOKIE_SECURE': True,      # True in production
    'AUTH_COOKIE_SAMESITE': 'Lax',
}

# django-allauth
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}
```

---

## 5. Docker Compose Setup

### Production-Ready Architecture:
```yaml
# docker-compose.yml (development)
services:
  backend:
    build:
      context: .
      dockerfile: docker/Dockerfile.backend
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  frontend:
    build:
      context: .
      dockerfile: docker/Dockerfile.frontend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "5173:5173"
    restart: unless-stopped

  db:
    image: pgvector/pgvector:pg16
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  redis:
    image: valkey/valkey:8-alpine    # See license note below
    healthcheck:
      test: ["CMD", "valkey-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  celery:
    build:
      context: .
      dockerfile: docker/Dockerfile.backend
    command: celery -A config worker -l info
    env_file: .env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  celery-beat:
    build:
      context: .
      dockerfile: docker/Dockerfile.backend
    command: celery -A config beat -l info
    env_file: .env
    depends_on:
      - redis
    restart: unless-stopped

volumes:
  postgres_data:
```

### Key Recommendations:
1. **Health checks** for every service (`pg_isready`, `valkey-cli ping`, custom `/health` endpoint for Django).
2. **`depends_on` with `condition: service_healthy`** to ensure proper startup ordering.
3. **Named volumes** for persistent data (especially PostgreSQL).
4. **`restart: unless-stopped`** for all services in production.
5. **Separate compose files** for dev and prod (`docker-compose.yml` and `docker-compose.prod.yml`).
6. **Use `pgvector/pgvector:pg16`** Docker image which comes with pgvector pre-installed.
7. **Production additions:**
   - Nginx reverse proxy for static files and SSL termination
   - Gunicorn as WSGI server (not Django's `runserver`)
   - Resource limits via `deploy` key
   - Proper logging configuration
8. **Entrypoint script** to wait for database readiness and run migrations.
9. **Use Valkey instead of Redis** (see license section below).

---

## 6. License Audit of All Proposed Dependencies

### Backend Dependencies

| Dependency | Proposed License | Verified License | Status |
|---|---|---|---|
| Django 5.2 | BSD-3-Clause | BSD-3-Clause | PASS |
| Django REST Framework | BSD-3-Clause | BSD-3-Clause | PASS |
| django-allauth | MIT | MIT | PASS |
| djangorestframework-simplejwt | MIT | MIT | PASS |
| PostgreSQL 16 | PostgreSQL License | PostgreSQL License | PASS |
| pgvector | PostgreSQL License | PostgreSQL License | PASS |
| Celery | BSD-3-Clause | BSD-3-Clause | PASS |
| Redis | BSD-3-Clause | **CHANGED - see warning** | **FLAG** |
| yt-dlp | Unlicense | Unlicense | PASS |
| beautifulsoup4 | MIT | MIT | PASS |
| requests | Apache-2.0 | Apache-2.0 | PASS |
| sentence-transformers | Apache-2.0 | Apache-2.0 | PASS |
| litellm | MIT | MIT (core) | PASS (see note) |
| django-cors-headers | MIT | MIT | PASS |
| python-decouple | MIT | MIT | PASS |
| pytest | MIT | MIT | PASS |
| pytest-django | BSD-3-Clause | BSD-3-Clause | PASS |
| factory-boy | MIT | MIT | PASS |
| ruff | MIT | MIT | PASS |

### Frontend Dependencies

| Dependency | Proposed License | Verified License | Status |
|---|---|---|---|
| React 18 | MIT | MIT | PASS |
| Vite | MIT | MIT | PASS |
| TypeScript | Apache-2.0 | Apache-2.0 | PASS |
| React Router v6 | MIT | MIT | PASS |
| Zustand | MIT | MIT | PASS |
| Axios | MIT | MIT | PASS |
| shadcn/ui | MIT | MIT | PASS |
| Radix UI | MIT | MIT | PASS |
| Tailwind CSS | MIT | MIT | PASS |
| Fabric.js | MIT | MIT | PASS |
| Konva.js | MIT | MIT | PASS |
| Vitest | MIT | MIT | PASS |
| React Testing Library | MIT | MIT | PASS |
| ESLint | MIT | MIT | PASS |
| Prettier | MIT | MIT | PASS |

### Infrastructure

| Dependency | Proposed License | Verified License | Status |
|---|---|---|---|
| Docker | Apache-2.0 | Apache-2.0 | PASS |
| Docker Compose | Apache-2.0 | Apache-2.0 | PASS |
| Nginx | BSD-2-Clause | BSD-2-Clause | PASS |

---

### CRITICAL LICENSE FLAG: Redis

**Redis has changed its license.** The situation is as follows:
- **Redis <= 7.2.x:** BSD-3-Clause (fully permissive) - this is what was listed in ARCHITECTURE.md
- **Redis 7.4-7.8.x:** Dual RSALv2/SSPLv1 - **NOT open source by OSI definition**, restricts commercial cloud hosting
- **Redis 8.0+:** Triple license (RSALv2/SSPLv1/AGPLv3) - AGPLv3 is copyleft and on our **prohibited list**

**Recommendation: Replace Redis with Valkey.**

**Valkey** is the BSD-3-Clause licensed fork of Redis, backed by the Linux Foundation, AWS, Google Cloud, and Oracle. It is:
- A **drop-in replacement** for Redis (identical API, compatible with Celery)
- **BSD-3-Clause licensed** (same as the original Redis)
- **Actively maintained** with better performance (37% higher write throughput)
- Supported by all major cloud providers
- 75% of former Redis users are evaluating or have adopted Valkey

Migration is trivial - change the Docker image and update Python imports.

### Note on litellm:
litellm core is MIT licensed. The `enterprise/` directory has a separate enterprise license. Since we only use the core open-source features, this is fine. However, enterprise features (SSO, RBAC) require a commercial license.

---

## 7. Alternative Recommendations

### Recommended Changes to ARCHITECTURE.md

#### 1. Replace Redis with Valkey
- **Current:** Redis (BSD-3-Clause)
- **Recommended:** Valkey (BSD-3-Clause)
- **Reason:** Redis license has changed to restrictive/copyleft terms. Valkey is the BSD-licensed community fork, drop-in compatible.
- **Docker image:** `valkey/valkey:8-alpine`

#### 2. Use Django 5.2 LTS (not just "5.x")
- **Current:** Django 5.x
- **Recommended:** Django 5.2 LTS specifically
- **Reason:** Django 5.2 is the LTS release (supported until April 2028). Pinning to LTS ensures long-term stability and security updates.

#### 3. Consider TanStack Query alongside Axios
- **Current:** Axios (MIT)
- **Recommended:** Axios + TanStack Query (MIT)
- **Reason:** TanStack Query (formerly React Query) provides automatic caching, background refetching, and server state management. The 2025 best practice is to pair Axios (HTTP layer) with TanStack Query (caching/state layer). Both are MIT licensed.

#### 4. Canvas Library: Konva.js over Fabric.js
- **Current:** Fabric.js or Konva.js (both MIT)
- **Recommended:** Konva.js
- **Reason:** Better performance for animations and frequent updates, automatic memory management, lighter weight, written in TypeScript. For a teaching canvas with interactive elements (timelines, maps, flashcards), Konva's performance characteristics are better suited. However, if SVG export is needed, Fabric.js is the better choice (Konva does not export SVG).

#### 5. Use `django-environ` or `python-decouple`
- Both are MIT licensed and widely used. `python-decouple` (listed in ARCHITECTURE.md) is fine. `django-environ` is another popular alternative. Either works well.

#### 6. Consider `uv` as Python Package Manager
- **`uv`** by Astral (same team as ruff) is a blazing-fast Python package installer and resolver, written in Rust. MIT licensed. It is 10-100x faster than pip and supports lockfiles. Worth considering for development workflow.

### Dependencies That Are Fine As-Is
All other proposed dependencies have been verified with permissive licenses and are current best-practice choices for 2025-2026. The architecture document is well-designed.

---

## Summary

The proposed tech stack in ARCHITECTURE.md is solid and well-chosen. The only critical issue is the **Redis license change** - Valkey is the recommended replacement. All other dependencies pass the license audit. The directory structure follows 2025 best practices. Key additions to consider are TanStack Query for data fetching and pinning Django to the 5.2 LTS release.
