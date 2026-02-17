# P0: Project Foundation & App Naming - Feature Plan

## Overview

P0 establishes the entire development infrastructure and gives the application its identity. Every subsequent feature (P1-P8) depends on this foundation being solid. The deliverable is a fully containerized, running development environment with a named application, CI/CD skeleton, and all tooling configured.

**Branch:** `feature/project-foundation`
**Features Covered:** #11 (App Naming), Project Setup

---

## 1. Detailed Task Breakdown

### T0.1 - App Naming Research & Selection
**Description:** Research Hebrew and Greek words related to church history, learning, and wisdom. Propose candidates. The name must be memorable, pronounceable, not trademarked, and not in use by any existing company or product. Check domain availability as a bonus.

**Acceptance Criteria:**
- At least 5 candidate names researched with etymology and meaning
- Each candidate checked against trademark databases and web search
- Final name selected and documented with rationale
- Name is of Hebrew or Greek origin (per feature #11)
- Name is easy to remember and pronounce for English speakers

**Assigned Role:** Theologian + Researcher
**Estimated Effort:** Small

---

### T0.2 - Repository & Git Configuration
**Description:** Initialize the git repository structure, configure `.gitignore`, set up branch protection rules, and establish the branching strategy.

**Acceptance Criteria:**
- `.gitignore` covers Python, Node.js, IDE, OS, Docker, and environment files
- `.env.example` file with placeholder values (no real secrets)
- `README.md` with project description, setup instructions, and license info
- Repository is on `feature/project-foundation` branch

**Assigned Role:** Backend Dev
**Estimated Effort:** Small

---

### T0.3 - Django Backend Setup
**Description:** Create the Django project with split settings (base/development/production), configure Django REST Framework, set up the initial app structure, and configure environment variable handling.

**Acceptance Criteria:**
- Django 5.x project created under `backend/`
- Split settings: `config/settings/base.py`, `development.py`, `production.py`
- Django REST Framework installed and configured
- `django-cors-headers` installed and configured
- `python-decouple` for environment variable management
- `config/urls.py` with API namespace and health-check endpoint
- `config/wsgi.py` and `config/asgi.py` configured
- `manage.py` works with `DJANGO_SETTINGS_MODULE` env var
- `requirements/base.txt`, `development.txt`, `production.txt` created
- All dependencies are permissively licensed (verified)
- `backend/apps/` directory with `__init__.py`
- `backend/apps/accounts/` app scaffolded (models, views, serializers, urls - minimal)
- Health-check endpoint returns 200 OK at `/api/health/`

**Assigned Role:** Backend Dev
**Estimated Effort:** Medium

---

### T0.4 - PostgreSQL + pgvector Configuration
**Description:** Set up PostgreSQL 16 with pgvector extension. Create the database configuration in Django settings. Ensure migrations can run.

**Acceptance Criteria:**
- PostgreSQL 16 configured in Django settings (via env vars for host, port, name, user, password)
- pgvector extension creation included in initial migration or Docker entrypoint
- `psycopg[binary]` or `psycopg2-binary` in requirements
- `django.contrib.postgres` in INSTALLED_APPS
- Database connection works in Docker environment
- `python manage.py migrate` runs successfully

**Assigned Role:** Backend Dev
**Estimated Effort:** Small

---

### T0.5 - React Frontend Setup
**Description:** Create the React application with Vite, TypeScript, Tailwind CSS, and Shadcn/ui. Set up the basic project structure with routing, state management, and an API client stub.

**Acceptance Criteria:**
- React 18 + Vite + TypeScript project under `frontend/`
- Tailwind CSS configured and working
- Shadcn/ui initialized with at least one component (Button)
- React Router v6 with basic route structure (Home, Login placeholder)
- Zustand store scaffolded (auth store stub)
- Axios instance configured with base URL from env var
- `frontend/src/` directory structure matches ARCHITECTURE.md (components, pages, hooks, stores, services, types, utils)
- ESLint + Prettier configured
- Vitest + React Testing Library configured
- `npm run dev` starts the dev server
- `npm run build` produces production build without errors
- `npm run test` runs and passes
- All npm dependencies are permissively licensed (verified)

**Assigned Role:** Frontend Dev
**Estimated Effort:** Medium

---

### T0.6 - Docker Compose Development Environment
**Description:** Create Dockerfiles for backend and frontend, and a `docker-compose.yml` that brings up the full development stack: Django, React dev server, PostgreSQL + pgvector, Redis, and Nginx.

**Acceptance Criteria:**
- `docker/Dockerfile.backend` - Python 3.12 base, installs dependencies, runs Django
- `docker/Dockerfile.frontend` - Node 20 base, installs dependencies, runs Vite dev server
- `docker/nginx/nginx.conf` - Reverse proxy config routing `/api/` to Django, `/` to React
- `docker-compose.yml` with services: `backend`, `frontend`, `db` (PostgreSQL 16 + pgvector), `redis`, `nginx`
- All services start with `docker compose up`
- Backend can reach database and Redis
- Frontend can reach backend through Nginx proxy
- Volume mounts for hot-reload in development (backend code, frontend code)
- Named volumes for database persistence
- Environment variables loaded from `.env` file
- Health checks configured for database and Redis services

**Assigned Role:** Backend Dev + Frontend Dev
**Estimated Effort:** Medium

---

### T0.7 - Google OAuth Configuration Skeleton
**Description:** Set up `django-allauth` with the Google OAuth provider. No real credentials - just the configuration scaffolding that reads client ID/secret from environment variables.

**Acceptance Criteria:**
- `django-allauth` installed and configured in Django settings
- Google provider configured to read `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` from env vars
- `.env.example` includes placeholder values for OAuth credentials
- Auth URLs registered in `config/urls.py`
- `djangorestframework-simplejwt` installed and configured for token-based auth
- Login/callback flow is structurally complete (will work once real credentials are provided)
- No real secrets in any committed file

**Assigned Role:** Backend Dev
**Estimated Effort:** Small

---

### T0.8 - CI/CD Skeleton (GitHub Actions)
**Description:** Create GitHub Actions workflow files for linting, testing, and building on push and PR events.

**Acceptance Criteria:**
- `.github/workflows/ci.yml` workflow that runs on push to any branch and on PRs to `main`/`develop`
- Jobs: lint-backend (ruff), lint-frontend (ESLint), test-backend (pytest), test-frontend (Vitest), build-frontend
- PostgreSQL service container for backend tests
- Workflow uses env vars for secrets (no hardcoded values)
- Badge in README.md for CI status

**Assigned Role:** Backend Dev
**Estimated Effort:** Small

---

### T0.9 - Backend Tests
**Description:** Write initial tests for the Django backend to verify the project is correctly configured.

**Acceptance Criteria:**
- `pytest.ini` or `pyproject.toml` pytest configuration
- `conftest.py` with basic fixtures
- Test that Django app starts without errors
- Test that health-check endpoint returns 200
- Test that Django settings load correctly for each environment
- `ruff` linting passes with zero errors
- All tests pass with `pytest`

**Assigned Role:** QA Engineer + Backend Dev
**Estimated Effort:** Small

---

### T0.10 - Frontend Tests
**Description:** Write initial tests for the React frontend to verify the project is correctly configured.

**Acceptance Criteria:**
- Vitest configuration in `vite.config.ts`
- Test that App component renders without crashing
- Test that routing works (renders Home page)
- ESLint passes with zero errors
- Prettier formatting passes
- All tests pass with `npm run test`

**Assigned Role:** QA Engineer + Frontend Dev
**Estimated Effort:** Small

---

### T0.11 - Documentation
**Description:** Ensure all documentation is complete and accurate for P0.

**Acceptance Criteria:**
- `README.md` updated with: project name, description, tech stack summary, setup instructions (Docker), development workflow, and license info
- `docs/features/p0-plan.md` (this document) is complete
- `.env.example` is complete with all required variables and comments
- `ARCHITECTURE.md` is still accurate (update if anything changed)
- Contributing guidelines (brief, in README or separate file)

**Assigned Role:** Program Manager
**Estimated Effort:** Small

---

### T0.12 - License Audit
**Description:** Run license checks on all Python and JavaScript dependencies to confirm compliance with LICENSING.md.

**Acceptance Criteria:**
- `pip-licenses` output shows only allowed licenses for all Python packages
- `license-checker` output shows only allowed licenses for all npm packages
- Any discrepancies documented and resolved
- Audit results saved or documented

**Assigned Role:** QA Engineer
**Estimated Effort:** Small

---

### T0.13 - Integration Verification
**Description:** End-to-end verification that the full stack works together.

**Acceptance Criteria:**
- `docker compose up` brings up all services without errors
- Frontend loads in browser at `http://localhost` (via Nginx)
- API health-check responds at `http://localhost/api/health/`
- Database migrations complete successfully
- Redis connection works
- Frontend can make API calls to backend (CORS works)
- All containers stay healthy for at least 60 seconds

**Assigned Role:** QA Engineer
**Estimated Effort:** Small

---

## 2. Dependency Graph

```
T0.1 (App Naming) ──────────────────────────────────────────┐
                                                              │
T0.2 (Repo & Git) ─┬── T0.3 (Django Backend) ─┬── T0.4 (PostgreSQL + pgvector)
                    │                           │
                    │                           ├── T0.7 (OAuth Skeleton)
                    │                           │
                    │                           └── T0.9 (Backend Tests)
                    │
                    └── T0.5 (React Frontend) ──── T0.10 (Frontend Tests)
                                                              │
T0.3 + T0.4 + T0.5 ──── T0.6 (Docker Compose) ──────────────┤
                                                              │
T0.9 + T0.10 ────────── T0.8 (CI/CD Skeleton) ───────────────┤
                                                              │
T0.9 + T0.10 ────────── T0.12 (License Audit) ───────────────┤
                                                              │
T0.1 + T0.6 + T0.8 + T0.12 ── T0.11 (Documentation) ────────┤
                                                              │
All above ─────────────── T0.13 (Integration Verification) ──┘
```

**Critical Path:** T0.2 -> T0.3 -> T0.4 -> T0.6 -> T0.13

**Parallelizable Streams:**
- Stream A: T0.1 (App Naming) - can run in parallel with everything
- Stream B: T0.2 -> T0.3 -> T0.4 -> T0.7 -> T0.9 (Backend path)
- Stream C: T0.2 -> T0.5 -> T0.10 (Frontend path)
- Stream D: T0.6 depends on both B and C completing T0.3/T0.5
- Stream E: T0.8 depends on T0.9 and T0.10
- Stream F: T0.12 depends on T0.9 and T0.10 (dependencies finalized)
- Final: T0.11 (docs) and T0.13 (integration) come last

---

## 3. Role Assignments

| Task | Primary Role | Supporting Role |
|------|-------------|-----------------|
| T0.1 - App Naming | Theologian | Researcher |
| T0.2 - Repo & Git Config | Backend Dev | - |
| T0.3 - Django Backend Setup | Backend Dev | - |
| T0.4 - PostgreSQL + pgvector | Backend Dev | - |
| T0.5 - React Frontend Setup | Frontend Dev | UI/UX Engineer |
| T0.6 - Docker Compose | Backend Dev | Frontend Dev |
| T0.7 - OAuth Skeleton | Backend Dev | - |
| T0.8 - CI/CD Skeleton | Backend Dev | - |
| T0.9 - Backend Tests | QA Engineer | Backend Dev |
| T0.10 - Frontend Tests | QA Engineer | Frontend Dev |
| T0.11 - Documentation | Program Manager | All roles review |
| T0.12 - License Audit | QA Engineer | - |
| T0.13 - Integration Verification | QA Engineer | Backend Dev, Frontend Dev |

---

## 4. Definition of Done for P0

All of the following must be true before P0 is considered complete:

- [ ] **App has a name** - A Hebrew or Greek-origin name is chosen, verified as unique, and applied to the project
- [ ] **Django backend starts and serves API** - `python manage.py runserver` works; health-check endpoint returns 200
- [ ] **React frontend builds and renders** - `npm run build` succeeds; `npm run dev` serves the app; home page renders
- [ ] **PostgreSQL with pgvector is configured** - Database accepts connections; pgvector extension is installed; migrations run
- [ ] **Docker Compose brings up the full stack** - `docker compose up` starts all services; frontend accessible via Nginx; API accessible via Nginx
- [ ] **Google OAuth config is in place** - `django-allauth` configured with Google provider; credentials read from env vars; no secrets in code
- [ ] **All tests pass** - `pytest` passes for backend; `npm run test` passes for frontend
- [ ] **All linters pass** - `ruff check` passes for backend; `eslint` passes for frontend
- [ ] **All dependencies are permissively licensed** - License audit completed; no GPL/AGPL/SSPL dependencies
- [ ] **No secrets in code** - Only `.env.example` with placeholders committed; `.env` is in `.gitignore`
- [ ] **CI/CD pipeline works** - GitHub Actions workflow runs lint, test, and build jobs
- [ ] **Documentation is complete** - README, architecture docs, and this plan are up to date
- [ ] **All code is on `feature/project-foundation` branch** - Clean commit history; ready for PR

---

## 5. PR Template

See `/.github/pull_request_template.md` for the full template.

The PR for P0 should contain:
- **Title:** `P0: Project Foundation & App Naming - [App Name]`
- **Summary:** Overview of what was built and the chosen app name with rationale
- **Checklist:** All Definition of Done items checked
- **Screenshots:** Frontend rendering, Docker Compose output, test results
- **Testing instructions:** How to run the project locally
- **License audit results:** Summary of dependency license check

---

## 6. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **pgvector Docker image issues** | Medium | High | Use official `pgvector/pgvector:pg16` image; test early; have fallback to plain PostgreSQL for initial setup |
| **Dependency license violation** | Low | High | Run `pip-licenses` and `license-checker` early and after every dependency addition; automate in CI |
| **Docker Compose networking issues** | Medium | Medium | Use Docker's DNS-based service discovery; test inter-service connectivity early; document common issues |
| **Version conflicts between dependencies** | Medium | Medium | Pin all dependency versions; test full install in clean environment (Docker) |
| **App name already taken** | Medium | Low | Research multiple candidates; check trademark databases, GitHub, npm, and web search |
| **OAuth configuration complexity** | Low | Medium | Follow `django-allauth` official docs; keep it as skeleton only in P0 (full flow in P1) |
| **Hot-reload not working in Docker** | Medium | Low | Use volume mounts correctly; configure Vite/Django to watch for changes; document workarounds |
| **CI/CD pipeline fails on GitHub** | Low | Medium | Test workflow locally with `act` if possible; keep jobs simple initially |
| **Scope creep into P1 territory** | Medium | Medium | Strict adherence to P0 scope; no actual auth flow, no real API endpoints beyond health-check |
| **Team member unfamiliarity with stack** | Low | Medium | Document setup thoroughly; pair on complex tasks; keep P0 scope minimal |

---

## 7. Quality Gates

The following gates must pass before the P0 PR can be merged:

### Gate 1: Code Quality
- [ ] `ruff check backend/` passes with zero errors
- [ ] `eslint` passes with zero warnings on `frontend/src/`
- [ ] `prettier --check` passes on all frontend files
- [ ] No `TODO` or `FIXME` comments left unresolved (or tracked in issues)

### Gate 2: Test Suite
- [ ] All backend tests pass: `pytest` exits with code 0
- [ ] All frontend tests pass: `npm run test` exits with code 0
- [ ] No skipped tests without documented justification

### Gate 3: Build & Runtime
- [ ] `docker compose build` completes without errors
- [ ] `docker compose up` brings up all services
- [ ] All health checks pass (database, Redis, backend, frontend)
- [ ] Frontend production build (`npm run build`) succeeds

### Gate 4: Security
- [ ] No secrets, API keys, or credentials in any committed file
- [ ] `.env.example` contains only placeholder values
- [ ] `.gitignore` covers all sensitive files (`.env`, `*.pem`, `*.key`, etc.)
- [ ] `pip-audit` reports no critical vulnerabilities
- [ ] `npm audit` reports no critical vulnerabilities

### Gate 5: License Compliance
- [ ] All Python dependencies have allowed licenses per `docs/LICENSING.md`
- [ ] All Node.js dependencies have allowed licenses per `docs/LICENSING.md`
- [ ] License audit results documented

### Gate 6: Documentation
- [ ] `README.md` has accurate setup instructions that a new developer can follow
- [ ] `.env.example` documents all required environment variables
- [ ] Architecture documentation reflects actual implementation

### Gate 7: PR Review
- [ ] At least one code review completed
- [ ] All review comments addressed
- [ ] PR description is complete using the PR template
- [ ] CI pipeline passes on the PR

---

## Appendix: Environment Variables (.env.example)

The following variables should be defined in `.env.example` with placeholder values:

```env
# Django
DJANGO_SECRET_KEY=change-me-to-a-random-secret-key
DJANGO_SETTINGS_MODULE=config.settings.development
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database
POSTGRES_DB=church_history
POSTGRES_USER=church_history_user
POSTGRES_PASSWORD=change-me-to-a-strong-password
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Google OAuth (get from Google Cloud Console)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Frontend
VITE_API_BASE_URL=http://localhost/api

# CORS
CORS_ALLOWED_ORIGINS=http://localhost,http://localhost:3000
```

---

## Appendix: Sequence of Work

Recommended order for implementation:

1. **Kick off T0.1** (App Naming) immediately - it has no dependencies and can run in parallel
2. **T0.2** (Repo & Git) - quick setup, unblocks everything else
3. **T0.3 + T0.5 in parallel** (Django + React) - the two main setup streams
4. **T0.4** (PostgreSQL) - immediately after Django setup
5. **T0.7** (OAuth skeleton) - immediately after Django setup
6. **T0.6** (Docker Compose) - once Django and React are individually working
7. **T0.9 + T0.10 in parallel** (Backend + Frontend tests) - once apps are set up
8. **T0.8** (CI/CD) - once tests exist to run
9. **T0.12** (License Audit) - once all dependencies are finalized
10. **T0.11** (Documentation) - once the app name is chosen and implementation is stable
11. **T0.13** (Integration Verification) - final step before PR
