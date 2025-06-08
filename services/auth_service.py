
"""
Enhanced authentication service with security features
"""
from datetime import datetime, timedelta
from typing import Optional, Dict
import bcrypt
import jwt
from sqlalchemy.orm import Session
from database.schema import User, UserSession, AuditLog
from config.security import SecurityConfig
from services.session_service import session_service
from services.rate_limiter import rate_limiter
import logging
import secrets

logger = logging.getLogger(__name__)

class AuthService:
    """Enhanced authentication with security features"""
    
    def __init__(self):
        self.jwt_secret = SecurityConfig.JWT_SECRET_KEY
        self.jwt_algorithm = SecurityConfig.JWT_ALGORITHM
        self.bcrypt_rounds = SecurityConfig.BCRYPT_ROUNDS
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        # Add pepper (application-level salt)
        peppered = password + SecurityConfig.JWT_SECRET_KEY[:10]
        
        # Generate salt and hash
        salt = bcrypt.gensalt(rounds=self.bcrypt_rounds)
        hashed = bcrypt.hashpw(peppered.encode('utf-8'), salt)
        
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password"""
        try:
            # Add pepper
            peppered = password + SecurityConfig.JWT_SECRET_KEY[:10]
            
            # Verify
            return bcrypt.checkpw(
                peppered.encode('utf-8'),
                hashed.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def register_user(
        self,
        db: Session,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Dict:
        """Register new user with security checks"""
        try:
            # Check rate limit
            allowed, remaining = rate_limiter.check_rate_limit(
                ip_address or 'unknown',
                'register'
            )
            
            if not allowed:
                return {
                    'success': False,
                    'error': 'Too many registration attempts. Please try again later.'
                }
            
            # Validate password strength
            if not self._validate_password_strength(password):
                return {
                    'success': False,
                    'error': 'Password does not meet security requirements'
                }
            
            # Check if user exists
            if db.query(User).filter(
                (User.email == email) | (User.username == username)
            ).first():
                return {
                    'success': False,
                    'error': 'User already exists'
                }
            
            # Create user
            hashed_password = self.hash_password(password)
            
            user = User(
                email=email,
                username=username,
                hashed_password=hashed_password,
                full_name=full_name,
                is_active=True,
                is_verified=False  # Require email verification
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Log registration
            self._log_audit(
                db,
                user.id,
                'user_registered',
                'user',
                str(user.id),
                {'email': email, 'username': username},
                ip_address
            )
            
            # Generate verification token
            verification_token = self._generate_verification_token(user.id)
            
            return {
                'success': True,
                'user': user,
                'verification_token': verification_token
            }
            
        except Exception as e:
            logger.error(f"Registration error: {e}")
            db.rollback()
            return {
                'success': False,
                'error': 'Registration failed'
            }
    
    def login_user(
        self,
        db: Session,
        email: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict:
        """Login user with security checks"""
        try:
            # Check rate limit
            allowed, remaining = rate_limiter.check_rate_limit(
                ip_address or email,
                'login'
            )
            
            if not allowed:
                return {
                    'success': False,
                    'error': 'Too many login attempts. Please try again later.'
                }
            
            # Find user
            user = db.query(User).filter(User.email == email).first()
            
            if not user:
                # Don't reveal if user exists
                self._log_failed_login(db, email, ip_address)
                return {
                    'success': False,
                    'error': 'Invalid credentials'
                }
            
            # Check if account is locked
            if user.locked_until and user.locked_until > datetime.utcnow():
                return {
                    'success': False,
                    'error': f'Account locked until {user.locked_until}'
                }
            
            # Verify password
            if not self.verify_password(password, user.hashed_password):
                # Increment failed attempts
                user.failed_login_attempts += 1
                
                # Lock account if too many attempts
                if user.failed_login_attempts >= SecurityConfig.MAX_LOGIN_ATTEMPTS:
                    user.locked_until = datetime.utcnow() + timedelta(
                        minutes=SecurityConfig.LOCKOUT_DURATION_MINUTES
                    )
                
                db.commit()
                
                self._log_failed_login(db, email, ip_address, user.id)
                
                return {
                    'success': False,
                    'error': 'Invalid credentials'
                }
            
            # Check if account is active
            if not user.is_active:
                return {
                    'success': False,
                    'error': 'Account is disabled'
                }
            
            # Reset failed attempts
            user.failed_login_attempts = 0
            user.locked_until = None
            user.last_login = datetime.utcnow()
            
            # Create session
            session_id = session_service.create_session(
                user.id,
                {
                    'email': user.email,
                    'username': user.username,
                    'is_admin': user.is_admin,
                    'ip_address': ip_address,
                    'user_agent': user_agent
                }
            )
            
            # Generate JWT token
            token = self._generate_token(user, session_id)
            
            # Save session to database
            db_session = UserSession(
                session_id=session_id,
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=datetime.utcnow() + timedelta(
                    hours=SecurityConfig.JWT_EXPIRATION_HOURS
                )
            )
            
            db.add(db_session)
            db.commit()
            
            # Log successful login
            self._log_audit(
                db,
                user.id,
                'user_login',
                'session',
                session_id,
                {'method': 'password'},
                ip_address
            )
            
            return {
                'success': True,
                'token': token,
                'session_id': session_id,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'is_admin': user.is_admin
                }
            }
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            db.rollback()
            return {
                'success': False,
                'error': 'Login failed'
            }
    
    def logout_user(
        self,
        db: Session,
        user_id: int,
        session_id: str,
        ip_address: Optional[str] = None
    ) -> bool:
        """Logout user and destroy session"""
        try:
            # Destroy Redis session
            session_service.destroy_session(session_id)
            
            # Mark database session as inactive
            db_session = db.query(UserSession).filter(
                UserSession.session_id == session_id
            ).first()
            
            if db_session:
                db_session.is_active = False
                db.commit()
            
            # Log logout
            self._log_audit(
                db,
                user_id,
                'user_logout',
                'session',
                session_id,
                {},
                ip_address
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token and session"""
        try:
            # Decode token
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.jwt_algorithm]
            )
            
            # Check session
            session_id = payload.get('session_id')
            if not session_id:
                return None
            
            session_data = session_service.get_session(session_id)
            if not session_data:
                return None
            
            # Return user data
            return {
                'user_id': payload['user_id'],
                'email': payload['email'],
                'username': payload['username'],
                'is_admin': payload.get('is_admin', False),
                'session_id': session_id
            }
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    def _generate_token(self, user: User, session_id: str) -> str:
        """Generate JWT token"""
        payload = {
            'user_id': user.id,
            'email': user.email,
            'username': user.username,
            'is_admin': user.is_admin,
            'session_id': session_id,
            'exp': datetime.utcnow() + timedelta(
                hours=SecurityConfig.JWT_EXPIRATION_HOURS
            )
        }
        
        return jwt.encode(
            payload,
            self.jwt_secret,
            algorithm=self.jwt_algorithm
        )
    
    def _generate_verification_token(self, user_id: int) -> str:
        """Generate email verification token"""
        token = secrets.token_urlsafe(32)
        
        # Store in Redis with expiration
        key = f"verify:{token}"
        session_service.redis_client.setex(
            key,
            86400,  # 24 hours
            str(user_id)
        )
        
        return token
    
    def _validate_password_strength(self, password: str) -> bool:
        """Validate password meets security requirements"""
        if len(password) < 8:
            return False
        
        # Check for required character types
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
        
        return has_upper and has_lower and has_digit and has_special
    
    def _log_audit(
        self,
        db: Session,
        user_id: Optional[int],
        action: str,
        resource_type: Optional[str],
        resource_id: Optional[str],
        details: Optional[Dict],
        ip_address: Optional[str]
    ):
        """Log audit entry"""
        try:
            audit = AuditLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details,
                ip_address=ip_address,
                success=True
            )
            
            db.add(audit)
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to log audit: {e}")
    
    def _log_failed_login(
        self,
        db: Session,
        email: str,
        ip_address: Optional[str],
        user_id: Optional[int] = None
    ):
        """Log failed login attempt"""
        try:
            audit = AuditLog(
                user_id=user_id,
                action='login_failed',
                resource_type='user',
                resource_id=email,
                details={'reason': 'invalid_credentials'},
                ip_address=ip_address,
                success=False
            )
            
            db.add(audit)
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to log failed login: {e}")

# Initialize service
auth_service = AuthService()