"""
Error handling and validation utilities for Codeius AI Coding Agent.
Provides consistent error handling across the application.
"""
from typing import Any, Union, Optional
from enum import Enum
from dataclasses import dataclass
from coding_agent.logger import agent_logger


class ErrorCode(Enum):
    """Enumeration of possible error codes."""
    # File operations
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    PATH_TRAVERSAL = "PATH_TRAVERSAL"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    
    # API related
    API_RATE_LIMIT = "API_RATE_LIMIT"
    API_KEY_INVALID = "API_KEY_INVALID"
    API_CONNECTION_ERROR = "API_CONNECTION_ERROR"
    
    # Model related
    MODEL_NOT_FOUND = "MODEL_NOT_FOUND"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
    
    # Input validation
    INVALID_INPUT = "INVALID_INPUT"
    JSON_PARSE_ERROR = "JSON_PARSE_ERROR"
    
    # Security
    SECURITY_VIOLATION = "SECURITY_VIOLATION"
    
    # Generic
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


@dataclass
class ErrorResponse:
    """Structure for error responses."""
    success: bool
    error_code: ErrorCode
    message: str
    details: Optional[dict] = None
    data: Optional[Any] = None


@dataclass
class SuccessResponse:
    """Structure for success responses."""
    success: bool
    message: str
    data: Optional[Any] = None


def handle_error(error_code: ErrorCode, message: str, details: Optional[dict] = None) -> ErrorResponse:
    """Create a standardized error response."""
    agent_logger.log_error(error_code.value, message, str(details) if details else "")
    return ErrorResponse(success=False, error_code=error_code, message=message, details=details)


def handle_success(message: str, data: Optional[Any] = None) -> Union[SuccessResponse, ErrorResponse]:
    """Create a standardized success response."""
    if isinstance(data, ErrorResponse):
        return data  # Return error if error response is passed
    
    return SuccessResponse(success=True, message=message, data=data)


def validate_api_key(api_key: Optional[str], provider_name: str) -> Union[SuccessResponse, ErrorResponse]:
    """Validate an API key."""
    if not api_key or not api_key.strip():
        return handle_error(
            ErrorCode.API_KEY_INVALID,
            f"No valid {provider_name} API key found. Please set {provider_name.upper()}_API_KEY in your environment variables."
        )
    
    if len(api_key) < 10:  # Basic check for API key length
        return handle_error(
            ErrorCode.API_KEY_INVALID,
            f"Invalid {provider_name} API key format."
        )
    
    return handle_success(f"{provider_name} API key validated")


def validate_file_path(file_path: str) -> Union[SuccessResponse, ErrorResponse]:
    """Validate a file path for basic constraints."""
    if not file_path or not file_path.strip():
        return handle_error(ErrorCode.INVALID_INPUT, "File path cannot be empty")
    
    if '..' in file_path or file_path.startswith('/') or (':' in file_path and '\\' in file_path):
        return handle_error(ErrorCode.PATH_TRAVERSAL, f"Potentially unsafe file path: {file_path}")
    
    return handle_success(f"File path {file_path} is valid")


def validate_model_key(model_key: str, available_models: dict) -> Union[SuccessResponse, ErrorResponse]:
    """Validate a model key against available models."""
    if not model_key:
        return handle_error(ErrorCode.INVALID_INPUT, "Model key cannot be empty")
    
    if model_key not in available_models:
        return handle_error(
            ErrorCode.MODEL_NOT_FOUND,
            f"Model '{model_key}' not found. Available models: {', '.join(available_models.keys())}"
        )
    
    return handle_success(f"Model {model_key} is valid")


def safe_execute(func, error_message: str = "An error occurred", default_return=None):
    """Safely execute a function with error handling."""
    try:
        return func()
    except Exception as e:
        agent_logger.log_error("SAFE_EXECUTE_ERROR", str(e), error_message)
        return default_return if default_return is not None else handle_error(
            ErrorCode.UNKNOWN_ERROR,
            f"{error_message}: {str(e)}"
        )


def validate_json(json_str: str) -> Union[SuccessResponse, ErrorResponse]:
    """Validate that a string is valid JSON."""
    import json
    try:
        parsed = json.loads(json_str)
        return handle_success("JSON is valid", parsed)
    except json.JSONDecodeError as e:
        return handle_error(
            ErrorCode.JSON_PARSE_ERROR,
            f"Invalid JSON: {str(e)}",
            {"json_str": json_str[:100]}  # Only log first 100 chars for security
        )