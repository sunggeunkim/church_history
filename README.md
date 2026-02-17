# Toledot (תּוֹלְדוֹת)

> *The Generations of the Church* - An AI-powered web application for learning church history in the Reformed tradition.

## About the Name

**Toledot** (Hebrew: תּוֹלְדוֹת, pronounced TOH-leh-DOHT) means "generations" or "historical account." It is the structuring device of Genesis, introducing each epoch with "These are the toledot of..." This app traces the toledot of Christ's church -- the generations of believers, councils, confessions, and movements from the apostolic era to the modern age.

## Overview

Toledot provides an interactive, AI-driven learning experience for church history, with a focus on the Reformed theological tradition. Users learn through:

- Conversation with an AI agent grounded in seminary-level content
- Visual canvas with images, maps, and interactive tools
- Structured curriculum organized by historical era
- Fun quizzes and knowledge tests
- Progress tracking with achievement rewards
- Social sharing of learning milestones

## Tech Stack

- **Backend:** Django 5.2 LTS + Django REST Framework
- **Frontend:** React 19 + TypeScript + Vite + Tailwind CSS
- **Database:** PostgreSQL 16 with pgvector (vector similarity search)
- **Task Queue:** Celery + Valkey (BSD-licensed Redis fork)
- **Auth:** Google OAuth via django-allauth + JWT
- **AI:** LLM integration with RAG (Retrieval-Augmented Generation)
- **UI:** Shadcn/ui + Radix primitives + Zustand state management

All dependencies are **open source with commercially permissive licenses** (MIT, Apache-2.0, BSD). See [LICENSING.md](docs/LICENSING.md).

## Getting Started

### Prerequisites

- Docker & Docker Compose (recommended)
- Or manually: Python 3.12+, Node.js 20+, PostgreSQL 16+ with pgvector, Valkey/Redis

### Quick Start (Docker)

```bash
# 1. Clone the repository
git clone https://github.com/sunggeunkim/church_history.git
cd church_history

# 2. Set up environment variables
cp .env.example .env
# Edit .env with your values (Google OAuth credentials, etc.)

# 3. Start the full stack
docker compose up --build

# 4. Access the application
# Frontend: http://localhost (via Nginx)
# API:      http://localhost/api/health/
# Admin:    http://localhost/admin/
```

### Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements/development.txt
python manage.py migrate
python manage.py runserver
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Documentation

- [Feature Priority & Roadmap](docs/PRIORITY.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Licensing Policy](docs/LICENSING.md)
- [P0 Feature Plan](docs/features/p0-plan.md)
- [Design System & UI/UX](docs/features/p0-design.md)
- [Name Research](docs/features/p0-name-research.md)
- [Theological Name Review](docs/features/p0-name-theological-review.md)
- [Tech Stack Research](docs/features/p0-tech-research.md)

## Project Structure

```
toledot/
├── backend/          # Django 5.2 LTS + DRF
│   ├── config/       # Settings (base/dev/prod), URLs, WSGI, Celery
│   ├── apps/         # Django apps (accounts, content, eras, chat, quiz, progress, sharing)
│   └── requirements/ # Pinned dependencies (base/dev/prod)
├── frontend/         # React 19 + Vite + TypeScript
│   ├── src/
│   │   ├── components/  # Layout, shared, UI components
│   │   ├── pages/       # Route pages
│   │   ├── stores/      # Zustand state stores
│   │   ├── services/    # API client (Axios)
│   │   ├── hooks/       # Custom React hooks
│   │   └── types/       # TypeScript definitions
│   └── package.json
├── docker/           # Dockerfiles (backend, frontend) + Nginx config
├── docs/             # Architecture, plans, research, design specs
├── .github/          # CI workflow + PR template
├── docker-compose.yml
└── .env.example      # Environment variable template (no secrets!)
```

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Run tests: `pytest` (backend) and `npm run test` (frontend)
4. Run linters: `ruff check .` (backend) and `npm run lint` (frontend)
5. Create a PR using the PR template

## License

All dependencies are open source with commercially permissive licenses (MIT, Apache-2.0, BSD). No GPL, AGPL, or SSPL dependencies. See [LICENSING.md](docs/LICENSING.md) for the full policy.
