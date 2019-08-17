release: python manage.py migrate
rebuild_index: python manage.py rebuild_index --noinput
elasticsearch: /app/.heroku/vendor/elasticsearch/bin/elasticsearch
web: gunicorn config.wsgi:application
worker: celery worker --app=config.celery_app --loglevel=info
