"""Celery application instance for asynchronous RCA execution and graph analysis tasks."""

import os
from celery import Celery
from backend.config import get_settings

settings = get_settings()

celery_app = Celery(
    "graphtriage",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "backend.routes.rca"
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,        # 5 minute hard limit
    task_soft_time_limit=240,   # 4 minute soft limit
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=False,
    broker_transport_options={"max_retries": 1, "socket_timeout": 0.5, "socket_connect_timeout": 0.5},
    redis_socket_timeout=0.5,
    redis_socket_connect_timeout=0.5,
    task_routes={
        "backend.routes.rca.execute_rca_task": {"queue": "rca_tasks"},
    }
)

if __name__ == "__main__":
    celery_app.start()
