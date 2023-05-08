# Pull base image
FROM python:3.8

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        gcc \
        g++ \
        git \
        libsm6 \
        libxext6 \
        libxrender-dev \
        python3-dev \
        rabbitmq-server \
        redis-server \
    && rm -rf /var/lib/apt/lists/*

# Set up RabbitMQ
RUN rabbitmq-plugins enable rabbitmq_management

# Set work directory
WORKDIR /code

# Install dependencies
COPY Pipfile Pipfile.lock /code/

RUN pip install pipenv && pipenv install --system

RUN pip install psycopg2-binary

# Copy project
COPY . /code/

# RUN  python -m textblob.download_corpora

# Expose the ports for the application and RabbitMQ management
EXPOSE 8000 15672

# Start Redis server, Celery worker, RabbitMQ server, and Django application
CMD (redis-server &) && \
    (rabbitmq-server &) && \
    (celery -a bookstore_project worker --loglevel=info &) && \
    (sleep 5) && \
    python manage.py runserver 0.0.0.0:8000
