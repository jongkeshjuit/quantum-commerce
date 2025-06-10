# services/session_service.py
"""
Secure session management using Redis
"""
import redis
import json
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from config.dev_config import SecurityConfig
import logging

logger = logging.getLogger(__name__)

class SessionService:
    """Secure session management with Redis"""
    
    # Thêm vào đầu class SessionService:
def __init__(self):
    try:
        # Redis connection
        self.redis_client = redis.from_url(
            SecurityConfig.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        self.redis_client.ping()
        self.redis_available = True
        logger.info("✅ Redis session storage connected")
    except Exception as e:
        logger.warning(f"⚠️ Redis unavailable for sessions: {e}")
        self.redis_available = False
        self._memory_sessions = {}  # Fallback
    
    # Session configuration
    self.session_prefix = "session:"
    self.session_timeout = SecurityConfig.SESSION_TIMEOUT_MINUTES * 60
        
    def create_session(self, user_id: int, user_data: Dict[str, Any]) -> str:
        """Create a new session"""
        # Invalidate old sessions
        self.destroy_all_user_sessions(user_id)
        # Generate secure session ID
        session_id = secrets.token_urlsafe(32)
        
        # Session data
        session_data = {
            'user_id': user_id,
            'email': user_data.get('email'),
            'username': user_data.get('username'),
            'is_admin': user_data.get('is_admin', False),
            'created_at': datetime.utcnow().isoformat(),
            'last_activity': datetime.utcnow().isoformat(),
            'ip_address': user_data.get('ip_address'),
            'user_agent': user_data.get('user_agent'),
        }
        
        # Store in Redis with expiration
        key = f"{self.session_prefix}{session_id}"
        self.redis_client.setex(
            key,
            self.session_timeout,
            json.dumps(session_data)
        )
        
        logger.info(f"Created session for user {user_id}")
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        key = f"{self.session_prefix}{session_id}"
        
        # Get from Redis
        data = self.redis_client.get(key)
        if not data:
            return None
        
        try:
            session_data = json.loads(data)
            
            # Update last activity
            session_data['last_activity'] = datetime.utcnow().isoformat()
            
            # Extend expiration
            self.redis_client.setex(
                key,
                self.session_timeout,
                json.dumps(session_data)
            )
            
            return session_data
            
        except Exception as e:
            logger.error(f"Failed to get session: {e}")
            return None
    
    def destroy_session(self, session_id: str) -> bool:
        """Destroy a session"""
        key = f"{self.session_prefix}{session_id}"
        result = self.redis_client.delete(key)
        
        logger.info(f"Destroyed session {session_id}")
        
        return result > 0
    
    def destroy_all_user_sessions(self, user_id: int) -> int:
        """Destroy all sessions for a user"""
        count = 0
        
        # Scan for all sessions
        for key in self.redis_client.scan_iter(f"{self.session_prefix}*"):
            data = self.redis_client.get(key)
            if data:
                try:
                    session_data = json.loads(data)
                    if session_data.get('user_id') == user_id:
                        self.redis_client.delete(key)
                        count += 1
                except:
                    pass
        
        logger.info(f"Destroyed {count} sessions for user {user_id}")
        
        return count
    
    def update_session_activity(self, session_id: str) -> bool:
        """Update session last activity"""
        key = f"{self.session_prefix}{session_id}"
        
        data = self.redis_client.get(key)
        if not data:
            return False
        
        try:
            session_data = json.loads(data)
            session_data['last_activity'] = datetime.utcnow().isoformat()
            
            # Reset expiration
            self.redis_client.setex(
                key,
                self.session_timeout,
                json.dumps(session_data)
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update session: {e}")
            return False
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        count = 0
        for _ in self.redis_client.scan_iter(f"{self.session_prefix}*"):
            count += 1
        return count
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions (Redis handles this automatically)"""
        # Redis automatically removes expired keys
        # This method is here for completeness
        pass

# Initialize global session service
session_service = SessionService()