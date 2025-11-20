# src/file_ops.py

from pathlib import Path
import os
import re
from typing import Union
from coding_agent.config import config_manager
from coding_agent.logger import agent_logger
import mimetypes

class FileOps:
    def __init__(self, root: str = "."):
        self.config = config_manager.get_agent_config()
        self.security_config = config_manager.get_security_config()
        self.root = Path(root).resolve()
        # Use configured allowed extensions or default set
        self.allowed_extensions = self.config.allowed_extensions

    def _validate_path(self, file_path: str) -> tuple[bool, Union[Path, str]]:
        """Validate that the file path is safe and within the allowed workspace directory."""
        try:
            path = Path(file_path)

            # Prevent directory traversal
            if '..' in path.parts:
                agent_logger.log_security_event("PATH_TRAVERSAL_ATTEMPT", f"Detected path traversal in {file_path}")
                return False, "Path traversal detected"

            # Prevent absolute paths
            if path.is_absolute():
                # If workspace restriction is enabled, reject absolute paths
                if self.security_config.restrict_file_operations_to_workspace:
                    agent_logger.log_security_event("ABSOLUTE_PATH_ATTEMPT", f"Detected absolute path {file_path}")
                    return False, "Absolute paths are not allowed"

            # Resolve the full path and ensure it's within the allowed root
            if self.security_config.restrict_file_operations_to_workspace:
                full_path = (self.root / path).resolve()
                try:
                    full_path.relative_to(self.root)
                except ValueError:
                    agent_logger.log_security_event("OUTSIDE_WORKSPACE_ACCESS",
                                                   f"Attempt to access file outside workspace: {file_path}")
                    return False, "Path is outside the allowed workspace directory"
            else:
                full_path = path.resolve()

            return True, full_path

        except Exception as e:
            agent_logger.log_error("PATH_VALIDATION_ERROR", str(e), f"Error validating path: {file_path}")
            return False, f"Error validating path: {e}"

    def _validate_file_type(self, file_path: str) -> bool:
        """Validate that the file type is allowed for operations."""
        path = Path(file_path)

        if self.security_config.validate_file_extensions:
            if path.suffix.lower() not in self.config.allowed_extensions:
                return False
        return True

    def _is_binary_file(self, file_path: Path) -> bool:
        """Check if a file is binary using mimetypes."""
        file_type, _ = mimetypes.guess_type(str(file_path))
        if file_type:
            return not file_type.startswith('text/')
        # Fallback: check for null bytes or non-printable characters
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                if b'\x00' in chunk:
                    return True
                try:
                    chunk.decode('utf-8')
                    return False
                except UnicodeDecodeError:
                    return True
        except Exception:
            return True  # If we can't read the file, assume binary

    def _read_file_impl(self, file_path: str) -> str:
        """Implementation of read_file with security checks."""
        from coding_agent.error_handler import validate_file_path, handle_error, handle_success, ErrorCode

        # Use error handler validation
        validation_response = validate_file_path(file_path)
        if not validation_response.success:
            return f"Error: {validation_response.message}"

        is_valid, result = self._validate_path(file_path)
        if not is_valid:
            return f"Error: {result}"

        path = result
        # Additional check to prevent reading system files
        if not path.exists() or not path.is_file():
            error_response = handle_error(
                ErrorCode.FILE_NOT_FOUND,
                f"File '{file_path}' does not exist or is not a file"
            )
            agent_logger.log_file_operation("read", file_path, False, error_response.message)
            return f"Error: {error_response.message}"

        # Check if it's a binary file
        if self._is_binary_file(path):
            error_response = handle_error(
                ErrorCode.INVALID_FILE_TYPE,
                f"Cannot read binary file '{file_path}'"
            )
            agent_logger.log_file_operation("read", file_path, False, error_response.message)
            return f"Error: {error_response.message}"

        # Validate file type
        if not self._validate_file_type(file_path):
            error_response = handle_error(
                ErrorCode.INVALID_FILE_TYPE,
                f"File extension '{path.suffix}' is not allowed for reading"
            )
            agent_logger.log_file_operation("read", file_path, False, error_response.message)
            return f"Error: {error_response.message}"

        try:
            # Limit file size to prevent reading very large files
            file_size = path.stat().st_size
            max_size = self.config.max_file_size_mb * 1024 * 1024  # Convert to bytes
            if file_size > max_size:
                error_response = handle_error(
                    ErrorCode.FILE_TOO_LARGE,
                    f"File too large to read (max: {self.config.max_file_size_mb}MB)"
                )
                agent_logger.log_file_operation("read", file_path, False, error_response.message)
                return f"Error: {error_response.message}"

            content = path.read_text(encoding="utf-8")
            agent_logger.log_file_operation("read", file_path, True, f"Read {len(content)} characters")
            return content
        except Exception as e:
            error_response = handle_error(
                ErrorCode.UNKNOWN_ERROR,
                f"Error reading file '{file_path}': {e}"
            )
            agent_logger.log_file_operation("read", file_path, False, str(e))
            return f"Error: {error_response.message}"

    def read_file(self, file_path: str) -> str:
        """Read a file with security checks."""
        # Use the original implementation (without complex caching for now)
        return self._read_file_impl(file_path)

    def write_file(self, file_path: str, content: str) -> Union[bool, str]:
        """Write to a file with security checks."""
        from coding_agent.error_handler import validate_file_path, handle_error, handle_success, ErrorCode
        from coding_agent.performance import invalidate_file_cache

        # Use error handler validation
        validation_response = validate_file_path(file_path)
        if not validation_response.success:
            return f"Error: {validation_response.message}"

        is_valid, result = self._validate_path(file_path)
        if not is_valid:
            return f"Error: {result}"

        path = result
        # Validate file type
        if not self._validate_file_type(file_path):
            error_response = handle_error(
                ErrorCode.INVALID_FILE_TYPE,
                f"File extension '{path.suffix}' is not allowed for writing"
            )
            agent_logger.log_file_operation("write", file_path, False, error_response.message)
            return f"Error: {error_response.message}"

        # Check if content is binary (has null bytes or non-printable characters)
        try:
            content.encode('utf-8')
        except UnicodeEncodeError:
            error_response = handle_error(
                ErrorCode.INVALID_FILE_TYPE,
                "Content contains invalid characters"
            )
            agent_logger.log_file_operation("write", file_path, False, error_response.message)
            return f"Error: {error_response.message}"

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            # Invalidate cache for this file since we're changing it
            invalidate_file_cache(file_path)
            agent_logger.log_file_operation("write", file_path, True, f"Wrote {len(content)} characters")
            return True
        except Exception as e:
            error_response = handle_error(
                ErrorCode.UNKNOWN_ERROR,
                f"Error writing file '{file_path}': {e}"
            )
            agent_logger.log_file_operation("write", file_path, False, str(e))
            return f"Error: {error_response.message}"

    def append_to_file(self, file_path: str, content: str) -> Union[bool, str]:
        """Append content to an existing file with security checks."""
        from coding_agent.error_handler import validate_file_path, handle_error, handle_success, ErrorCode
        from coding_agent.performance import invalidate_file_cache

        # Use error handler validation
        validation_response = validate_file_path(file_path)
        if not validation_response.success:
            return f"Error: {validation_response.message}"

        is_valid, result = self._validate_path(file_path)
        if not is_valid:
            return f"Error: {result}"

        path = result
        # Validate file type
        if not self._validate_file_type(file_path):
            error_response = handle_error(
                ErrorCode.INVALID_FILE_TYPE,
                f"File extension '{path.suffix}' is not allowed for appending"
            )
            agent_logger.log_file_operation("append", file_path, False, error_response.message)
            return f"Error: {error_response.message}"

        # Check if content is binary (has null bytes or non-printable characters)
        try:
            content.encode('utf-8')
        except UnicodeEncodeError:
            error_response = handle_error(
                ErrorCode.INVALID_FILE_TYPE,
                "Content contains invalid characters"
            )
            agent_logger.log_file_operation("append", file_path, False, error_response.message)
            return f"Error: {error_response.message}"

        try:
            # Check if file exists before appending
            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                # Create the file if it doesn't exist
                path.write_text(content, encoding="utf-8")
            else:
                # Append to existing file
                with open(path, "a", encoding="utf-8") as f:
                    f.write(content)
            # Invalidate cache for this file since we're changing it
            invalidate_file_cache(file_path)
            agent_logger.log_file_operation("append", file_path, True, f"Appended {len(content)} characters")
            return True
        except Exception as e:
            error_response = handle_error(
                ErrorCode.UNKNOWN_ERROR,
                f"Error appending to file '{file_path}': {e}"
            )
            agent_logger.log_file_operation("append", file_path, False, str(e))
            return f"Error: {error_response.message}"

    def delete_file(self, file_path: str) -> Union[bool, str]:
        """Delete a file with security checks."""
        from coding_agent.error_handler import validate_file_path, handle_error, handle_success, ErrorCode
        from coding_agent.performance import invalidate_file_cache

        # Use error handler validation
        validation_response = validate_file_path(file_path)
        if not validation_response.success:
            return f"Error: {validation_response.message}"

        is_valid, result = self._validate_path(file_path)
        if not is_valid:
            return f"Error: {result}"

        path = result
        # Additional check to prevent deleting non-existent files
        if not path.exists() or not path.is_file():
            error_response = handle_error(
                ErrorCode.FILE_NOT_FOUND,
                f"File '{file_path}' does not exist or is not a file"
            )
            agent_logger.log_file_operation("delete", file_path, False, error_response.message)
            return f"Error: {error_response.message}"

        try:
            path.unlink()  # Delete the file
            # Invalidate cache for this file since we're removing it
            invalidate_file_cache(file_path)
            agent_logger.log_file_operation("delete", file_path, True, "File deleted successfully")
            return True
        except Exception as e:
            error_response = handle_error(
                ErrorCode.UNKNOWN_ERROR,
                f"Error deleting file '{file_path}': {e}"
            )
            agent_logger.log_file_operation("delete", file_path, False, str(e))
            return f"Error: {error_response.message}"

    def list_files(self, pattern: str = "**/*.py") -> list[str]:
        """List files with security checks."""
        from coding_agent.error_handler import handle_error, handle_success, ErrorCode

        # Ensure the pattern is safe and doesn't contain path traversal
        if '..' in pattern:
            error_response = handle_error(
                ErrorCode.SECURITY_VIOLATION,
                "Pattern contains path traversal",
                {"pattern": pattern}
            )
            agent_logger.log_error("LIST_FILES_ERROR", error_response.message, pattern)
            return [f"Error: {error_response.message}"]

        try:
            files = []
            for p in self.root.glob(pattern):
                if p.is_file():
                    # Only include files in allowed extensions if validation is enabled
                    if not self.config.validate_file_extensions or self._validate_file_type(str(p)):
                        files.append(str(p.relative_to(self.root)))

            agent_logger.log_file_operation("list", pattern, True, f"Found {len(files)} files")
            return files
        except Exception as e:
            error_response = handle_error(
                ErrorCode.UNKNOWN_ERROR,
                f"Error listing files with pattern '{pattern}': {e}",
                {"pattern": pattern}
            )
            agent_logger.log_error("LIST_FILES_ERROR", str(e), pattern)
            return [f"Error: {error_response.message}"]

    def create_directory(self, dir_path: str) -> Union[bool, str]:
        """Create a directory with security checks."""
        from coding_agent.error_handler import validate_file_path, handle_error, handle_success, ErrorCode

        # Use error handler validation
        validation_response = validate_file_path(dir_path)
        if not validation_response.success:
            return f"Error: {validation_response.message}"

        is_valid, result = self._validate_path(dir_path)
        if not is_valid:
            return f"Error: {result}"

        path = result
        try:
            path.mkdir(parents=True, exist_ok=True)
            agent_logger.log_file_operation("create_dir", dir_path, True, "Directory created successfully")
            return True
        except Exception as e:
            error_response = handle_error(
                ErrorCode.UNKNOWN_ERROR,
                f"Error creating directory '{dir_path}': {e}"
            )
            agent_logger.log_file_operation("create_dir", dir_path, False, str(e))
            return f"Error: {error_response.message}"
