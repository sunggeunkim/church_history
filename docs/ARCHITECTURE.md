# Architecture Overview

## Tech Stack

All dependencies must be **open source with commercially permissive licenses** (MIT, Apache-2.0, BSD, ISC, PostgreSQL License). No AGPL, GPL, or SSPL unless isolated and pre-approved.

### Backend (Django)
| Component | Technology | License |
|---|---|---|
| Framework | Django 5.2 LTS | BSD-3-Clause |
| REST API | Django REST Framework | BSD-3-Clause |
| Auth | django-allauth (Google OAuth) | MIT |
| JWT | djangorestframework-simplejwt | MIT |
| Database | PostgreSQL 16 | PostgreSQL License |
| Vector DB | pgvector extension | PostgreSQL License |
| Task Queue | Celery + Valkey (Redis fork) | BSD-3-Clause / BSD-3-Clause |
| Web Scraping | yt-dlp (transcripts), beautifulsoup4, requests | Unlicense / MIT / Apache-2.0 |
| Embeddings | sentence-transformers (Apache-2.0) or OpenAI API |  Apache-2.0 |
| LLM Integration | litellm or direct API calls | MIT |
| CORS | django-cors-headers | MIT |
| Environment | python-decouple | MIT |
| Testing | pytest, pytest-django, factory-boy | MIT |
| Linting | ruff | MIT |

### Frontend (React)
| Component | Technology | License |
|---|---|---|
| Framework | React 18 | MIT |
| Build Tool | Vite | MIT |
| Language | TypeScript | Apache-2.0 |
| Routing | React Router v6 | MIT |
| State Management | Zustand | MIT |
| HTTP Client | Axios | MIT |
| UI Components | Shadcn/ui (Radix primitives) | MIT |
| Styling | Tailwind CSS | MIT |
| Chat UI | Custom components | N/A |
| Canvas | Konva.js | MIT |
| Testing | Vitest + React Testing Library | MIT |
| Linting | ESLint + Prettier | MIT |

### Infrastructure
| Component | Technology | License |
|---|---|---|
| Containerization | Docker + Docker Compose | Apache-2.0 |
| Reverse Proxy | Nginx | BSD-2-Clause |
| CI/CD | GitHub Actions | N/A (platform) |

---

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Client (Browser)                   │
│                  React + TypeScript                   │
│         Vite | Tailwind | Shadcn/ui | Zustand        │
└──────────────────────┬──────────────────────────────┘
                       │ HTTPS (REST + WebSocket)
                       ▼
┌─────────────────────────────────────────────────────┐
│                   Nginx (Reverse Proxy)               │
│              Static files | SSL termination           │
└──────────┬───────────────────────┬──────────────────┘
           │                       │
           ▼                       ▼
┌─────────────────────┐  ┌─────────────────────────┐
│   Django Backend     │  │   Celery Workers         │
│   (Gunicorn/ASGI)    │  │   (Background Tasks)     │
│                      │  │   - Scraping             │
│   - REST API         │  │   - Embedding generation │
│   - Auth (OAuth)     │  │   - Quiz generation      │
│   - Chat/RAG         │  │                          │
│   - WebSocket (chat) │  │                          │
└──────────┬───────────┘  └──────────┬──────────────┘
           │                         │
           ▼                         ▼
┌─────────────────────────────────────────────────────┐
│              PostgreSQL 16 + pgvector                 │
│                                                       │
│   Tables:                    Vector Store:            │
│   - users                    - content_embeddings     │
│   - eras                     - (cosine similarity)    │
│   - content_sources                                   │
│   - chat_sessions                                     │
│   - quiz_results                                      │
│   - progress                                          │
└─────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────┐
│    Valkey (Redis)    │
│   - Celery broker    │
│   - Cache            │
│   - Session store    │
└─────────────────────┘
```

---

## Security Practices

1. **No secrets in code.** All secrets via environment variables (`.env` files in `.gitignore`).
2. **`.env.example`** files with placeholder values only.
3. **Django `SECRET_KEY`** generated per environment, never committed.
4. **OAuth credentials** stored in environment variables only.
5. **API keys** (LLM providers) stored in environment variables only.
6. **HTTPS enforced** in production.
7. **CSRF protection** enabled (Django default).
8. **CORS whitelist** configured per environment.
9. **SQL injection prevention** via Django ORM (no raw SQL without parameterization).
10. **XSS prevention** via React's default escaping + DRF serializers.
11. **Rate limiting** on API endpoints.
12. **Input validation** on all user inputs.
13. **Dependency scanning** via `pip-audit` and `npm audit`.

---

## Directory Structure

```
church_history/
├── docs/                    # Project documentation
│   ├── ARCHITECTURE.md
│   ├── PRIORITY.md
│   ├── LICENSING.md
│   └── features/            # Per-feature documentation
├── backend/                 # Django project
│   ├── config/              # Django settings (base, dev, prod)
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── apps/
│   │   ├── accounts/        # User auth & profiles
│   │   ├── content/         # Scraped content & embeddings
│   │   ├── eras/            # Church history eras
│   │   ├── chat/            # AI chat & RAG
│   │   ├── quiz/            # Tests & quizzes
│   │   ├── progress/        # Progress tracking
│   │   └── sharing/         # Social sharing
│   ├── requirements/
│   │   ├── base.txt
│   │   ├── development.txt
│   │   └── production.txt
│   ├── manage.py
│   └── pytest.ini
├── frontend/                # React application
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── stores/
│   │   ├── services/        # API clients
│   │   ├── types/
│   │   └── utils/
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.ts
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── nginx/
│       └── nginx.conf
├── docker-compose.yml
├── docker-compose.prod.yml
├── .github/
│   └── workflows/
├── .gitignore
├── .env.example
├── features.md
└── README.md
```
