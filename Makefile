.PHONY: help build up down restart logs shell clean test lint format migrate seed

# Colors
BLUE := \033[0;34m
GREEN := \033[0;32m
NC := \033[0m

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(BLUE)%-20s$(NC) %s\n", $$1, $$2}'

# Docker commands
build: ## Build all Docker images
	docker compose build --parallel

up: ## Start all services
	docker compose up -d
	@echo "$(GREEN)ExamSaaS is running at http://localhost$(NC)"

down: ## Stop all services
	docker compose down

restart: down up ## Restart all services

logs: ## Show logs (all services)
	docker compose logs -f

logs-flask: ## Show Flask logs
	docker compose logs -f flask

logs-celery: ## Show Celery worker logs
	docker compose logs -f celery-worker

# Development
dev: ## Start development environment
	docker compose up -d flask redis mongo
	@echo "$(GREEN)Backend running at http://localhost:5000$(NC)"

dev-frontend: ## Start frontend dev server
	cd frontend && npm run dev

shell: ## Open Flask shell
	docker compose exec flask flask shell

mongo-shell: ## Open MongoDB shell
	docker compose exec mongo mongosh -u $(MONGO_USER) -p $(MONGO_PASSWORD) examsaas

redis-cli: ## Open Redis CLI
	docker compose exec redis redis-cli -a $(REDIS_PASSWORD)

# Testing
test: ## Run all tests
	cd backend && pytest tests/ -v

test-coverage: ## Run tests with coverage
	cd backend && pytest tests/ -v --cov=app --cov-report=html

# Code quality
lint: ## Run linters
	cd backend && flake8 app/ --max-line-length=120 --ignore=E501,W503
	cd frontend && npm run lint

format: ## Format code
	cd backend && black app/
	cd frontend && npm run format

# Database
migrate: ## Run database migrations
	cd backend && python -c "from seed import create_indexes; create_indexes()"

seed: ## Seed the database
	cd backend && python seed.py

clean: ## Clean up containers, volumes, and build artifacts
	docker compose down -v --remove-orphans
	rm -rf backend/__pycache__ frontend/node_modules/.vite
	rm -rf backend/dist frontend/dist

# Production
deploy: ## Deploy to production (requires PRODUCTION=true)
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

pull: ## Pull latest images
	docker compose pull

# Utilities
health: ## Check health of all services
	@curl -s http://localhost/health | jq . || echo "Flask not healthy"
	@docker compose ps

port-check: ## Check if required ports are available
	@echo "Checking ports 5000, 5173, 27017, 6379..."
	@for port in 5000 5173 27017 6379; do \
		if lsof -Pi :$$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then \
			echo "Port $$port: IN USE"; \
		else \
			echo "Port $$port: AVAILABLE"; \
		fi; \
	done
