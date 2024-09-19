DC = docker compose
EXEC = docker exec -it
LOGS = docker logs
ENV = --env-file fastapi_solution/.env
TEST_ENV = --env-file tests/functional/.env
APP_FILE = docker_compose/app.yaml
TEST_APP_FILE = docker_compose/tests_app.yaml
APP_CONTAINER = backend

.PHONY: app
app:
	${DC} -f ${APP_FILE} ${ENV} up --build -d

.PHONY: app-down
app-down:
	${DC} -f ${APP_FILE} down

.PHONY: app-shell
app-shell:
	${EXEC} ${APP_CONTAINER} bash

.PHONY: app-logs
app-logs:
	${LOGS} ${APP_CONTAINER} -f

.PHONY: app-tests
app-tests:
	${DC} -f ${TEST_APP_FILE} ${TEST_ENV} up --build -d

.PHONY: app-tests-down
app-tests-down:
	${DC} -f ${TEST_APP_FILE} down

