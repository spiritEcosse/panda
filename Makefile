#!/usr/bin/env bash
PORT_WEB?=8000
COMPOSE_FILE?=local.yml
PORT_DB?=5432

makemessages:
	docker-compose exec django ./manage.py makemessages -a

compilemessages:
	docker-compose exec django ./manage.py compilemessages

migrate:
	docker-compose exec django ./manage.py makemigrations && docker-compose exec django ./manage.py migrate

shell:
	docker-compose -f ${COMPOSE_FILE} exec django ./manage.py shell

deploy_hard:
	export COMPOSE_FILE=${COMPOSE_FILE} && docker-compose stop && docker-compose rm -f && docker-compose up --build --remove-orphans --scale initial-data=0

stop_rm:
	export COMPOSE_FILE=${COMPOSE_FILE} && docker-compose stop && docker-compose rm -f

rm_volumes:
	docker volume rm -f panda_local_postgres_data
	#panda_local_solr_data

rm_hard: stop_rm rm_volumes

deploy:
	docker-compose -f ${COMPOSE_FILE} up --scale initial-data=0

deploy_build:
	docker-compose -f ${COMPOSE_FILE} up --build --scale initial-data=0

logs:
	docker-compose -f ${COMPOSE_FILE} logs -f

initial-data_bash:
	docker-compose -f ${COMPOSE_FILE} run initial-data bash

initial-data:
	docker-compose -f ${COMPOSE_FILE} up -d postgres
	docker-compose -f ${COMPOSE_FILE} up initial-data

initial-data_logs:
	docker-compose -f ${COMPOSE_FILE} logs initial-data

django_stop_rm:
	docker-compose -f ${COMPOSE_FILE} stop django
	docker-compose -f ${COMPOSE_FILE} rm -f django

django_reupd: django_stop_rm
	docker-compose -f ${COMPOSE_FILE} up -d django

initial_data_stop_rm:
	docker-compose -f ${COMPOSE_FILE} stop initial-data
	docker-compose -f ${COMPOSE_FILE} rm -f initial-data

initial_data_reupd: initial_data_stop_rm
	docker-compose -f ${COMPOSE_FILE} up -d initial-data

install: initial-data deploy_build
#install: initial-data deploy

collectstatic:
	docker-compose exec django ./manage.py collectstatic --noinput

freeze:
	docker-compose -f ${COMPOSE_FILE} exec django pip freeze

restart_django:
	docker-compose stop django && docker-compose start django

restart_django_hard:
	docker-compose rm django && docker-compose stop django && docker-compose start django

clear_db:
	docker-compose exec django python manage.py flush --noinput

pass_change_admin:
	docker-compose exec django python manage.py changepassword admin

create_superuser:
	docker-compose -f ${COMPOSE_FILE} run --rm django python manage.py createsuperuser

ipython:
	docker-compose -f ${COMPOSE_FILE} exec django ipython

bash:
	docker-compose -f ${COMPOSE_FILE} exec django bash

rebuild_index:
	docker-compose -f ${COMPOSE_FILE} run --rm django python manage.py rebuild_index --noinput

update_index:
	docker-compose -f ${COMPOSE_FILE} run --rm django python manage.py update_index


# Solr
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

build_solr_schema: solr-create-collection
	rm -fr schema.xml
	export COMPOSE_FILE=${COMPOSE_FILE} && docker-compose build django && docker-compose run --rm django python manage.py build_solr_schema > schema.xml
