"""Prometheus monitoring and metrics for x-maqina"""

import logging
import time
from functools import wraps
from typing import Callable, Any, Optional

try:
    from prometheus_client import (
        Counter,
        Gauge,
        Histogram,
        Summary,
        CollectorRegistry,
        generate_latest,
        CONTENT_TYPE_LATEST,
    )
except ImportError:
    Counter = Gauge = Histogram = Summary = None
    CollectorRegistry = None

logger = logging.getLogger(__name__)


class MetricsRegistry:
    """Central Prometheus metrics registry"""

    def __init__(self):
        """Initialize metrics registry"""
        if not Counter:
            logger.warning("Prometheus client not available")
            return

        self.registry = CollectorRegistry()

        # Request metrics
        self.request_count = Counter(
            "xmaqina_requests_total",
            "Total requests",
            ["method", "endpoint", "status"],
            registry=self.registry,
        )

        self.request_duration = Histogram(
            "xmaqina_request_duration_seconds",
            "Request duration in seconds",
            ["method", "endpoint"],
            registry=self.registry,
        )

        # Gemini API metrics
        self.gemini_requests = Counter(
            "xmaqina_gemini_requests_total",
            "Total Gemini API requests",
            ["model", "status"],
            registry=self.registry,
        )

        self.gemini_tokens = Counter(
            "xmaqina_gemini_tokens_total",
            "Total tokens used",
            ["model", "type"],  # type: input or output
            registry=self.registry,
        )

        self.gemini_latency = Histogram(
            "xmaqina_gemini_latency_seconds",
            "Gemini API latency in seconds",
            ["model"],
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0),
            registry=self.registry,
        )

        # Cache metrics
        self.cache_hits = Counter(
            "xmaqina_cache_hits_total",
            "Total cache hits",
            registry=self.registry,
        )

        self.cache_misses = Counter(
            "xmaqina_cache_misses_total",
            "Total cache misses",
            registry=self.registry,
        )

        self.cache_size = Gauge(
            "xmaqina_cache_size_bytes",
            "Cache size in bytes",
            registry=self.registry,
        )

        # Domain engine metrics
        self.engine_executions = Counter(
            "xmaqina_engine_executions_total",
            "Total engine executions",
            ["engine", "status"],
            registry=self.registry,
        )

        self.engine_duration = Histogram(
            "xmaqina_engine_duration_seconds",
            "Engine execution duration",
            ["engine"],
            registry=self.registry,
        )

        # Agent metrics
        self.agent_tasks = Counter(
            "xmaqina_agent_tasks_total",
            "Total agent tasks",
            ["agent_id", "status"],
            registry=self.registry,
        )

        self.agent_confidence = Summary(
            "xmaqina_agent_confidence",
            "Agent confidence scores",
            ["agent_id"],
            registry=self.registry,
        )

        # System health metrics
        self.system_health = Gauge(
            "xmaqina_system_health",
            "System health score (0-1)",
            registry=self.registry,
        )

        self.db_connections = Gauge(
            "xmaqina_db_connections",
            "Active database connections",
            registry=self.registry,
        )

        self.redis_connections = Gauge(
            "xmaqina_redis_connections",
            "Active Redis connections",
            registry=self.registry,
        )

        # Error metrics
        self.errors = Counter(
            "xmaqina_errors_total",
            "Total errors",
            ["error_type", "component"],
            registry=self.registry,
        )

        # Safety metrics
        self.safety_violations = Counter(
            "xmaqina_safety_violations_total",
            "Total safety violations",
            ["category"],
            registry=self.registry,
        )

    def get_metrics(self) -> bytes:
        """Get Prometheus metrics in text format"""
        if not self.registry:
            return b""
        return generate_latest(self.registry)


# Global metrics instance
metrics = MetricsRegistry()


class MetricsMiddleware:
    """Middleware for automatic metrics collection"""

    @staticmethod
    def track_request(method: str, endpoint: str):
        """Decorator to track request metrics"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                start_time = time.time()
                status = "success"

                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    status = "error"
                    logger.error(f"Request failed: {str(e)}")
                    raise
                finally:
                    duration = time.time() - start_time
                    if metrics.request_count:
                        metrics.request_count.labels(
                            method=method,
                            endpoint=endpoint,
                            status=status,
                        ).inc()
                        metrics.request_duration.labels(
                            method=method,
                            endpoint=endpoint,
                        ).observe(duration)

            @wraps(func)
            def sync_wrapper(*args, **kwargs) -> Any:
                start_time = time.time()
                status = "success"

                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    status = "error"
                    logger.error(f"Request failed: {str(e)}")
                    raise
                finally:
                    duration = time.time() - start_time
                    if metrics.request_count:
                        metrics.request_count.labels(
                            method=method,
                            endpoint=endpoint,
                            status=status,
                        ).inc()
                        metrics.request_duration.labels(
                            method=method,
                            endpoint=endpoint,
                        ).observe(duration)

            # Return async wrapper for async functions
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

        return decorator

    @staticmethod
    def track_gemini_call(model: str):
        """Decorator to track Gemini API calls"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                start_time = time.time()
                status = "success"

                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    status = "error"
                    raise
                finally:
                    duration = time.time() - start_time
                    if metrics.gemini_requests:
                        metrics.gemini_requests.labels(
                            model=model, status=status
                        ).inc()
                        metrics.gemini_latency.labels(model=model).observe(duration)

            return async_wrapper

        return decorator

    @staticmethod
    def track_engine_execution(engine_name: str):
        """Decorator to track engine execution"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                start_time = time.time()
                status = "success"

                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    status = "error"
                    raise
                finally:
                    duration = time.time() - start_time
                    if metrics.engine_executions:
                        metrics.engine_executions.labels(
                            engine=engine_name, status=status
                        ).inc()
                        metrics.engine_duration.labels(
                            engine=engine_name
                        ).observe(duration)

            return async_wrapper

        return decorator


async def collect_system_metrics() -> None:
    """Collect system health metrics periodically"""
    import psutil

    if not metrics.system_health:
        return

    # CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)
    # Memory usage
    memory_info = psutil.virtual_memory()
    # Calculate health score (0-1)
    # Lower is better
    health_score = 1.0 - (cpu_percent + memory_info.percent) / 200.0
    health_score = max(0.0, min(1.0, health_score))

    metrics.system_health.set(health_score)


import asyncio
