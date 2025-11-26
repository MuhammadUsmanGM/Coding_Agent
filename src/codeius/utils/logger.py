"""
Logging system for Codeius AI Coding Agent
Provides structured logging for debugging and monitoring.
"""
import logging
import logging.handlers
from pathlib import Path
from typing import Optional
import os
from datetime import datetime

class Logger:
    """Structured logging system for the Codeius AI Coding Agent."""
    
    def __init__(self, name: str = "codeius", log_file: Optional[str] = None, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=10*1024*1024, backupCount=5  # 10MB max, 5 backups
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        
        self.logger.propagate = False  # Don't propagate to root logger
    
    def debug(self, message: str, extra: Optional[dict] = None):
        """Log a debug message."""
        self.logger.debug(message, extra=extra)
    
    def info(self, message: str, extra: Optional[dict] = None):
        """Log an info message."""
        self.logger.info(message, extra=extra)
    
    def warning(self, message: str, extra: Optional[dict] = None):
        """Log a warning message."""
        self.logger.warning(message, extra=extra)
    
    def error(self, message: str, extra: Optional[dict] = None):
        """Log an error message."""
        self.logger.error(message, extra=extra)
    
    def critical(self, message: str, extra: Optional[dict] = None):
        """Log a critical message."""
        self.logger.critical(message, extra=extra)
    
    def exception(self, message: str, extra: Optional[dict] = None):
        """Log an exception with traceback."""
        self.logger.exception(message, extra=extra)

class AgentLogger:
    """Centralized logging system for the agent."""
    
    def __init__(self):
        # Create logs directory
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        
        # Initialize loggers
        self.app_logger = Logger("codeius.app", log_file=str(self.logs_dir / "app.log"))
        self.agent_logger = Logger("codeius.agent", log_file=str(self.logs_dir / "agent.log"))
        self.api_logger = Logger("codeius.api", log_file=str(self.logs_dir / "api.log"))
        self.security_logger = Logger("codeius.security", log_file=str(self.logs_dir / "security.log"))
        self.file_logger = Logger("codeius.file", log_file=str(self.logs_dir / "file.log"))
    
    def log_agent_activity(self, user_input: str, agent_response: str, actions_taken: list):
        """Log agent activity."""
        self.agent_logger.info(
            f"Agent processed query: {user_input[:100]}...", 
            extra={
                "input_length": len(user_input),
                "response_length": len(agent_response),
                "actions_count": len(actions_taken),
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def log_api_call(self, provider: str, endpoint: str, status: int, duration: float):
        """Log API calls."""
        self.api_logger.info(
            f"API call to {provider} at {endpoint} completed with status {status}",
            extra={
                "provider": provider,
                "endpoint": endpoint,
                "status": status,
                "duration_ms": duration * 1000,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def log_security_event(self, event_type: str, details: str, severity: str = "info"):
        """Log security-related events."""
        log_method = getattr(self.security_logger, severity.lower(), self.security_logger.info)
        log_method(
            f"Security event: {event_type}",
            extra={
                "event_type": event_type,
                "details": details,
                "severity": severity,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def log_file_operation(self, operation: str, file_path: str, success: bool, details: str = ""):
        """Log file operations."""
        status = "SUCCESS" if success else "FAILED"
        self.file_logger.info(
            f"File operation {status}: {operation} on {file_path}",
            extra={
                "operation": operation,
                "file_path": file_path,
                "success": success,
                "details": details,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def log_error(self, error_type: str, error_message: str, context: str = ""):
        """Log general errors."""
        self.app_logger.error(
            f"Error occurred: {error_type} - {error_message}",
            extra={
                "error_type": error_type,
                "error_message": error_message,
                "context": context,
                "timestamp": datetime.now().isoformat()
            }
        )

# Global logger instance
agent_logger = AgentLogger()