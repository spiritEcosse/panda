#!/usr/bin/env bash
PORT_WEB?=8000
COMPOSE_FILE?=local.yml
PORT_DB?=5432
PROJECT?=test_panda
COMMIT_MESSAGE?=
REPO=shevchenkoigor/panda
REPO_TEST=shevchenkoigor/panda_test
DOCKER_FILE=compose/local/django/Dockerfile
DOCKER_FILE_TEST=compose/test/django/Dockerfile
APP?=

makemessages:
	docker-compose -f ${COMPOSE_FILE} exec django ./manage.py makemessages -a

compilemessages:
	docker-compose exec django ./manage.py compilemessages

migrate:
	docker-compose exec django ./manage.py makemigrations && docker-compose exec django ./manage.py migrate

shell:
	docker-compose -f ${COMPOSE_FILE} exec django ./manage.py shell

pytest:
	docker-compose -f ${COMPOSE_FILE} run --rm django pytest

tests:
	docker-compose -f ${COMPOSE_FILE} run --rm django tests

deploy_hard:
	export COMPOSE_FILE=${COMPOSE_FILE} && docker-compose stop && docker-compose rm -f && docker-compose up --build --remove-orphans --scale initial-data=0

tagged_django_image:
	sed -i "s%panda:.*%panda:`git rev-parse --abbrev-ref HEAD`%g" ${COMPOSE_FILE}
	sed -i "s%panda:.*%panda:`git rev-parse --abbrev-ref HEAD`_test%g" test.yml

build_django:
	docker build -t ${REPO}:`git rev-parse --abbrev-ref HEAD` -f ${DOCKER_FILE} .

commit: tagged_django_image
	git add .
	git commit -m '${COMMIT_MESSAGE}'
	git branch --set-upstream-to=origin/`git rev-parse --abbrev-ref HEAD` `git rev-parse --abbrev-ref HEAD`
	git push
	docker build -t ${REPO}:`git rev-parse --abbrev-ref HEAD` -f ${DOCKER_FILE} .
	docker push ${REPO}:`git rev-parse --abbrev-ref HEAD`
	docker build -t ${REPO}:`git rev-parse --abbrev-ref HEAD`_test -f ${DOCKER_FILE_TEST} .
	docker push ${REPO}:`git rev-parse --abbrev-ref HEAD`_test

docker_build_push:
	docker build -t ${REPO}:`git rev-parse --abbrev-ref HEAD` -f ${DOCKER_FILE} .
	docker push ${REPO}:`git rev-parse --abbrev-ref HEAD`
	docker build -t ${REPO}:`git rev-parse --abbrev-ref HEAD`_test -f ${DOCKER_FILE_TEST} .
	docker push ${REPO}:`git rev-parse --abbrev-ref HEAD`_test

docker_pull:
	docker pull ${REPO}:`git rev-parse --abbrev-ref HEAD`

deploy_hard:
	export COMPOSE_FILE=${COMPOSE_FILE} && docker-compose stop && docker-compose rm -f && docker-compose up --build --remove-orphans --scale initial-data=0

stop_rm:
	export COMPOSE_FILE=${COMPOSE_FILE} && docker-compose stop && docker-compose rm -f

rm_volumes:
	docker volume rm -f panda_local_postgres_data panda_local_postgres_data_backups
	#panda_local_solr_data

rm_hard: stop_rm rm_volumes

deploy:
	docker-compose -f ${COMPOSE_FILE} up --scale initial-data=0

build_local:
	docker build -t panda:`git rev-parse --abbrev-ref HEAD` -f compose/local/django/Dockerfile .

deploy_build:
	docker-compose -f ${COMPOSE_FILE} up --build --scale initial-data=0

logs:
	docker-compose -f ${COMPOSE_FILE} logs -f

initial-data_bash:
	docker-compose -f ${COMPOSE_FILE} run initial-data bash

initial-data:
	docker-compose -f ${COMPOSE_FILE} up initial-data

initial-data_logs:
	docker-compose -f ${COMPOSE_FILE} logs initial-data

django_stop_rm:
	docker-compose -f ${COMPOSE_FILE} stop django
	docker-compose -f ${COMPOSE_FILE} rm -f django

django-logs:
	docker-compose -f ${COMPOSE_FILE} logs django

kibana-logs:
	docker-compose -f ${COMPOSE_FILE} logs kibana

elasticsearch_logs:
	docker-compose -f ${COMPOSE_FILE} logs elasticsearch

django_reupd: django_stop_rm
	docker-compose -f ${COMPOSE_FILE} up -d django

