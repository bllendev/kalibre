# --- Stage 1: Python setup ---
FROM python:3.8 AS backend

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

# Install dependencies
COPY Pipfile Pipfile.lock /code/
RUN pip install pipenv && pipenv install --system
RUN pip install psycopg2-binary

# Copy project
COPY . /code/

# Expose the port for the application
EXPOSE 8000

# --- Stage 2: Node.js setup ---
FROM node:16 AS frontend

# Set environment to development to ensure devDependencies are installed
ENV NODE_ENV=development

# Set work directory
WORKDIR /app/kalibre

# Copy package.json and yarn.lock
COPY kalibre/package.json kalibre/yarn.lock ./

# Install Node.js dependencies
RUN yarn install --frozen-lockfile

# Copy the rest of the app
COPY kalibre/ .

# Build the React App using Vite.js
RUN yarn run build

# --- Final stage ---
FROM backend as final

# Copy the React app build folder to the Python backend container
COPY --from=frontend /app/kalibre/dist /code/kalibre/build

# Start Celery worker and Django application
CMD (celery -A bookstore_project worker --loglevel=info &) && \
    gunicorn bookstore_project.wsgi:application --whitenoise --bind 0.0.0.0:8000
