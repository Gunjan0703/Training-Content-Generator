import logging
import json
import sys
import uuid

class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Optional correlation/request IDs
        if hasattr(record, "request_id"):
            payload["request_id"] = record.request_id
        return json.dumps(payload, ensure_ascii=False)

def configure_logging(level: str = "INFO"):
    logger = logging.getLogger()
    logger.setLevel(level.upper())
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    # Avoid duplicate handlers when re-initializing (e.g., in tests)
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        logger.addHandler(handler)
    return logger

def new_request_id() -> str:
    return str(uuid.uuid4())
