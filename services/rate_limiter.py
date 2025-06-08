
"""
Rate limiting service using Redis
"""
import redis
from datetime import datetime, timedelta
from typing import Tuple
from config.security import SecurityConfig
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiting implementation"""
    
    def __init__(self):
        try:
            # Thử kết nối Redis với cấu hình đơn giản hơn cho testing
            self.redis_client = redis.from_url(
                SecurityConfig.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            self.redis_client.ping()
            self.redis_available = True
        except Exception as e:
            logger.warning(f"Redis không khả dụng, sử dụng in-memory storage: {e}")
            self.redis_available = False
            self._memory_store = {}  # Fallback to memory
        
        # Rate limit configurations
        self.limits = {
            'login': {'requests': 5, 'window': 300},  # 5 attempts per 5 minutes
            'api': {'requests': 100, 'window': 60},   # 100 requests per minute
            'payment': {'requests': 10, 'window': 600}, # 10 payments per 10 minutes
            'register': {'requests': 3, 'window': 3600}, # 3 registrations per hour
        }
    
    def check_rate_limit(self, key: str, limit_type: str = 'api') -> Tuple[bool, int]:
        """
        Check if rate limit is exceeded
        Returns: (is_allowed, remaining_requests)
        """
        if limit_type not in self.limits:
            limit_type = 'api'
        
        limit_config = self.limits[limit_type]
        max_requests = limit_config['requests']
        window = limit_config['window']
        
        # Create Redis key
        redis_key = f"rate_limit:{limit_type}:{key}"
        
        try:
            if self.redis_available:
                return self._check_redis_rate_limit(redis_key, max_requests, window)
            else:
                return self._check_memory_rate_limit(redis_key, max_requests, window)
                
        except Exception as e:
            logger.error(f"Rate limiter error: {e}")
            # On error, allow request but log
            return True, 0
    
    def _check_redis_rate_limit(self, redis_key: str, max_requests: int, window: int) -> Tuple[bool, int]:
        """Check rate limit using Redis"""
        # Get current count
        current = self.redis_client.get(redis_key)
        
        if current is None:
            # First request
            self.redis_client.setex(redis_key, window, 1)
            return True, max_requests - 1
        
        current_count = int(current)
        
        if current_count >= max_requests:
            # Rate limit exceeded
            ttl = self.redis_client.ttl(redis_key)
            logger.warning(f"Rate limit exceeded for key {redis_key}")
            return False, 0
        
        # Increment counter
        new_count = self.redis_client.incr(redis_key)
        
        return True, max_requests - new_count
    
    def _check_memory_rate_limit(self, key: str, max_requests: int, window: int) -> Tuple[bool, int]:
        """Fallback rate limiting using memory"""
        import time
        current_time = time.time()
        
        if key not in self._memory_store:
            self._memory_store[key] = {'count': 1, 'reset_time': current_time + window}
            return True, max_requests - 1
        
        store_data = self._memory_store[key]
        
        # Check if window has expired
        if current_time > store_data['reset_time']:
            self._memory_store[key] = {'count': 1, 'reset_time': current_time + window}
            return True, max_requests - 1
        
        # Check if limit exceeded
        if store_data['count'] >= max_requests:
            return False, 0
        
        # Increment counter
        store_data['count'] += 1
        remaining = max_requests - store_data['count']
        
        return True, remaining
    
    def get_limit_info(self, key: str, limit_type: str = 'api') -> Dict:
        """Get rate limit information"""
        redis_key = f"rate_limit:{limit_type}:{key}"
        limit_config = self.limits.get(limit_type, self.limits['api'])
        
        if self.redis_available:
            try:
                current = self.redis_client.get(redis_key)
                ttl = self.redis_client.ttl(redis_key) if current else 0
            except:
                current = None
                ttl = 0
        else:
            current = self._memory_store.get(redis_key, {}).get('count', 0)
            ttl = 0
        
        return {
            'limit': limit_config['requests'],
            'window': limit_config['window'],
            'used': int(current) if current else 0,
            'remaining': limit_config['requests'] - (int(current) if current else 0),
            'reset_in': ttl if ttl > 0 else 0
        }
    
    def reset_limit(self, key: str, limit_type: str = 'api'):
        """Reset rate limit for a key"""
        redis_key = f"rate_limit:{limit_type}:{key}"
        
        if self.redis_available:
            try:
                self.redis_client.delete(redis_key)
            except:
                pass
        else:
            self._memory_store.pop(redis_key, None)

# Initialize global rate limiter
rate_limiter = RateLimiter()