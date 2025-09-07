from celery import Celery
from app.core.config import settings
from app.ingestion.tasks import ingest_document_sync
import logging

logger = logging.getLogger(__name__)

celery_app = Celery("ai_docs_assistant", broker=settings.REDIS_URL, backend=settings.REDIS_URL)
celery_app.conf.update(
    task_default_queue="default",
    worker_concurrency=settings.CELERY_CONCURRENCY,
)


@celery_app.task(name="ingest_document")
def ingest_document_task(document_id: str):
    try:
        ingest_document_sync(document_id)
    except Exception as e:
        logger.exception("Ingest failed for %s: %s", document_id, e)
        raise
