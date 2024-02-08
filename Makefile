args := $(wordlist 2, 100, $(MAKECMDGOALS))

ifeq ($(wildcard "conf/.env"),)
	include conf/.env
endif

APPLICATION_NAME = currency_checker

HELP_FUN = \
	%help; while(<>){push@{$$help{$$2//'options'}},[$$1,$$3] \
	if/^([\w-_]+)\s*:.*\#\#(?:@(\w+))?\s(.*)$$/}; \
    print"$$_:\n", map"  $$_->[0]".(" "x(20-length($$_->[0])))."$$_->[1]\n",\
    @{$$help{$$_}},"\n" for keys %help; \

CODE = currency_checker
TEST = poetry run python3 -m pytest --verbosity=2 --showlocals --log-level=DEBUG

ifndef args
MESSAGE = "No such command (or you pass two or many targets to ). List of possible commands: make help"
else
MESSAGE = "Done"
endif


help: ##@Help Show this help
	@echo -e "Usage: make [target] ...\n"
	@perl -e '$(HELP_FUN)' $(MAKEFILE_LIST)

install:  ##@Setup Install project requirements
	python3 -m pip install poetry
	poetry install

run_api:  ##@Application Run api
	poetry run python3 -m currency_checker.api

run_scheduler:  ##@Application Run scheduler
	poetry run python3 -m currency_checker.scheduler
run_worker:  ##@Application Run workers
	poetry run python3 -m currency_checker.scheduler.broker

up:  ##@AApplication Create databases and app containers with docker-compose
	docker-compose -f docker-compose.yml up -d --remove-orphans

migrate:  ##@Database Create database with docker-compose
	cd currency_checker/infrastructure/migrations && poetry run alembic upgrade head

revision:  ##@Database Create database with docker-compose
	cd currency_checker/infrastructure/migrations && poetry run alembic revision --autogenerate --message $(args)

test:  ##@Testing Test application with pytest
	make db && $(TEST)

test-cov:  ##@Testing Test application with pytest and create coverage report
	make db && $(TEST) --cov=$(APPLICATION_NAME) --cov-report html --cov-fail-under=70

lint:  ##@Code Check code with pylint
	poetry run python3 -m ruff $(CODE) tests
	poetry run python3 -m mypy $(CODE)

format:  ##@Code Reformat code with ruff and black
	poetry run python3 -m ruff $(CODE) tests --fix

clean:  ##@Code Clean directory from garbage files
	rm -fr *.egg-info dist

build:  ##@Docker Build docker container with bot
	docker build  --platform linux/amd64 -f Dockerfile -t currency_checker:latest .

tag:  ##@Docker Create tag on local bot container
	docker tag currency_checker cr.yandex/$(CLOUD__REGISTRY_ID)/currency_checker:latest

push:  ##@Docker Push container with bot to registry
	docker push cr.yandex/$(CLOUD__REGISTRY_ID)/currency_checker:latest

deploy:  ##@Deploy Create vm with docker-compose (change to your credentials first)
	yc compute instance create-with-container \
  --name currency_checker-vm \
  --zone ru-central1-a \
  --ssh-key ~/.ssh/id_ed25519.pub \
  --create-boot-disk size=30 \
  --network-interface subnet-name=defult-ru-central1-a,nat-ip-version=ipv4 \
  --service-account-name $(CLOUD__ACCOUNT_NAME) \
  --docker-compose-file docker-compose.cloud.yaml

%::
	echo $(MESSAGE)
