import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging(app_name: str = "quantum-commerce", log_level: str = "INFO"):
    """Setup logging configuration"""
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # Console handler
            logging.StreamHandler(sys.stdout),
            # File handler with rotation
            RotatingFileHandler(
                log_dir / "app.log",
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
        ]
    )
    
    # Create logger
    logger = logging.getLogger(app_name)
    logger.info(f"Logging initialized for {app_name}")
    
    return logger

# Create logs directory
Path("logs").mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
class SecurityLogger:
    def __init__(self):
        self.logger = logging.getLogger("security")
        
    def log_auth_attempt(self, email: str, success: bool, ip: str):
        if success:
            self.logger.info(f"Successful login: {email} from {ip}")
        else:
            self.logger.warning(f"Failed login attempt: {email} from {ip}")
            
    def log_transaction(self, transaction_id: str, amount: float, user_id: str):
        self.logger.info(f"Transaction {transaction_id}: ${amount} by user {user_id}")
        
    def log_security_event(self, event_type: str, details: str):
        self.logger.warning(f"Security event - {event_type}: {details}")

# Create loggers
api_logger = logging.getLogger('api')
crypto_logger = logging.getLogger('crypto')
payment_logger = logging.getLogger('payment')
