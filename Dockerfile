# ===== Etapa 1: construir el frontend (Node) =====
FROM node:22-alpine AS node
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install --include=dev
COPY frontend/ frontend/
RUN npm run build

# ===== Etapa 2: entorno de Python (producción) =====
FROM python:3.12-slim AS python

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.prod

WORKDIR /app

# Dependencias de sistema para psycopg
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Arte del frontend desde la etapa Node
COPY --from=node /app/static/js/dist/ static/js/dist/
COPY --from=node /app/static/css/dist/ static/css/dist/

RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "config.wsgi", "--bind", "0.0.0.0:8000", "--workers", "3"]
