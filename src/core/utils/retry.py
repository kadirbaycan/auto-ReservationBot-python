"""Retry Mechanisms with Exponential Backoff"""

import asyncio
from typing import Callable, TypeVar, Optional, Type, Tuple
from dataclasses import dataclass
import logging

T = TypeVar("T")

logger = logging.getLogger(__name__)


@dataclass
class RetryConfig:
    """Retry configuration."""

    max_attempts: int = 5
    initial_delay: float = 1.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    exceptions: Tuple[Type[Exception], ...] = (Exception,)


async def retry_async(
    func: Callable[..., T],
    config: RetryConfig = None,
    *args,
    **kwargs,
) -> T:
    """
    Retry an async function with exponential backoff.

    Args:
        func: Async function to retry
        config: Retry configuration
        *args: Positional arguments for func
        **kwargs: Keyword arguments for func

    Returns:
        Result of func

    Raises:
        Last exception if all retries fail
    """
    cfg = config or RetryConfig()
    delay = cfg.initial_delay
    last_exception = None

    for attempt in range(1, cfg.max_attempts + 1):
        try:
            logger.debug(f"Attempt {attempt}/{cfg.max_attempts} for {func.__name__}")
            result = await func(*args, **kwargs)
            if attempt > 1:
                logger.info(f"Success on attempt {attempt} for {func.__name__}")
            return result

        except cfg.exceptions as e:
            last_exception = e
            logger.warning(
                f"Attempt {attempt}/{cfg.max_attempts} failed for {func.__name__}: {str(e)}"
            )

            if attempt < cfg.max_attempts:
                logger.debug(f"Retrying in {delay:.2f} seconds...")
                await asyncio.sleep(delay)

                # Calculate next delay with exponential backoff
                delay = min(delay * cfg.backoff_factor, cfg.max_delay)
            else:
                logger.error(f"All {cfg.max_attempts} attempts failed for {func.__name__}")

    # All retries exhausted
    if last_exception:
        raise last_exception


def retry_with_config(config: RetryConfig = None):
    """
    Decorator for retry with config.

    Usage:
        @retry_with_config(RetryConfig(max_attempts=3))
        async def my_function():
            ...
    """

    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            return await retry_async(func, config, *args, **kwargs)

        return wrapper

    return decorator
