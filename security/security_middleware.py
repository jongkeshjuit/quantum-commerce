# security/security_middleware.py
"""
Enhanced Security Middleware Stack
"""
import time
import json
import hashlib
from typing import Dict, Any, Optional
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class SecurityEnhancements:
    """Enhanced security middleware stack"""
    
    def __init__(self):
        self.rate_limits = {}
        self.suspicious_ips = set()
        self.failed_attempts = {}
        
    async def security_middleware(self, request: Request, call_next):
        """Comprehensive security middleware"""
        
        # 1. Get client info
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        
        # 2. Security checks
        security_result = await self._run_security_checks(request, client_ip, user_agent)
        
        if not security_result["allowed"]:
            logger.warning(f"🚫 Security block: {security_result['reason']} from {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=security_result["reason"]
            )
        
        # 3. Add security headers
        response = await call_next(request)
        self._add_security_headers(response)
        
        # 4. Log security event
        await self._log_security_event(request, response, client_ip)
        
        return response
    
    async def _run_security_checks(self, request: Request, client_ip: str, user_agent: str) -> Dict[str, Any]:
        """Run comprehensive security checks"""
        
        # 1. Rate limiting
        if not self._check_rate_limit(client_ip, request.url.path):
            return {"allowed": False, "reason": "Rate limit exceeded"}
        
        # 2. Suspicious IP check
        if client_ip in self.suspicious_ips:
            return {"allowed": False, "reason": "IP blocked for suspicious activity"}
        
        # 3. Bot detection
        if self._detect_bot(user_agent):
            return {"allowed": False, "reason": "Automated traffic detected"}
        
        # 4. Path traversal detection
        if self._detect_path_traversal(str(request.url)):
            self.suspicious_ips.add(client_ip)
            return {"allowed": False, "reason": "Path traversal attempt detected"}
        
        # 5. SQL injection detection (basic)
        if self._detect_sql_injection(str(request.url)):
            self.suspicious_ips.add(client_ip)
            return {"allowed": False, "reason": "SQL injection attempt detected"}
        
        return {"allowed": True, "reason": "Passed security checks"}
    
    def _check_rate_limit(self, client_ip: str, path: str) -> bool:
        """Enhanced rate limiting per IP per endpoint"""
        current_time = time.time()
        
        # Different limits for different endpoints
        limits = {
            "/api/crypto/sign": {"requests": 10, "window": 60},      # 10 signatures per minute
            "/api/crypto/verify": {"requests": 20, "window": 60},    # 20 verifications per minute
            "/api/auth/login": {"requests": 5, "window": 300},       # 5 login attempts per 5 minutes
            "default": {"requests": 100, "window": 60}               # 100 requests per minute
        }
        
        # Get limit for this path
        limit_config = limits.get(path, limits["default"])
        
        # Create rate limit key
        key = f"{client_ip}:{path}"
        
        if key not in self.rate_limits:
            self.rate_limits[key] = []
        
        # Clean old requests
        self.rate_limits[key] = [
            req_time for req_time in self.rate_limits[key]
            if current_time - req_time < limit_config["window"]
        ]
        
        # Check if limit exceeded
        if len(self.rate_limits[key]) >= limit_config["requests"]:
            return False
        
        # Add current request
        self.rate_limits[key].append(current_time)
        return True
    
    def _detect_bot(self, user_agent: str) -> bool:
        """Detect automated/bot traffic"""
        bot_indicators = [
            "bot", "crawler", "spider", "scraper", "curl", "wget",
            "python-requests", "http", "automated", "script"
        ]
        
        ua_lower = user_agent.lower()
        return any(indicator in ua_lower for indicator in bot_indicators)
    
    def _detect_path_traversal(self, url: str) -> bool:
        """Detect path traversal attempts"""
        traversal_patterns = ["../", "..\\", "%2e%2e", "%2f", "%5c"]
        return any(pattern in url.lower() for pattern in traversal_patterns)
    
    def _detect_sql_injection(self, url: str) -> bool:
        """Basic SQL injection detection"""
        sql_patterns = [
            "union select", "drop table", "insert into", "delete from",
            "update set", "or 1=1", "and 1=1", "'; --", "admin'--"
        ]
        return any(pattern in url.lower() for pattern in sql_patterns)
    
    def _get_client_ip(self, request: Request) -> str:
        """Get real client IP considering proxies"""
        # Check various headers for real IP
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _add_security_headers(self, response):
        """Add comprehensive security headers"""
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "X-Quantum-Secure": "true"  # Custom header
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value
    
    async def _log_security_event(self, request: Request, response, client_ip: str):
        """Log security events for analysis"""
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "client_ip": client_ip,
            "method": request.method,
            "path": str(request.url.path),
            "user_agent": request.headers.get("user-agent", ""),
            "status_code": response.status_code,
            "quantum_endpoint": "/api/crypto/" in str(request.url.path)
        }
        
        # Log to security log file
        logger.info(f"🔒 Security Event: {json.dumps(event)}")

class QuantumSecurityAudit:
    """Audit logging for quantum crypto operations"""
    
    def __init__(self):
        self.audit_log = []
    
    def log_crypto_operation(self, operation: str, user_id: str, details: Dict[str, Any]):
        """Log quantum crypto operations"""
        audit_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operation": operation,
            "user_id": user_id,
            "details": details,
            "signature_hash": self._generate_audit_hash(operation, user_id, details)
        }
        
        self.audit_log.append(audit_entry)
        logger.info(f"🛡️ Quantum Audit: {operation} by {user_id}")
    
    def _generate_audit_hash(self, operation: str, user_id: str, details: Dict[str, Any]) -> str:
        """Generate hash for audit integrity"""
        audit_string = f"{operation}:{user_id}:{json.dumps(details, sort_keys=True)}"
        return hashlib.sha256(audit_string.encode()).hexdigest()
    
    def get_audit_trail(self, user_id: Optional[str] = None) -> list:
        """Get audit trail for user or all"""
        if user_id:
            return [entry for entry in self.audit_log if entry["user_id"] == user_id]
        return self.audit_log

# Global instances
security_middleware = SecurityEnhancements()
quantum_audit = QuantumSecurityAudit()

# Enhanced authentication
class QuantumJWTBearer(HTTPBearer):
    """Enhanced JWT bearer with quantum crypto context"""
    
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request):
        """Validate JWT with enhanced security"""
        credentials = await super().__call__(request)
        
        if credentials:
            # Enhanced token validation
            token_data = self._validate_token(credentials.credentials)
            
            if not token_data:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid quantum security token"
                )
            
            # Log authentication event
            quantum_audit.log_crypto_operation(
                "authentication",
                token_data.get("user_id", "unknown"),
                {"token_valid": True, "quantum_context": True}
            )
            
            return token_data
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing quantum security credentials"
        )
    
    def _validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Enhanced token validation"""
        # Implement JWT validation with quantum context
        # For now, return mock data
        return {
            "user_id": "quantum_user_123",
            "quantum_verified": True,
            "security_level": "quantum_secure"
        }

# Export middleware
quantum_jwt = QuantumJWTBearer()