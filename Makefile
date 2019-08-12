#!/usr/bin/env bash
PORT_WEB?=8000
COMPOSE_FILE=local.yml

makemessages:
	docker-compose exec django ./manage.py makemessages -a

compilemessages:
	docker-compose exec django ./manage.py compilemessages

migrate:
	docker-compose exec django ./manage.py makemigrations && docker-compose exec django ./manage.py migrate

shell:
	docker-compose exec django ./manage.py shell

deploy_hard:
	docker-compose stop && docker-compose rm -f && docker-compose up --build

deploy:
	docker-compose up

collectstatic:
	docker-compose exec django ./manage.py collectstatic --noinput

freeze:
	docker-compose exec django pip freeze > requirements.txt

restart_django:
	docker-compose stop django && docker-compose start django

restart_django_hard:
	docker-compose rm django && docker-compose stop django && docker-compose start django

clear_db:
	docker-compose exec django python manage.py flush --noinput

pass_change_admin:
	docker-compose exec django python manage.py changepassword admin

create_superuser:
	docker-compose exec django python manage.py createsuperuser

ipython:
	docker-compose exec django ipython

bash:
	docker-compose exec django bash

rebuild_index:
	docker-compose exec django python manage.py rebuild_index --noinput

update_index:
	docker-compose exec django python manage.py update_index
