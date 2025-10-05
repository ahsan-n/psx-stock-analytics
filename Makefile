.PHONY: setup dev stop clean migrate seed test lint help

help:
	@echo "PSX Stock Analytics Platform - Development Commands"
	@echo ""
	@echo "  make setup       - Initial setup (copy .env, install dependencies)"
	@echo "  make dev         - Start development environment"
	@echo "  make stop        - Stop all containers"
	@echo "  make clean       - Stop and remove containers, volumes"
	@echo "  make migrate     - Run database migrations"
	@echo "  make seed        - Seed mock financial data"
	@echo "  make test        - Run test suite"
	@echo "  make lint        - Run linting"
	@echo "  make logs        - View logs from all services"
	@echo "  make shell-db    - Open PostgreSQL shell"
	@echo "  make shell-api   - Open backend shell"
	@echo ""

setup:
	@echo "🚀 Setting up PSX Analytics Platform..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Created .env file"; \
	else \
		echo "⚠️  .env already exists"; \
	fi
	@mkdir -p data/reports
	@echo "✅ Created data directories"
	@echo "✅ Setup complete! Run 'make dev' to start"

dev:
	@echo "🏗️  Starting development environment..."
	docker-compose up --build

stop:
	@echo "🛑 Stopping containers..."
	docker-compose stop

clean:
	@echo "🧹 Cleaning up..."
	docker-compose down -v
	@echo "✅ Cleanup complete"

migrate:
	@echo "🔄 Running database migrations..."
	docker-compose exec backend alembic upgrade head
	@echo "✅ Migrations complete"

seed:
	@echo "🌱 Seeding mock data..."
	docker-compose exec backend python -m app.seed
	@echo "✅ Seeding complete"

test:
	@echo "🧪 Running tests..."
	docker-compose exec backend pytest
	@echo "✅ Tests complete"

lint:
	@echo "🔍 Running linters..."
	docker-compose exec backend black app/ --check
	docker-compose exec backend ruff app/
	@echo "✅ Linting complete"

logs:
	docker-compose logs -f

shell-db:
	docker-compose exec db psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

shell-api:
	docker-compose exec backend bash
