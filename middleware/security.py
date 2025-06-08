# middleware/security.py
"""
Security middleware for FastAPI
"""
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from services.auth_service import auth_service
from services.rate_limiter import rate_limiter
import logging

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    """Security middleware for API protection"""
    
    async def __call__(self, request: Request, call_next):
        # Add security headers
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response

class JWTBearer(HTTPBearer):
    """JWT Bearer token verification"""
    
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request) -> Optional[Dict]:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid authentication scheme."
                )
            
            # Verify token
            user_data = auth_service.verify_token(credentials.credentials)
            
            if not user_data:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid or expired token."
                )
            
            return user_data
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authorization code."
            )

class RateLimitMiddleware:
    """Rate limiting middleware"""
    
    async def __call__(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host
        
        # Check rate limit
        allowed, remaining = rate_limiter.check_rate_limit(client_ip)
        
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response

# Initialize middleware
security_middleware = SecurityMiddleware()
rate_limit_middleware = RateLimitMiddleware()
jwt_bearer = JWTBearer()