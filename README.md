# Church History Learning Platform

> *An AI-powered web application for learning church history in the Reformed tradition.*

## Overview

This application provides an interactive, AI-driven learning experience for church history, with a focus on the Reformed theological tradition. Users learn through conversation with an AI agent, visual tools, structured curriculum by historical era, fun quizzes, and progress tracking.

## Tech Stack

- **Backend:** Django 5 + Django REST Framework
- **Frontend:** React 18 + TypeScript + Vite + Tailwind CSS
- **Database:** PostgreSQL 16 with pgvector
- **Task Queue:** Celery + Redis
- **Auth:** Google OAuth via django-allauth
- **AI:** LLM integration with RAG (Retrieval-Augmented Generation)

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 16+ with pgvector extension
- Redis
- Docker & Docker Compose (recommended)

### Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and fill in your values
3. See detailed setup instructions in `docs/ARCHITECTURE.md`

## Documentation

- [Feature Priority & Roadmap](docs/PRIORITY.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Licensing Policy](docs/LICENSING.md)

## License

All dependencies are open source with commercially permissive licenses. See [LICENSING.md](docs/LICENSING.md) for details.
