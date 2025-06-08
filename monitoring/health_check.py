# monitoring/health_check.py
"""Health check endpoints and system monitoring"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import psutil
import redis
from typing import Dict, Any
from database import get_db, engine
from config.security import SecurityConfig
from monitoring.metrics import system_health
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])

class HealthChecker:
    """System health monitoring"""
    
    def __init__(self):
        self.checks = {
            'database': self._check_database,
            'redis': self._check_redis,
            'crypto': self._check_crypto,
            'disk': self._check_disk_space,
            'memory': self._check_memory
        }
    
    async def check_all(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'checks': {}
        }
        
        for name, check_func in self.checks.items():
            try:
                results['checks'][name] = await check_func()
            except Exception as e:
                logger.error(f"Health check {name} failed: {e}")
                results['checks'][name] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                results['status'] = 'degraded'
        
        # Update system health metric
        overall_health = 1 if results['status'] == 'healthy' else 0
        system_health.set(overall_health)
        
        return results
    
    async def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity"""
        try:
            with engine.connect() as conn:
                result = conn.execute("SELECT 1").scalar()
                return {
                    'status': 'healthy' if result == 1 else 'unhealthy',
                    'response_time_ms': 10  # Mock for now
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    async def _check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity"""
        try:
            r = redis.from_url(SecurityConfig.REDIS_URL)
            r.ping()
            return {
                'status': 'healthy',
                'response_time_ms': 5
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    async def _check_crypto(self) -> Dict[str, Any]:
        """Check crypto systems"""
        try:
            from crypto import DilithiumSigner, IBESystem
            
            # Quick test
            signer = DilithiumSigner()
            ibe = IBESystem()
            
            return {
                'status': 'healthy',
                'dilithium': 'active',
                'ibe': 'active'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    async def _check_disk_space(self) -> Dict[str, Any]:
        """Check disk space"""
        try:
            disk_usage = psutil.disk_usage('/')
            return {
                'status': 'healthy' if disk_usage.percent < 90 else 'warning',
                'used_percent': disk_usage.percent,
                'free_gb': disk_usage.free / (1024**3)
            }
        except Exception as e:
            return {
                'status': 'unknown',
                'error': str(e)
            }
    
    async def _check_memory(self) -> Dict[str, Any]:
        """Check memory usage"""
        try:
            memory = psutil.virtual_memory()
            return {
                'status': 'healthy' if memory.percent < 85 else 'warning',
                'used_percent': memory.percent,
                'available_gb': memory.available / (1024**3)
            }
        except Exception as e:
            return {
                'status': 'unknown',
                'error': str(e)
            }

# Initialize health checker
health_checker = HealthChecker()

@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        'status': 'healthy',
        'service': 'Quantum Commerce API',
        'timestamp': datetime.utcnow().isoformat()
    }

@router.get("/live")
async def liveness_probe():
    """Kubernetes liveness probe"""
    return {'status': 'alive'}

@router.get("/ready")
async def readiness_probe(db: Session = Depends(get_db)):
    """Kubernetes readiness probe"""
    try:
        # Quick DB check
        db.execute("SELECT 1")
        return {'status': 'ready'}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {'status': 'not_ready'}, 503

@router.get("/detailed")
async def detailed_health():
    """Detailed health check"""
    return await health_checker.check_all()