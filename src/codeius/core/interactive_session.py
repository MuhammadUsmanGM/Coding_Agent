# src/coding_agent/interactive_session.py

import subprocess
import threading
from typing import Dict, Optional

class InteractiveSession:
    """Manages interactive sessions with background processes."""

    def __init__(self):
        self.processes: Dict[int, subprocess.Popen] = {}

    def start_process(self, command: str) -> int:
        """Starts a new process in the background."""
        process = subprocess.Popen(
            command,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )
        pid = process.pid
        self.processes[pid] = process
        return pid

    def send_input(self, pid: int, data: str):
        """Sends input to the stdin of a running process."""
        if pid in self.processes:
            process = self.processes[pid]
            if process.stdin:
                process.stdin.write(data)
                process.stdin.flush()

    def read_output(self, pid: int) -> Optional[str]:
        """Reads the output from the stdout of a running process."""
        if pid in self.processes:
            process = self.processes[pid]
            if process.stdout:
                return process.stdout.readline()
        return None

    def read_error(self, pid: int) -> Optional[str]:
        """Reads the error from the stderr of a running process."""
        if pid in self.processes:
            process = self.processes[pid]
            if process.stderr:
                return process.stderr.readline()
        return None

    def stop_process(self, pid: int):
        """Terminates a running process."""
        if pid in self.processes:
            process = self.processes[pid]
            process.terminate()
            del self.processes[pid]

# Global interactive session manager
interactive_session_manager = InteractiveSession()
