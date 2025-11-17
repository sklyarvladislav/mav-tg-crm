REPOSITORY=github.com/sklyarvladislav/mav-tg-crm


TAG=${REPOSITORY}:${VESION}
TARGET=development-image

GID=$(shell id -g)
UID=$(shell id -u)

compose:
	docker-compose -f ./infra/docker-compose.yaml up --build -d --remove-orphans

watch:
	docker-compose -f ./infra/docker-compose.yaml down
	docker-compose -f ./infra/docker-compose.yaml up --build --watch

down:
	docker-compose -f ./infra/docker-compose.yaml down

lint:
	uv run ruff check --fix
	uv run ruff format

upgrade:
	uv run alembic upgrade head

downgrade:
	uv run alembic downgrade -1

migration:
	uv run alembic revision --autogenerate -m $(MSG)
	uv run alembic upgrade head
