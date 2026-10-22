"""Structured logging with contextual incident_id tracking."""

import logging
import json
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class JSONFormatter(logging.Formatter):
    """Formats log records as structured JSON."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "incident_id"):
            log_obj["incident_id"] = getattr(record, "incident_id")
        if hasattr(record, "component"):
            log_obj["component"] = getattr(record, "component")
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)


def setup_logger(name: str = "telecom_rca", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
    return logger


logger = setup_logger()


def get_incident_logger(incident_id: str) -> logging.LoggerAdapter:
    """Returns a logger adapter binding the specific incident_id."""
    return logging.LoggerAdapter(logger, {"incident_id": incident_id})
