# src/file_ops.py

from pathlib import Path
import os
import re

class FileOps:
    def __init__(self, root="."):
        self.root = Path(root).resolve()
        # Define allowed file extensions to prevent writing to unexpected file types
        self.allowed_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', 
                                   '.json', '.txt', '.md', '.yaml', '.yml', '.xml', '.ini', 
                                   '.cfg', '.conf', '.env'}

    def _validate_path(self, file_path):
        """Validate that the file path is safe and within the allowed root directory."""
        path = Path(file_path)
        
        # Prevent directory traversal
        if '..' in path.parts or path.is_absolute():
            return False, "Path traversal detected"
        
        # Resolve the full path and ensure it's within the allowed root
        full_path = (self.root / file_path).resolve()
        try:
            full_path.relative_to(self.root)
        except ValueError:
            return False, "Path is outside the allowed root directory"
        
        return True, full_path

    def read_file(self, file_path):
        is_valid, result = self._validate_path(file_path)
        if not is_valid:
            return f"Error: {result}"
        
        path = result
        # Additional check to prevent reading system files
        if not path.exists() or not path.is_file():
            return f"Error: File '{file_path}' does not exist or is not a file"
        
        try:
            # Limit file size to prevent reading very large files
            if path.stat().st_size > 10 * 1024 * 1024:  # 10MB limit
                return "Error: File too large to read"
            return path.read_text(encoding="utf-8")
        except Exception as e:
            return f"Error reading file '{file_path}': {e}"

    def write_file(self, file_path, content):
        is_valid, result = self._validate_path(file_path)
        if not is_valid:
            return f"Error: {result}"
        
        path = result
        # Check file extension to ensure it's an allowed type
        if path.suffix.lower() not in self.allowed_extensions:
            return f"Error: File extension '{path.suffix}' is not allowed for writing"
        
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return True
        except Exception as e:
            return f"Error writing file '{file_path}': {e}"

    def list_files(self, pattern="**/*.py"):
        # Ensure the pattern is safe and doesn't contain path traversal
        if '..' in pattern:
            return ["Error: Pattern contains invalid characters"]
        
        try:
            return [str(p.relative_to(self.root)) for p in self.root.glob(pattern) if p.is_file()]
        except Exception as e:
            return [f"Error listing files with pattern '{pattern}': {e}"]
