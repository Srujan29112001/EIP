.PHONY: help install start stop restart logs clean test

help:
	@echo "EIP - Entrepreneurship Intelligence Platform"
	@echo ""
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make start      - Start all services with Docker Compose"
	@echo "  make stop       - Stop all services"
	@echo "  make restart    - Restart all services"
	@echo "  make logs       - View logs"
	@echo "  make clean      - Clean up containers and volumes"
	@echo "  make init-db    - Initialize database"
	@echo "  make test       - Run tests"
	@echo "  make dev        - Start in development mode"

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

start:
	@echo "Starting all services..."
	docker-compose up -d
	@echo "Services started!"
	@echo "Frontend: http://localhost:8501"
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

stop:
	@echo "Stopping all services..."
	docker-compose down

restart:
	@echo "Restarting all services..."
	docker-compose restart

logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

clean:
	@echo "Cleaning up..."
	docker-compose down -v
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

init-db:
	@echo "Initializing database..."
	docker-compose exec backend python scripts/init_db.py
	docker-compose exec backend python scripts/create_admin.py

test:
	@echo "Running tests..."
	pytest backend/tests -v

dev:
	@echo "Starting development environment..."
	@echo "Starting databases..."
	docker-compose up -d postgres mongodb redis neo4j kafka zookeeper
	@echo "Databases started!"
	@echo ""
	@echo "Start backend: cd backend && uvicorn app.main:app --reload"
	@echo "Start frontend: cd frontend && streamlit run app.py"

build:
	@echo "Building Docker images..."
	docker-compose build

ps:
	docker-compose ps

shell-backend:
	docker-compose exec backend /bin/bash

shell-db:
	docker-compose exec postgres psql -U eip_user -d eip_db