initial_data_stop_rm:
	docker-compose -f ${COMPOSE_FILE} stop initial-data
	docker-compose -f ${COMPOSE_FILE} rm -f initial-data

initial_data_reupd: initial_data_stop_rm
	docker-compose -f ${COMPOSE_FILE} up -d initial-data

#install: initial-data deploy_build
install: deploy_build

collectstatic:
	docker-compose -f ${COMPOSE_FILE} run --rm django ./manage.py collectstatic --noinput

freeze:
	docker-compose -f ${COMPOSE_FILE} exec django pip freeze

restart_django:
	export COMPOSE_FILE=${COMPOSE_FILE} && docker-compose stop django && docker-compose start django

restart_django_hard:
	docker-compose rm django && docker-compose stop django && docker-compose start django

clear_db:
	docker-compose exec django python manage.py flush --noinput

pass_change_admin:
	docker-compose exec django python manage.py changepassword admin

create_superuser:
	docker-compose -f ${COMPOSE_FILE} run --rm django python manage.py createsuperuser

startapp:
	docker-compose -f ${COMPOSE_FILE} run --rm django python manage.py startapp ${APP}
	sudo chown igor:users -R ${APP}
	mv ${APP} panda

ipython:
	docker-compose -f ${COMPOSE_FILE} run --rm django ipython

bash:
	docker-compose -f ${COMPOSE_FILE} run --rm django sh

bash_test:
	docker-compose -f ${COMPOSE_FILE} -p ${PROJECT} run --rm django sh

sh:
	docker-compose -f ${COMPOSE_FILE} run --rm django sh

rebuild_index:
	docker-compose -f ${COMPOSE_FILE} run --rm django python manage.py rebuild_index --noinput

update_index:
	docker-compose -f ${COMPOSE_FILE} run --rm django python manage.py update_index

django_populate_countries:
	docker-compose -f ${COMPOSE_FILE} run --rm django python manage.py oscar_populate_countries

PYTEST = py.test

venv: ## Install test requirements
	docker-compose -f ${COMPOSE_FILE} -p ${PROJECT} run django pip install -r docs/requirements.txt

install-migrations-testing-requirements: ## Install migrations testing requirements
	pip install -r requirements_migrations.txt

##################
# Tests and checks
##################
#test: venv ## Run tests
test:
	docker-compose -f ${COMPOSE_FILE} -p ${PROJECT} run --rm django $(PYTEST)

retest: venv ## Run failed tests only
	$(PYTEST) --lf

coverage_unit:
	$(PYTEST) --cov=panda -m unit tests/panda/

panda_integration:
	$(PYTEST) -m integration tests/panda/

coverage_unit_html:
	$(PYTEST) --cov=panda --cov-report=html -m unit tests/panda/

coverage_panda_all:
	$(PYTEST) --cov=panda tests/panda/

lint: ## Run flake8 and isort checks
	flake8 src/oscar/
	flake8 tests/
	isort -q --recursive --diff src/
	isort -q --recursive --diff tests/

test_migrations: ## Tests migrations
	./test_migrations.sh


# Solr
# locally

solr-install:
	wget http://archive.apache.org/dist/lucene/solr/4.7.2/solr-4.7.2.tgz
	tar xzf solr-4.7.2.tgz
	./manage.py build_solr_schema > solr-4.7.2/example/solr/collection1/conf/schema.xml
	cd solr-4.7.2/example
	java -jar start.jar

rm_volume_solr:
	docker volume rm -f panda_local_solr_data

solr-bash:
	docker-compose -f ${COMPOSE_FILE} run solr bash

solr-logs:
	docker-compose -f ${COMPOSE_FILE} logs solr

solr_stop_rm:
	export COMPOSE_FILE=${COMPOSE_FILE} && docker-compose stop solr && docker-compose rm -f solr

solr-reupd: solr_stop_rm
	docker-compose -f ${COMPOSE_FILE} up -d --build solr

solr-create-collection: solr_stop_rm rm_volume_solr
	export COMPOSE_FILE=${COMPOSE_FILE} && docker-compose up -d --build solr && docker-compose exec solr solr create -c panda

build_solr_schema:
	rm -fr schema.xml
	export COMPOSE_FILE=${COMPOSE_FILE} && docker-compose build django && docker-compose run --rm django python manage.py build_solr_schema > schema.xml

clean: ## Remove files not in source control
	find . -type f -name "*.pyc" -delete
	rm -rf nosetests.xml coverage.xml htmlcov *.egg-info *.pdf dist violations.txt

run_tests:
	rm -fr tests/public/media/products/
	$(PYTEST)
