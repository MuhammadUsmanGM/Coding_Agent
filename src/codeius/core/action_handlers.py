"""
Action handlers for the CodingAgent.
Separates the action handling logic into modular components.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple, Optional
from codeius.utils.file_ops import FileOps
from codeius.utils.git_ops import GitOps
from codeius.core.code_analyzer import CodeAnalyzer
from codeius.utils.logger import agent_logger
from codeius.provider.mcp import MCPProvider
from codeius.core.interactive_session import interactive_session_manager


class ActionHandler(ABC):
    """Abstract base class for action handlers."""
    
    def __init__(self, file_ops: FileOps, git_ops: GitOps):
        self.file_ops = file_ops
        self.git_ops = git_ops

    @abstractmethod
    def handle(self, action: Dict[str, Any], search_provider: Optional[Any] = None) -> Tuple[str, bool]:
        """Handle the action and return result and success status."""
        pass


class ReadFileHandler(ActionHandler):
    """Handle read_file actions."""
    
    def handle(self, action: Dict[str, Any], search_provider: Optional[Any] = None) -> Tuple[str, bool]:
        content = self.file_ops.read_file(action["path"])
        result = f"🔹 Read `{action['path']}`:\n{content}"
        success = not content.startswith("Error:")
        agent_logger.log_file_operation("read", action["path"], success, 
                                       "File read successfully" if success else content)
        return result, success


class WriteFileHandler(ActionHandler):
    """Handle write_file actions."""
    
    def handle(self, action: Dict[str, Any], search_provider: Optional[Any] = None) -> Tuple[str, bool]:
        res = self.file_ops.write_file(action["path"], action["content"])
        if res is True:
            result = f"✅ Wrote `{action['path']}`."
            agent_logger.log_file_operation("write", action["path"], True, "File written successfully")
            return result, True
        else:
            result = f"❌ Error writing `{action['path']}`: {res}"
            agent_logger.log_file_operation("write", action["path"], False, str(res))
            return result, False


class AppendToFileHandler(ActionHandler):
    """Handle append_to_file actions."""
    
    def handle(self, action: Dict[str, Any], search_provider: Optional[Any] = None) -> Tuple[str, bool]:
        res = self.file_ops.append_to_file(action["path"], action["content"])
        if res is True:
            result = f"✅ Appended to `{action['path']}`."
            agent_logger.log_file_operation("append", action["path"], True, "Content appended successfully")
            return result, True
        else:
            result = f"❌ Error appending to `{action['path']}`: {res}"
            agent_logger.log_file_operation("append", action["path"], False, str(res))
            return result, False


class DeleteFileHandler(ActionHandler):
    """Handle delete_file actions."""
    
    def handle(self, action: Dict[str, Any], search_provider: Optional[Any] = None) -> Tuple[str, bool]:
        res = self.file_ops.delete_file(action["path"])
        if res is True:
            result = f"🗑️ Deleted `{action['path']}`."
            agent_logger.log_file_operation("delete", action["path"], True, "File deleted successfully")
            return result, True
        else:
            result = f"❌ Error deleting `{action['path']}`: {res}"
            agent_logger.log_file_operation("delete", action["path"], False, str(res))
            return result, False


class ListFilesHandler(ActionHandler):
    """Handle list_files actions."""
    
    def handle(self, action: Dict[str, Any], search_provider: Optional[Any] = None) -> Tuple[str, bool]:
        pattern = action.get("pattern", "**/*.py")  # Default pattern if not specified
        files = self.file_ops.list_files(pattern)
        if isinstance(files, list) and not any(f.startswith("Error:") for f in files):
            result = f"📋 Found {len(files)} files matching '{pattern}':\n" + "\n".join(f"- {f}" for f in files)
            agent_logger.log_file_operation("list", pattern, True, f"Listed {len(files)} files")
            return result, True
        else:
            error_msg = files[0] if isinstance(files, list) else str(files)
            result = f"❌ Error listing files with pattern '{pattern}': {error_msg}"
            agent_logger.log_file_operation("list", pattern, False, error_msg)
            return result, False


class CreateDirectoryHandler(ActionHandler):
    """Handle create_directory actions."""
    
    def handle(self, action: Dict[str, Any], search_provider: Optional[Any] = None) -> Tuple[str, bool]:
        res = self.file_ops.create_directory(action["path"])
        if res is True:
            result = f"📁 Created directory `{action['path']}`."
            agent_logger.log_file_operation("create_dir", action["path"], True, "Directory created successfully")
            return result, True
        else:
            result = f"❌ Error creating directory `{action['path']}`: {res}"
            agent_logger.log_file_operation("create_dir", action["path"], False, str(res))
            return result, False


class GitCommitHandler(ActionHandler):
    """Handle git_commit actions."""
    
    def handle(self, action: Dict[str, Any], search_provider: Optional[Any] = None) -> Tuple[str, bool]:
        self.git_ops.stage_files(".")
        cm = self.git_ops.commit(action["message"])
        result = f"✅ Git commit: {action['message']}"
        agent_logger.log_file_operation("git", "git commit", True, f"Committed with message: {action['message']}")
        return result, True


class WebSearchHandler(ActionHandler):
    """Handle web_search actions."""
    
    def handle(self, action: Dict[str, Any], search_provider: Optional[Any] = None) -> Tuple[str, bool]:
        # Handle web search if provider is available
        if search_provider:
            if isinstance(search_provider, MCPProvider) and search_provider.server_name == 'duckduckgo':
                # Create a message to send to the search provider
                import time

                search_messages = [
                    {"role": "user", "content": f"Search for information about: {action['query']}"}
                ]
                search_start = time.time()
                answer = search_provider.chat(search_messages)
                search_duration = time.time() - search_start
                result = f"🌐 DuckDuckGo search for '{action['query']}':\n{answer}\n"
                agent_logger.log_api_call("duckduckgo", "search", 200, search_duration)
                return result, True
            else:
                result = f"⚠️ Invalid search provider for query: {action['query']}"
                return result, False
        else:
            result = f"⚠️ No search provider available for query: {action['query']}"
            agent_logger.app_logger.warning(f"No search provider available for query: {action['query']}")
            return result, False


class AnalyzeCodeHandler(ActionHandler):
    """Handle analyze_code actions."""
    
    def __init__(self, file_ops: FileOps, git_ops: GitOps):
        super().__init__(file_ops, git_ops)
        self.analyzer = CodeAnalyzer()

    def handle(self, action: Dict[str, Any], search_provider: Optional[Any] = None) -> Tuple[str, bool]:
        # Get the file content first if path is provided
        if "path" in action:
            # Read the file content
            content = self.file_ops.read_file(action["path"])
            if content.startswith("Error:"):
                result = f"❌ Error reading file to analyze: {content}"
                return result, False
            else:
                analysis_result = self.analyzer.analyze_code(action["path"], content)
                suggestions = self.analyzer.get_code_suggestions(analysis_result)
                result = f"🔍 Code analysis for `{action['path']}`:\n" + "\n".join(f"- {suggestion}" for suggestion in suggestions)
                return result, True
        # If content is directly provided instead of a path
        elif "content" in action and "filename" in action:
            analysis_result = self.analyzer.analyze_code(action["filename"], action["content"])
            suggestions = self.analyzer.get_code_suggestions(analysis_result)
            result = f"🔍 Code analysis for `{action['filename']}`:\n" + "\n".join(f"- {suggestion}" for suggestion in suggestions)
            return result, True
        else:
            result = "❌ Error: analyze_code action requires either 'path' or both 'content' and 'filename' parameters"
            return result, False

class StartProcessHandler(ActionHandler):
    """Handle start_process actions."""

    def handle(self, action: Dict[str, Any], search_provider: Optional[Any] = None) -> Tuple[str, bool]:
        pid = interactive_session_manager.start_process(action["command"])
        result = f"🚀 Started process with PID: {pid}"
        return result, True


class SendInputHandler(ActionHandler):
    """Handle send_input actions."""

    def handle(self, action: Dict[str, Any], search_provider: Optional[Any] = None) -> Tuple[str, bool]:
        interactive_session_manager.send_input(action["pid"], action["data"])
        result = f"📥 Sent input to process {action['pid']}"
        return result, True


class ReadOutputHandler(ActionHandler):
    """Handle read_output actions."""

    def handle(self, action: Dict[str, Any], search_provider: Optional[Any] = None) -> Tuple[str, bool]:
        output = interactive_session_manager.read_output(action["pid"])
        result = f"📤 Output from process {action['pid']}:\n{output}"
        return result, True


class ReadErrorHandler(ActionHandler):
    """Handle read_error actions."""

    def handle(self, action: Dict[str, Any], search_provider: Optional[Any] = None) -> Tuple[str, bool]:
        error = interactive_session_manager.read_error(action["pid"])
        result = f"🚨 Error from process {action['pid']}:\n{error}"
        return result, True


class StopProcessHandler(ActionHandler):
    """Handle stop_process actions."""

    def handle(self, action: Dict[str, Any], search_provider: Optional[Any] = None) -> Tuple[str, bool]:
        interactive_session_manager.stop_process(action["pid"])
        result = f"🛑 Stopped process {action['pid']}"
        return result, True

# Dictionary mapping action types to their handlers
ACTION_HANDLERS: Dict[str, type] = {
    "read_file": ReadFileHandler,
    "write_file": WriteFileHandler,
    "append_to_file": AppendToFileHandler,
    "delete_file": DeleteFileHandler,
    "list_files": ListFilesHandler,
    "create_directory": CreateDirectoryHandler,
    "git_commit": GitCommitHandler,
    "web_search": WebSearchHandler,
    "analyze_code": AnalyzeCodeHandler,
    "start_process": StartProcessHandler,
    "send_input": SendInputHandler,
    "read_output": ReadOutputHandler,
    "read_error": ReadErrorHandler,
    "stop_process": StopProcessHandler,
}