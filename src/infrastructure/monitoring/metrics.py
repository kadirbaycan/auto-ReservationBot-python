"""Metrics Collection using Prometheus"""

import os
from typing import Dict, Optional

try:
    from prometheus_client import Counter, Histogram, Gauge, Summary, CollectorRegistry
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    Counter = Histogram = Gauge = Summary = CollectorRegistry = None


class MetricsCollector:
    """Metrics collector for application monitoring."""

    def __init__(self, registry: CollectorRegistry = None):
        if not PROMETHEUS_AVAILABLE:
            self.enabled = False
            return

        self.enabled = os.getenv("METRICS_ENABLED", "true").lower() == "true"
        if not self.enabled:
            return

        self.registry = registry or CollectorRegistry()

        # Define metrics
        self._setup_metrics()

    def _setup_metrics(self):
        """Setup Prometheus metrics."""
        # Request metrics
        self.http_requests_total = Counter(
            "http_requests_total",
            "Total HTTP requests",
            ["method", "endpoint", "status"],
            registry=self.registry,
        )

        self.http_request_duration = Histogram(
            "http_request_duration_seconds",
            "HTTP request duration",
            ["method", "endpoint"],
            registry=self.registry,
        )

        # Booking metrics
        self.booking_attempts_total = Counter(
            "booking_attempts_total",
            "Total booking attempts",
            ["status"],
            registry=self.registry,
        )

        self.booking_duration = Histogram(
            "booking_duration_seconds",
            "Booking process duration",
            registry=self.registry,
        )

        self.active_bookings = Gauge(
            "active_bookings",
            "Number of active bookings",
            registry=self.registry,
        )

        # Client metrics
        self.active_clients = Gauge(
            "active_clients",
            "Number of active clients",
            registry=self.registry,
        )

        # Cloudflare bypass metrics
        self.cloudflare_bypass_attempts = Counter(
            "cloudflare_bypass_attempts_total",
            "Cloudflare bypass attempts",
            ["strategy", "result"],
            registry=self.registry,
        )

        # Database metrics
        self.database_query_duration = Histogram(
            "database_query_duration_seconds",
            "Database query duration",
            ["operation"],
            registry=self.registry,
        )

        # Cache metrics
        self.cache_hits = Counter(
            "cache_hits_total",
            "Cache hits",
            registry=self.registry,
        )

        self.cache_misses = Counter(
            "cache_misses_total",
            "Cache misses",
            registry=self.registry,
        )

    def record_http_request(self, method: str, endpoint: str, status: int, duration: float):
        """Record HTTP request metrics."""
        if not self.enabled:
            return

        self.http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
        self.http_request_duration.labels(method=method, endpoint=endpoint).observe(duration)

    def record_booking_attempt(self, status: str, duration: float = None):
        """Record booking attempt."""
        if not self.enabled:
            return

        self.booking_attempts_total.labels(status=status).inc()
        if duration:
            self.booking_duration.observe(duration)

    def set_active_bookings(self, count: int):
        """Set active bookings gauge."""
        if not self.enabled:
            return
        self.active_bookings.set(count)

    def set_active_clients(self, count: int):
        """Set active clients gauge."""
        if not self.enabled:
            return
        self.active_clients.set(count)

    def record_cloudflare_bypass(self, strategy: str, success: bool):
        """Record Cloudflare bypass attempt."""
        if not self.enabled:
            return

        result = "success" if success else "failure"
        self.cloudflare_bypass_attempts.labels(strategy=strategy, result=result).inc()

    def record_database_query(self, operation: str, duration: float):
        """Record database query duration."""
        if not self.enabled:
            return
        self.database_query_duration.labels(operation=operation).observe(duration)

    def record_cache_hit(self):
        """Record cache hit."""
        if not self.enabled:
            return
        self.cache_hits.inc()

    def record_cache_miss(self):
        """Record cache miss."""
        if not self.enabled:
            return
        self.cache_misses.inc()


# Singleton instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get or create metrics collector instance."""
    global _metrics_collector

    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()

    return _metrics_collector
