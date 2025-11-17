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
                if self.config.restrict_file_operations_to_workspace:
                    agent_logger.log_security_event("ABSOLUTE_PATH_ATTEMPT", f"Detected absolute path {file_path}")
                    return False, "Absolute paths are not allowed"

            # Resolve the full path and ensure it's within the allowed root
            if self.config.restrict_file_operations_to_workspace:
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

        if self.config.validate_file_extensions:
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
        except:
            return True  # If we can't read the file, assume binary

    def read_file(self, file_path: str) -> str:
        """Read a file with security checks."""
        is_valid, result = self._validate_path(file_path)
        if not is_valid:
            return f"Error: {result}"

        path = result
        # Additional check to prevent reading system files
        if not path.exists() or not path.is_file():
            agent_logger.log_file_operation("read", file_path, False, "File does not exist or is not a file")
            return f"Error: File '{file_path}' does not exist or is not a file"

        # Check if it's a binary file
        if self._is_binary_file(path):
            agent_logger.log_file_operation("read", file_path, False, "Attempt to read binary file")
            return f"Error: Cannot read binary file '{file_path}'"

        # Validate file type
        if not self._validate_file_type(file_path):
            agent_logger.log_file_operation("read", file_path, False, "File type not allowed")
            return f"Error: File extension '{path.suffix}' is not allowed for reading"

        try:
            # Limit file size to prevent reading very large files
            file_size = path.stat().st_size
            max_size = self.config.max_file_size_mb * 1024 * 1024  # Convert to bytes
            if file_size > max_size:
                agent_logger.log_file_operation("read", file_path, False, f"File too large: {file_size} bytes")
                return f"Error: File too large to read (max: {self.config.max_file_size_mb}MB)"

            content = path.read_text(encoding="utf-8")
            agent_logger.log_file_operation("read", file_path, True, f"Read {len(content)} characters")
            return content
        except Exception as e:
            agent_logger.log_file_operation("read", file_path, False, str(e))
            return f"Error reading file '{file_path}': {e}"

    def write_file(self, file_path: str, content: str) -> Union[bool, str]:
        """Write to a file with security checks."""
        is_valid, result = self._validate_path(file_path)
        if not is_valid:
            return f"Error: {result}"

        path = result
        # Validate file type
        if not self._validate_file_type(file_path):
            agent_logger.log_file_operation("write", file_path, False, "File type not allowed")
            return f"Error: File extension '{path.suffix}' is not allowed for writing"

        # Check if content is binary (has null bytes or non-printable characters)
        try:
            content.encode('utf-8')
        except UnicodeEncodeError:
            agent_logger.log_file_operation("write", file_path, False, "Content contains invalid characters")
            return f"Error: Content contains invalid characters"

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            agent_logger.log_file_operation("write", file_path, True, f"Wrote {len(content)} characters")
            return True
        except Exception as e:
            agent_logger.log_file_operation("write", file_path, False, str(e))
            return f"Error writing file '{file_path}': {e}"

    def list_files(self, pattern: str = "**/*.py") -> list[str]:
        """List files with security checks."""
        # Ensure the pattern is safe and doesn't contain path traversal
        if '..' in pattern:
            agent_logger.log_error("LIST_FILES_ERROR", "Pattern contains path traversal", pattern)
            return ["Error: Pattern contains invalid characters"]

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
            agent_logger.log_error("LIST_FILES_ERROR", str(e), pattern)
            return [f"Error listing files with pattern '{pattern}': {e}"]
