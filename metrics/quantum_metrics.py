# metrics/quantum_metrics.py
"""
Prometheus metrics cho Quantum Commerce API
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, Info
from functools import wraps
import time
from typing import Callable

# Quantum Crypto Metrics
quantum_signatures_total = Counter(
    'quantum_signatures_total',
    'Total quantum signatures created',
    ['algorithm', 'status']
)

quantum_verification_total = Counter(
    'quantum_verification_total', 
    'Total signature verifications',
    ['algorithm', 'result']
)

quantum_signature_duration = Histogram(
    'quantum_signature_duration_seconds',
    'Time to create quantum signature',
    ['algorithm']
)

quantum_verification_duration = Histogram(
    'quantum_verification_duration_seconds',
    'Time to verify quantum signature',
    ['algorithm']
)

# IBE Metrics
ibe_encryptions_total = Counter(
    'ibe_encryptions_total',
    'Total IBE encryptions',
    ['algorithm', 'status']
)

ibe_encryption_duration = Histogram(
    'ibe_encryption_duration_seconds',
    'Time to encrypt with IBE',
    ['algorithm']
)

# API Metrics
api_requests_total = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status_code']
)

api_request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint']
)

# System Metrics
active_crypto_operations = Gauge(
    'active_crypto_operations',
    'Currently active crypto operations'
)

crypto_system_info = Info(
    'crypto_system_info',
    'Information about crypto system'
)

# Payment Metrics  
payments_total = Counter(
    'payments_total',
    'Total payments processed',
    ['status', 'currency']
)

payment_amount = Histogram(
    'payment_amount_usd',
    'Payment amounts in USD',
    buckets=(10, 50, 100, 500, 1000, 5000, 10000, float('inf'))
)

# Security Metrics
security_events_total = Counter(
    'security_events_total',
    'Security events',
    ['event_type', 'severity']
)

failed_auth_attempts = Counter(
    'failed_auth_attempts_total',
    'Failed authentication attempts',
    ['reason']
)

# Decorators for automatic metrics
def track_quantum_signature(algorithm: str):
    """Decorator to track quantum signature operations"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            active_crypto_operations.inc()
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                quantum_signatures_total.labels(
                    algorithm=algorithm, 
                    status='success'
                ).inc()
                return result
            except Exception as e:
                quantum_signatures_total.labels(
                    algorithm=algorithm,
                    status='failed'
                ).inc()
                raise
            finally:
                duration = time.time() - start_time
                quantum_signature_duration.labels(algorithm=algorithm).observe(duration)
                active_crypto_operations.dec()
        
        return wrapper
    return decorator

def track_quantum_verification(algorithm: str):
    """Decorator to track verification operations"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                quantum_verification_total.labels(
                    algorithm=algorithm,
                    result='valid' if result else 'invalid'
                ).inc()
                return result
            except Exception as e:
                quantum_verification_total.labels(
                    algorithm=algorithm,
                    result='error'
                ).inc()
                raise
            finally:
                duration = time.time() - start_time
                quantum_verification_duration.labels(algorithm=algorithm).observe(duration)
        
        return wrapper
    return decorator

def track_ibe_encryption(algorithm: str):
    """Decorator to track IBE encryption"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                ibe_encryptions_total.labels(
                    algorithm=algorithm,
                    status='success'
                ).inc()
                return result
            except Exception as e:
                ibe_encryptions_total.labels(
                    algorithm=algorithm,
                    status='failed'
                ).inc()
                raise
            finally:
                duration = time.time() - start_time
                ibe_encryption_duration.labels(algorithm=algorithm).observe(duration)
        
        return wrapper
    return decorator

def track_api_request(method: str, endpoint: str):
    """Decorator to track API requests"""
    def decorator(func: Callable):
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
                duration = time.time() - start_time
                api_requests_total.labels(
                    method=method,
                    endpoint=endpoint,
                    status_code=status_code
                ).inc()
                api_request_duration.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(duration)
        
        return wrapper
    return decorator

# Initialize system info
def initialize_crypto_info():
    """Initialize crypto system info metrics"""
    try:
        from crypto import get_crypto_status
        status = get_crypto_status()
        
        crypto_system_info.info({
            'quantum_secure_signatures': str(status.get('quantum_secure_signatures', False)),
            'enhanced_ibe': str(status.get('enhanced_ibe', False)),
            'production_ready': str(status.get('production_ready', False)),
            'available_variants': ','.join(status.get('available_variants', []))
        })
    except Exception as e:
        crypto_system_info.info({
            'error': str(e),
            'status': 'failed_to_initialize'
        })

# Metrics endpoint function
def get_metrics():
    """Get Prometheus metrics"""
    return generate_latest()

# Initialize on import
initialize_crypto_info()