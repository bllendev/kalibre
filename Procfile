web: gunicorn bookstore_project.wsgi:application --whitenoise
release: python manage.py migrate && python manage.py collectstatic --noinput
