release: export DJANGO_SETTINGS_MODULE=config.settings.production && python manage.py migrate
web: gunicorn config.wsgi:application
worker: celery worker --app=config.celery_app --loglevel=info

