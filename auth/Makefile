.PHONY: up down local lint migrations migrate superuser

up:
	docker compose up --build

down:
	docker compose down -v --remove-orphans

local:
	docker compose -f local-docker-compose.yml up -d --build

lint:
	ruff format .
	ruff check . --fix --show-fixes

migrations:
	cd src; alembic revision --autogenerate -m $(m)

migrate:
	cd src; alembic upgrade head

superuser:
	python ./src/app/commands/createsuperuser.py

tests:
	docker compose -f test-docker-compose.yml up -d
	docker build -t test-auth:latest --file ./src/TestDockerfile ./src
	docker run --network test-auth --env-file ./src/.test.env test-auth:latest
	docker compose -f test-docker-compose.yml down -v --remove-orphans
	docker ps -a | grep 'test-auth' | awk '{print $$1}' | xargs docker rm

.DEFAULT_GOAL := up