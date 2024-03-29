# Set Base Image
FROM python:3.11.5 AS backend

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
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /code

# Copy requirements file to the docker image and install packages
# COPY Pipfile /code/
COPY requirements.txt /code/

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install psycopg2-binary \
    && pip install psycopg2


# Copy the rest of the project's code to the Docker image
COPY . /code/

# Expose the port for the application
EXPOSE 8000

# Start Celery worker and Django application
CMD (celery -A bookstore_project worker --loglevel=info &) && \
    gunicorn bookstore_project.wsgi:application --whitenoise --bind 0.0.0.0:8000
