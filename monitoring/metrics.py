"""Prometheus metrics for monitoring"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from functools import wraps
import time

# Define metrics
payment_counter = Counter(
    'payments_total', 
    'Total number of payments processed',
    ['status', 'payment_method']
)

payment_amount = Histogram(
    'payment_amount_usd',
    'Payment amounts in USD',
    buckets=(10, 50, 100, 500, 1000, 5000, 10000)
)

payment_duration = Histogram(
    'payment_processing_duration_seconds',
    'Time spent processing payments'
)

active_users = Gauge(
    'active_users_total',
    'Number of currently active users'
)

crypto_operations = Counter(
    'crypto_operations_total',
    'Cryptographic operations performed',
    ['operation_type', 'algorithm']
)

api_requests = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status_code']
)

api_request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint']
)

# Database metrics
db_connections = Gauge('db_connections_active', 'Active database connections')
db_queries = Counter('db_queries_total', 'Total database queries', ['query_type'])

# System health
system_health = Gauge('system_health_status', 'System health status (1=healthy, 0=unhealthy)')

# Decorators for tracking
def track_payment_metrics(func):
    """Decorator to track payment metrics"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            # Assume result has status and amount attributes
            payment_counter.labels(
                status='success',
                payment_method=kwargs.get('payment_method', 'unknown')
            ).inc()
            if hasattr(result, 'amount'):
                payment_amount.observe(float(result.amount))
            return result
        except Exception as e:
            payment_counter.labels(
                status='failed',
                payment_method=kwargs.get('payment_method', 'unknown')
            ).inc()
            raise e
        finally:
            payment_duration.observe(time.time() - start_time)
    return wrapper

def track_api_request(method: str, endpoint: str):
    """Decorator to track API requests"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status_code = 200
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status_code = getattr(e, 'status_code', 500)
                raise
            finally:
                api_requests.labels(
                    method=method,
                    endpoint=endpoint,
                    status_code=status_code
                ).inc()
                api_request_duration.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(time.time() - start_time)
        return wrapper
    return decorator

def track_crypto_operation(operation_type: str, algorithm: str):
    """Decorator to track cryptographic operations"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            crypto_operations.labels(
                operation_type=operation_type,
                algorithm=algorithm
            ).inc()
            return result
        return wrapper
    return decorator

# Initialize system health as healthy
system_health.set(1)
