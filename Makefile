.PHONY: build up down restart logs logs-auth logs-orchestrator logs-agents logs-gateway migrate

build:
	docker compose build

up:
	docker compose up --build -d

down:
	docker compose down

restart:
	docker compose down
	docker compose up --build -d

logs:
	docker compose logs -f

logs-auth:
	docker compose logs -f auth-service

logs-orchestrator:
	docker compose logs -f orchestrator-service

logs-agents:
	docker compose logs -f agents-service

logs-gateway:
	docker compose logs -f gateway

migrate:
	docker compose exec auth-service alembic upgrade head
	docker compose exec orchestrator-service alembic upgrade head

clean:
	docker compose down -v