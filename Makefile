PROJECT_NAME=fastapi-project

COMPOSE=docker compose
BASE_FILE=-f docker-compose.yml
OVERRIDE_FILE=-f docker-compose.override.yml

.PHONY: help \
        up-local down-local restart-local \
        up-staging down-staging \
        up-prod down-prod \
        logs ps config

help:
	@echo ""
	@echo "Available commands:"
	@echo "  make up-local       Start local dev (with override)"
	@echo "  make down-local     Stop local dev"
	@echo "  make up-staging     Start staging"
	@echo "  make down-staging   Stop staging"
	@echo "  make up-prod        Start production"
	@echo "  make down-prod      Stop production"
	@echo "  make logs           Show logs"
	@echo "  make ps             Show containers"
	@echo "  make config         Show merged config"
	@echo ""

# ---------- LOCAL (dev) ----------

up-local:
	ENVIRONMENT=local $(COMPOSE) $(BASE_FILE) $(OVERRIDE_FILE) up -d

down-local:
	ENVIRONMENT=local $(COMPOSE) down

restart-local:
	$(MAKE) down-local
	$(MAKE) up-local

# ---------- STAGING ----------

up-staging:
	ENVIRONMENT=staging $(COMPOSE) $(BASE_FILE) up -d

down-staging:
	ENVIRONMENT=staging $(COMPOSE) down

# ---------- PRODUCTION ----------

up-prod:
	ENVIRONMENT=production $(COMPOSE) $(BASE_FILE) up -d

down-prod:
	ENVIRONMENT=production $(COMPOSE) down

# ---------- UTILS ----------

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

config:
	$(COMPOSE) $(BASE_FILE) $(OVERRIDE_FILE) config
