search_engine: ./run_search_engine.sh
release: python manage.py migrate
web: gunicorn config.wsgi:application
worker: celery worker --app=config.celery_app --loglevel=info
