up:
	docker compose up --build -d

run: up

down:
	docker compose down -v

local:
	docker compose -f docker-compose.local.yml up --build -d && cd ./app && python manage.py runserver

migrations:
	docker exec -ti movies python manage.py makemigrations

migrate:
	docker exec -ti movies python manage.py migrate

superuser:
	docker exec -ti movies python manage.py createsuperuser

.DEFAULT_GOAL := up