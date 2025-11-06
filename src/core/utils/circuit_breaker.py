"""Circuit Breaker Pattern Implementation"""

import asyncio
from enum import Enum
from typing import Callable, TypeVar, Optional
from datetime import datetime, timedelta
import logging

T = TypeVar("T")

logger = logging.getLogger(__name__)


class CircuitBreakerState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreakerError(Exception):
    """Circuit breaker is open."""
    pass


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.

    Prevents cascading failures by stopping requests to a failing service.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
        recovery_timeout: int = 30,
        name: str = "circuit_breaker",
    ):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.recovery_timeout = recovery_timeout
        self.name = name

        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.opened_at: Optional[datetime] = None

        self._lock = asyncio.Lock()

    async def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        Call function through circuit breaker.

        Args:
            func: Async function to call
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Result of func

        Raises:
            CircuitBreakerError: If circuit is open
        """
        async with self._lock:
            # Check if we should attempt to recover
            if self.state == CircuitBreakerState.OPEN:
                if self._should_attempt_reset():
                    logger.info(f"Circuit breaker {self.name}: Attempting recovery (half-open)")
                    self.state = CircuitBreakerState.HALF_OPEN
                else:
                    raise CircuitBreakerError(
                        f"Circuit breaker {self.name} is OPEN. "
                        f"Opened at {self.opened_at}, will retry after {self.timeout_seconds}s"
                    )

        # Execute the function
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result

        except Exception as e:
            await self._on_failure(e)
            raise

    async def _on_success(self):
        """Handle successful call."""
        async with self._lock:
            if self.state == CircuitBreakerState.HALF_OPEN:
                logger.info(f"Circuit breaker {self.name}: Recovery successful, closing circuit")
                self.state = CircuitBreakerState.CLOSED

            self.failure_count = 0
            self.last_failure_time = None

    async def _on_failure(self, exception: Exception):
        """Handle failed call."""
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()

            logger.warning(
                f"Circuit breaker {self.name}: Failure {self.failure_count}/{self.failure_threshold} - {str(exception)}"
            )

            if self.state == CircuitBreakerState.HALF_OPEN:
                # Failed during recovery, reopen circuit
                logger.error(f"Circuit breaker {self.name}: Recovery failed, reopening circuit")
                self.state = CircuitBreakerState.OPEN
                self.opened_at = datetime.utcnow()

            elif self.failure_count >= self.failure_threshold:
                # Threshold exceeded, open circuit
                logger.error(
                    f"Circuit breaker {self.name}: Failure threshold exceeded, opening circuit"
                )
                self.state = CircuitBreakerState.OPEN
                self.opened_at = datetime.utcnow()

    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit breaker."""
        if not self.opened_at:
            return False

        elapsed = (datetime.utcnow() - self.opened_at).total_seconds()
        return elapsed >= self.timeout_seconds

    def get_state(self) -> dict:
        """Get current circuit breaker state."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "last_failure": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "opened_at": self.opened_at.isoformat() if self.opened_at else None,
        }

    async def reset(self):
        """Manually reset circuit breaker."""
        async with self._lock:
            logger.info(f"Circuit breaker {self.name}: Manual reset")
            self.state = CircuitBreakerState.CLOSED
            self.failure_count = 0
            self.last_failure_time = None
            self.opened_at = None
