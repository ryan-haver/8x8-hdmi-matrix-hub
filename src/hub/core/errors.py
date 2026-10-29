"""Public references for unexpected errors; details stay in private server logs."""

import logging
import uuid


def safe_action_error(exc: Exception, context: str, *, logger: logging.Logger) -> tuple[str, str]:
    """Log the original traceback and return a neutral message with its reference."""
    correlation_id = uuid.uuid4().hex[:8]
    logger.error("[%s] %s: %s", correlation_id, context, exc, exc_info=(type(exc), exc, exc.__traceback__))
    return f"Internal server error (ref: {correlation_id})", correlation_id
