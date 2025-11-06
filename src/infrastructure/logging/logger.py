"""Structured Logging Configuration"""

import os
import sys
import logging
from typing import Dict, Any
from pathlib import Path
import uuid

try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False
    structlog = None


class LoggerAdapter:
    """Logger adapter for structured logging."""

    def __init__(self, logger, context: Dict[str, Any] = None):
        self.logger = logger
        self.context = context or {}

    def bind(self, **kwargs) -> "LoggerAdapter":
        """Bind context variables to logger."""
        new_context = {**self.context, **kwargs}
        return LoggerAdapter(self.logger, new_context)

    def _log(self, level: str, message: str, **kwargs):
        """Log with context."""
        log_data = {**self.context, **kwargs, "message": message}
        getattr(self.logger, level)(message, extra=log_data)

    def debug(self, message: str, **kwargs):
        self._log("debug", message, **kwargs)

    def info(self, message: str, **kwargs):
        self._log("info", message, **kwargs)

    def warning(self, message: str, **kwargs):
        self._log("warning", message, **kwargs)

    def error(self, message: str, **kwargs):
        self._log("error", message, **kwargs)

    def critical(self, message: str, **kwargs):
        self._log("critical", message, **kwargs)


def setup_logging(
    log_level: str = None,
    log_file: str = None,
    structured: bool = True,
) -> None:
    """Setup application logging."""
    level = log_level or os.getenv("LOG_LEVEL", "INFO")
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    log_file_path = log_file or log_dir / "vfs_automation.log"

    # Configure standard logging
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file_path),
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Configure structlog if available
    if STRUCTLOG_AVAILABLE and structured:
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(
                getattr(logging, level.upper())
            ),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )


def get_logger(name: str, **context) -> LoggerAdapter:
    """
    Get logger instance with optional context.

    Args:
        name: Logger name (usually __name__)
        **context: Additional context to bind to logger

    Returns:
        LoggerAdapter instance
    """
    logger = logging.getLogger(name)

    # Add correlation ID if not present
    if "correlation_id" not in context:
        context["correlation_id"] = str(uuid.uuid4())

    return LoggerAdapter(logger, context)


def get_correlation_id() -> str:
    """Generate a new correlation ID."""
    return str(uuid.uuid4())
