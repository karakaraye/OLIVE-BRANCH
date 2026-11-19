UV ?= uv
NPM ?= npm
BACKEND_HOST ?= 127.0.0.1
FRONTEND_HOST ?= 127.0.0.1
MANAGE = $(UV) run --locked --project backend python backend/manage.py

.PHONY: install db start frontend migrate test lint build seed

install:
	$(UV) sync --locked --project backend --python 3.12
	$(NPM) --prefix frontend ci

db:
	docker compose up -d --wait db

start:
	$(MANAGE) runserver $(BACKEND_HOST):8000

frontend:
	NEXT_TELEMETRY_DISABLED=1 $(NPM) --prefix frontend run dev -- --hostname $(FRONTEND_HOST)

migrate:
	$(MANAGE) migrate

test:
	DJANGO_SETTINGS_MODULE=config.settings.test $(MANAGE) test tests -v 2
	$(NPM) --prefix frontend test

lint:
	$(UV) run --locked --project backend ruff check backend
	$(UV) run --locked --project backend ruff format --check backend
	$(NPM) --prefix frontend run lint
	$(NPM) --prefix frontend run typecheck

build:
	NEXT_TELEMETRY_DISABLED=1 $(NPM) --prefix frontend run build

seed:
	$(MANAGE) seed_demo --request-id local-demo-v1
