FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir -e .
COPY app ./app
CMD ["celery", "-A", "app.ingestion.worker:celery_app", "worker", "--loglevel=INFO"]
