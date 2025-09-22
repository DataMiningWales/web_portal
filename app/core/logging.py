import logging
import json
from datetime import datetime
from typing import Any, Dict
import sys


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        if hasattr(record, 'request_id'):
            log_obj['request_id'] = record.request_id
            
        if hasattr(record, 'user_id'):
            log_obj['user_id'] = record.user_id
            
        if hasattr(record, 'extra_data'):
            log_obj['extra_data'] = record.extra_data
            
        if record.exc_info:
            log_obj['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_obj)


def setup_logging(log_level: str = "INFO") -> None:
    """Set up comprehensive JSON logging"""
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler with JSON formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(console_handler)
    
    # Create file handler for persistent logging
    file_handler = logging.FileHandler('app.log')
    file_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)


def log_request(logger: logging.Logger, request_id: str, endpoint: str, 
                method: str, payload: Dict[str, Any] = None) -> None:
    """Log API request with structured data"""
    extra_data = {
        "endpoint": endpoint,
        "method": method,
        "payload": payload
    }
    
    logger.info(
        f"API request to {method} {endpoint}",
        extra={
            'request_id': request_id,
            'extra_data': extra_data
        }
    )


def log_subscription_event(logger: logging.Logger, request_id: str, 
                          event_type: str, email: str, 
                          additional_data: Dict[str, Any] = None) -> None:
    """Log subscription-related events"""
    extra_data = {
        "event_type": event_type,
        "email": email,
        **(additional_data or {})
    }
    
    logger.info(
        f"Subscription event: {event_type} for {email}",
        extra={
            'request_id': request_id,
            'extra_data': extra_data
        }
    )