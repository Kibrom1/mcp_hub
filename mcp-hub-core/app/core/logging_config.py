"""
Structured logging configuration for MCP Hub Core
"""

import logging
import logging.config
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional
import traceback
from pathlib import Path

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'execution_time'):
            log_entry['execution_time'] = record.execution_time
        if hasattr(record, 'tool_name'):
            log_entry['tool_name'] = record.tool_name
        if hasattr(record, 'provider'):
            log_entry['provider'] = record.provider
        
        return json.dumps(log_entry, ensure_ascii=False)

class RequestContextFilter(logging.Filter):
    """Filter to add request context to log records"""
    
    def filter(self, record):
        # Add request context if available
        # This would be populated by middleware
        return True

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    enable_console: bool = True,
    enable_file: bool = True
) -> None:
    """Configure structured logging for the application"""
    
    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'structured': {
                '()': StructuredFormatter,
            },
            'simple': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        },
        'filters': {
            'request_context': {
                '()': RequestContextFilter,
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': log_level,
                'formatter': 'structured',
                'filters': ['request_context'],
                'stream': sys.stdout
            }
        },
        'loggers': {
            'mcp_hub': {
                'level': log_level,
                'handlers': ['console'],
                'propagate': False
            },
            'app': {
                'level': log_level,
                'handlers': ['console'],
                'propagate': False
            },
            'uvicorn': {
                'level': 'INFO',
                'handlers': ['console'],
                'propagate': False
            },
            'fastapi': {
                'level': 'INFO',
                'handlers': ['console'],
                'propagate': False
            }
        },
        'root': {
            'level': log_level,
            'handlers': ['console']
        }
    }
    
    # Add file handler if specified
    if enable_file and log_file:
        config['handlers']['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': log_level,
            'formatter': 'structured',
            'filters': ['request_context'],
            'filename': log_file,
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        }
        
        # Add file handler to all loggers
        for logger_name in config['loggers']:
            config['loggers'][logger_name]['handlers'].append('file')
        config['root']['handlers'].append('file')
    
    # Apply configuration
    logging.config.dictConfig(config)
    
    # Set up specific loggers
    logger = logging.getLogger('mcp_hub')
    logger.info("Logging system initialized", extra={
        'log_level': log_level,
        'log_file': log_file,
        'enable_console': enable_console,
        'enable_file': enable_file
    })

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with proper configuration"""
    return logging.getLogger(f'mcp_hub.{name}')

class LoggerMixin:
    """Mixin class to add logging capabilities to any class"""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class"""
        return get_logger(self.__class__.__name__)

def log_execution_time(func):
    """Decorator to log function execution time"""
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = datetime.now()
        
        try:
            result = func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(
                f"Function {func.__name__} executed successfully",
                extra={
                    'function': func.__name__,
                    'execution_time': execution_time,
                    'success': True
                }
            )
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.error(
                f"Function {func.__name__} failed: {str(e)}",
                extra={
                    'function': func.__name__,
                    'execution_time': execution_time,
                    'success': False,
                    'error': str(e)
                },
                exc_info=True
            )
            
            raise
    
    return wrapper

def log_api_request(func):
    """Decorator to log API requests"""
    def wrapper(*args, **kwargs):
        logger = get_logger('api')
        start_time = datetime.now()
        
        try:
            result = func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(
                f"API request {func.__name__} completed",
                extra={
                    'endpoint': func.__name__,
                    'execution_time': execution_time,
                    'status': 'success'
                }
            )
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.error(
                f"API request {func.__name__} failed: {str(e)}",
                extra={
                    'endpoint': func.__name__,
                    'execution_time': execution_time,
                    'status': 'error',
                    'error': str(e)
                },
                exc_info=True
            )
            
            raise
    
    return wrapper

def log_tool_execution(func):
    """Decorator to log tool executions"""
    def wrapper(*args, **kwargs):
        logger = get_logger('tools')
        start_time = datetime.now()
        
        # Extract tool information from arguments
        tool_name = kwargs.get('tool_name', 'unknown')
        server_name = kwargs.get('server_name', 'unknown')
        
        try:
            result = func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(
                f"Tool {tool_name} executed successfully",
                extra={
                    'tool_name': tool_name,
                    'server_name': server_name,
                    'execution_time': execution_time,
                    'success': True
                }
            )
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.error(
                f"Tool {tool_name} execution failed: {str(e)}",
                extra={
                    'tool_name': tool_name,
                    'server_name': server_name,
                    'execution_time': execution_time,
                    'success': False,
                    'error': str(e)
                },
                exc_info=True
            )
            
            raise
    
    return wrapper

def log_llm_request(func):
    """Decorator to log LLM requests"""
    def wrapper(*args, **kwargs):
        logger = get_logger('llm')
        start_time = datetime.now()
        
        # Extract provider information
        provider = kwargs.get('provider', 'unknown')
        model = kwargs.get('model', 'unknown')
        
        try:
            result = func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(
                f"LLM request to {provider} completed",
                extra={
                    'provider': provider,
                    'model': model,
                    'execution_time': execution_time,
                    'tokens_used': getattr(result, 'tokens_used', None),
                    'success': True
                }
            )
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.error(
                f"LLM request to {provider} failed: {str(e)}",
                extra={
                    'provider': provider,
                    'model': model,
                    'execution_time': execution_time,
                    'success': False,
                    'error': str(e)
                },
                exc_info=True
            )
            
            raise
    
    return wrapper

# Initialize logging on import
setup_logging(
    log_level="INFO",
    log_file="logs/mcp_hub.log",
    enable_console=True,
    enable_file=True
)
