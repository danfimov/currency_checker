args := $(wordlist 2, 100, $(MAKECMDGOALS))

ifeq ($(wildcard "conf/.env"),)
	include conf/.env
endif

.DEFAULT:
	@echo "No such command (or you pass two or many targets to ). List of possible commands: make help"

.DEFAULT_GOAL := help

##@ Help

.PHONY: help
help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target> <arg=value>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m  %s\033[0m\n\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Local development

.PHONY: install
install: ## Install project requirements
	python3 -m pip install poetry
	poetry install

.PHONY: run_api
run_api: ## Run api
	poetry run python3 -m currency_checker.api

.PHONY: run_scheduler
run_scheduler: ## Run scheduler
	poetry run python3 -m currency_checker.scheduler

.PHONY: run_worker
run_worker: ## Run workers
	poetry run python3 -m currency_checker.scheduler.broker

.PHONY: up
up: ## Create databases and app containers with docker-compose
	docker-compose -f docker-compose.yml up -d --remove-orphans

##@ Database

.PHONY: migrate
migrate: ## Create database with docker-compose
	cd currency_checker/infrastructure/migrations && poetry run alembic upgrade head

.PHONY: revision
revision: ## Create database with docker-compose
	cd currency_checker/infrastructure/migrations && poetry run alembic revision --autogenerate --message $(args)

##@ Code Quality

.PHONY: test
test: ## Test app with pytest
	make db && poetry run python3 -m pytest --verbosity=2 --showlocals --log-level=DEBUG

.PHONY: test-cov
test-cov: ## Test app with pytest and create coverage report
	make db && poetry run python3 -m pytest --verbosity=2 --showlocals --log-level=DEBUG --cov=currency_checker --cov-report html --cov-fail-under=70

.PHONY: lint
lint: ## Check code with pylint
	poetry run python3 -m ruff $(CODE) tests
	poetry run python3 -m mypy $(CODE)

.PHONY: format
format: ## Reformat code with ruff and black
	poetry run python3 -m ruff $(CODE) tests --fix

.PHONY: clean
clean: ## Clean directory from garbage files
	rm -fr *.egg-info dist

##@ Docker

.PHONY: build
build: ## Build docker container with bot
	docker build  --platform linux/amd64 -f Dockerfile -t currency_checker:latest .

.PHONY: tag
tag: ## Create tag on local bot container
	docker tag currency_checker cr.yandex/$(CLOUD__REGISTRY_ID)/currency_checker:latest

.PHONY: push
push: ## Push container with bot to registry
	docker push cr.yandex/$(CLOUD__REGISTRY_ID)/currency_checker:latest

##@ Deploy

.PHONY: deploy
deploy: ## Create vm with docker-compose (change to your credentials first)
	yc compute instance create-with-container \
  --name currency_checker-vm \
  --zone ru-central1-a \
  --ssh-key ~/.ssh/id_ed25519.pub \
  --create-boot-disk size=30 \
  --network-interface subnet-name=defult-ru-central1-a,nat-ip-version=ipv4 \
  --service-account-name $(CLOUD__ACCOUNT_NAME) \
  --docker-compose-file docker-compose.cloud.yaml
