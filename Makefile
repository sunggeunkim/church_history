# =============================================================================
# Toledot - Development Commands
# =============================================================================

.PHONY: help up down restart logs build test lint format clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ---------------------------------------------------------------------------
# Docker
# ---------------------------------------------------------------------------

up: ## Start all services
	docker compose up -d

up-build: ## Build and start all services
	docker compose up -d --build

down: ## Stop all services
	docker compose down

restart: ## Restart all services
	docker compose restart

logs: ## Tail logs for all services
	docker compose logs -f

logs-backend: ## Tail backend logs
	docker compose logs -f backend

logs-frontend: ## Tail frontend logs
	docker compose logs -f frontend

# ---------------------------------------------------------------------------
# Backend
# ---------------------------------------------------------------------------

migrate: ## Run Django migrations
	docker compose exec backend python manage.py migrate

makemigrations: ## Create new migrations
	docker compose exec backend python manage.py makemigrations

shell: ## Open Django shell
	docker compose exec backend python manage.py shell

# ---------------------------------------------------------------------------
# Testing
# ---------------------------------------------------------------------------

test: test-backend test-frontend ## Run all tests

test-backend: ## Run backend tests
	cd backend && python -m pytest -v

test-frontend: ## Run frontend tests
	cd frontend && npm run test

# ---------------------------------------------------------------------------
# Linting & Formatting
# ---------------------------------------------------------------------------

lint: lint-backend lint-frontend ## Run all linters

lint-backend: ## Lint backend (ruff)
	cd backend && ruff check .

lint-frontend: ## Lint frontend (ESLint)
	cd frontend && npm run lint

format: format-backend format-frontend ## Format all code

format-backend: ## Format backend (ruff)
	cd backend && ruff format .

format-frontend: ## Format frontend (Prettier)
	cd frontend && npm run format

# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

clean: ## Remove build artifacts and caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf frontend/dist frontend/node_modules/.cache
