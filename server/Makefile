# Build configuration
# -------------------

APP_NAME := $(shell sed -n 's/^ *name.*=.*"\([^"]*\)".*/\1/p' pyproject.toml)
APP_VERSION := $(shell sed -n 's/^ *version.*=.*"\([^"]*\)".*/\1/p' pyproject.toml)
GIT_REVISION = $(shell git rev-parse HEAD)

# Introspection targets
# ---------------------

.PHONY: help
help: header targets

.PHONY: header
header:
	@echo "\033[34mEnvironment\033[0m"
	@echo "\033[34m---------------------------------------------------------------\033[0m"
	@printf "\033[33m%-23s\033[0m" "APP_NAME"
	@printf "\033[35m%s\033[0m" $(APP_NAME)
	@echo ""
	@printf "\033[33m%-23s\033[0m" "APP_VERSION"
	@printf "\033[35m%s\033[0m" $(APP_VERSION)
	@echo ""
	@printf "\033[33m%-23s\033[0m" "GIT_REVISION"
	@printf "\033[35m%s\033[0m" $(GIT_REVISION)
	@echo "\n"

.PHONY: targets
targets:
	@echo "\033[34mDevelopment Targets\033[0m"
	@echo "\033[34m---------------------------------------------------------------\033[0m"
	@perl -nle'print $& if m{^[a-zA-Z_-]+:.*?## .*$$}' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}'

# Development targets
# -------------

.PHONY: install
install: ## Install dependencies
	poetry install

.PHONY: run
run: start

.PHONY: start
start: ## Starts the server
	@eval "$(shell sed 's/=.*//' .env | xargs echo export)"
	poetry run python main.py

.PHONY: migrate
migrate: ## Run the migrations
	@eval "$(shell sed 's/=.*//' .env | xargs echo export)"
	poetry run alembic upgrade head

.PHONY: rollback
rollback: ## Rollback migrations one level
	@eval "$(shell sed 's/=.*//' .env | xargs echo export)"
	poetry run alembic downgrade -1

.PHONY: reset-database
reset-database: ## Rollback all migrations
	@eval "$(shell sed 's/=.*//' .env | xargs echo export)"
	poetry run alembic downgrade base

.PHONY: generate-migration 
generate-migration: ## Generate a new migration
	@eval "$(shell sed 's/=.*//' .env | xargs echo export)"
	@read -p "Enter migration message: " message; \
	poetry run alembic revision --autogenerate -m "$$message"

# Check, lint and format targets
# ------------------------------

.PHONY: check
check: check-format lint

.PHONY: check-format
check-format: ## Dry-run code formatter
	poetry run black ./ --check
	poetry run isort ./ --profile black --check

.PHONY: lint
lint: ## Run linter
	poetry run pylint ./api ./app ./core

.PHONY: format
format: ## Run code formatter
	poetry run black ./
	poetry run isort ./ --profile black

.PHONY: check-lockfile
check-lockfile: ## Compares lock file with pyproject.toml
	poetry lock --check

.PHONY: test
test: ## Run the test suite
	@eval "$(shell sed 's/=.*//' .env | xargs echo export)"
	poetry run pytest -vv -rs --cache-clear ./
