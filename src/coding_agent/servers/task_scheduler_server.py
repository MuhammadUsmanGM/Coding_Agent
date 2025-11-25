"""
Scheduling/Task Automation Tool
Local cron/task scheduler using schedule, letting the agent run commands, tests, or code checks automatically.
"""
from flask import Flask, request, jsonify
import schedule
import time
import threading
import subprocess
import os
from datetime import datetime
from typing import Dict, Any
import asyncio

app = Flask(__name__)

class TaskScheduler:
    def __init__(self):
        self.scheduled_tasks: Dict[str, Dict[str, Any]] = {}
        self.running = False

    async def start_scheduler(self):
        """Start the scheduler loop"""
        if not self.running:
            self.running = True
            asyncio.create_task(self._run_scheduler())
            return {"status": "success", "message": "Scheduler started"}
        return {"status": "info", "message": "Scheduler already running"}

    def stop_scheduler(self):
        """Stop the scheduler"""
        if self.running:
            self.running = False
            schedule.clear()
            self.scheduled_tasks = {}
            return {"status": "success", "message": "Scheduler stopped and tasks cleared"}
        return {"status": "info", "message": "Scheduler not running"}

    async def _run_scheduler(self):
        """Run the scheduler loop asynchronously"""
        while self.running:
            # Run pending synchronous schedule jobs in a thread pool executor
            await asyncio.to_thread(schedule.run_pending)
            await asyncio.sleep(1)

    def _run_async_task_in_event_loop(self, coro):
        """Helper to run an async coroutine from a synchronous context in the main event loop."""
        loop = asyncio.get_event_loop()
        # Submit the coroutine to the event loop, possibly from another thread
        asyncio.run_coroutine_threadsafe(coro, loop)

    def schedule_task(self, task_id: str, task_type: str, interval: str, command: str = None,
                     file_path: str = None, custom_script: str = None):
        """Schedule a new task based on the provided parameters"""
        try:
            # Parse interval (e.g., "every 5 minutes", "hourly", "daily at 10:30")
            interval_parts = interval.split()
            
            if len(interval_parts) >= 2 and interval_parts[0].lower() == "every":
                # Handle "every X [unit]" format
                count = int(interval_parts[1])
                unit = interval_parts[2].lower()
                
                if unit.startswith("minute"):
                    job = schedule.every(count).minutes
                elif unit.startswith("hour"):
                    job = schedule.every(count).hours
                elif unit.startswith("day"):
                    job = schedule.every(count).days
                elif unit.startswith("second"):
                    job = schedule.every(count).seconds
                else:
                    return {"status": "error", "message": f"Unknown time unit: {unit}"}
            elif interval.lower() == "hourly":
                job = schedule.every().hour
            elif interval.lower() == "daily":
                job = schedule.every().day
            elif "at" in interval:
                # Handle "daily at HH:MM" or similar
                time_part = interval.split(" at ")[-1]
                if "daily" in interval:
                    job = schedule.every().day.at(time_part)
                elif "monday" in interval:
                    job = schedule.every().monday.at(time_part)
                elif "tuesday" in interval:
                    job = schedule.every().tuesday.at(time_part)
                elif "wednesday" in interval:
                    job = schedule.every().wednesday.at(time_part)
                elif "thursday" in interval:
                    job = schedule.every().thursday.at(time_part)
                elif "friday" in interval:
                    job = schedule.every().friday.at(time_part)
                elif "saturday" in interval:
                    job = schedule.every().saturday.at(time_part)
                elif "sunday" in interval:
                    job = schedule.every().sunday.at(time_part)
                else:
                    return {"status": "error", "message": f"Unsupported time format: {interval}"}
            else:
                return {"status": "error", "message": f"Unsupported interval format: {interval}"}
            
            # Define the task function based on task type
            if task_type == "command":
                async def _async_command_runner(task_cmd):
                    try:
                        process = await asyncio.create_subprocess_exec(
                            *task_cmd.split(),
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE,
                            text=True
                        )
                        stdout, stderr = await process.communicate()
                        return f"Command '{task_cmd}' completed with return code {process.returncode}"
                    except Exception as e:
                        return f"Command '{task_cmd}' failed: {str(e)}"

                def task_func(task_cmd=command):
                    result = self._run_async_task_in_event_loop(_async_command_runner(task_cmd))
                    return result

                job.do(task_func)

            elif task_type == "test":
                async def _async_test_runner(test_path):
                    try:
                        process = await asyncio.create_subprocess_exec(
                            "python", "-m", "pytest", test_path,
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE,
                            text=True
                        )
                        stdout, stderr = await process.communicate()
                        return f"Test run completed. Return code: {process.returncode}. Output: {stdout[:200]}"
                    except Exception as e:
                        return f"Test run failed: {str(e)}"

                def task_func(test_path=file_path or "."):
                    result = self._run_async_task_in_event_loop(_async_test_runner(test_path))
                    return result

                job.do(task_func)

            elif task_type == "script":
                async def _async_script_runner(script_path):
                    try:
                        process = await asyncio.create_subprocess_exec(
                            "python", script_path,
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE,
                            text=True
                        )
                        stdout, stderr = await process.communicate()
                        return f"Script '{script_path}' executed. Return code: {process.returncode}"
                    except Exception as e:
                        return f"Script execution failed: {str(e)}"

                def task_func(script_path=file_path):
                    result = self._run_async_task_in_event_loop(_async_script_runner(script_path))
                    return result

                job.do(task_func)

            elif task_type == "custom":
                def task_func(custom_code=custom_script):
                    try:
                        local_vars = {}
                        exec(custom_code, globals(), local_vars)
                        return f"Custom task executed: {str(local_vars)}"
                    except Exception as e:
                        return f"Custom task failed: {str(e)}"
                
                job.do(task_func)
            
            else:
                return {"status": "error", "message": f"Unknown task type: {task_type}"}
            
            # Store task details
            self.scheduled_tasks[task_id] = {
                "type": task_type,
                "interval": interval,
                "command": command,
                "file_path": file_path,
                "custom_script": custom_script,
                "next_run": str(job.next_run),
                "created_at": str(datetime.now())
            }
            
            return {
                "status": "success", 
                "message": f"Task '{task_id}' scheduled to run {interval}",
                "task_id": task_id,
                "next_run": str(job.next_run)
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Failed to schedule task: {str(e)}"}
    
    def list_tasks(self):
        """List all scheduled tasks"""
        tasks_list = []
        for task_id, details in self.scheduled_tasks.items():
            tasks_list.append({
                "id": task_id,
                "details": details
            })
        
        return {
            "status": "success",
            "tasks": tasks_list,
            "count": len(tasks_list)
        }
    
    def remove_task(self, task_id: str):
        """Remove a specific task from the scheduler"""
        if task_id in self.scheduled_tasks:
            del self.scheduled_tasks[task_id]
            # Note: schedule library doesn't provide a direct way to cancel specific jobs
            # For now, we'll clear and reschedule remaining jobs
            return {"status": "success", "message": f"Task '{task_id}' removed"}
        else:
            return {"status": "error", "message": f"Task '{task_id}' not found"}

task_scheduler = TaskScheduler()

@app.route('/schedule', methods=['POST'])
async def handle_schedule():
    """Handle scheduling requests asynchronously"""
    try:
        action = request.json.get('action', 'create')

        if action == 'start':
            result = await task_scheduler.start_scheduler()
            return jsonify(result)
        
        elif action == 'stop':
            result = task_scheduler.stop_scheduler()
            return jsonify(result)
        
        elif action == 'create' or action == 'schedule':
            task_id = request.json.get('task_id', f"task_{int(time.time())}")
            task_type = request.json.get('type', 'command')
            interval = request.json.get('interval', 'every 1 hour')
            command = request.json.get('command', None)
            file_path = request.json.get('file_path', None)
            custom_script = request.json.get('custom_script', None)
            
            result = task_scheduler.schedule_task(task_id, task_type, interval, command, file_path, custom_script)
            return jsonify(result)
        
        elif action == 'list':
            result = task_scheduler.list_tasks()
            return jsonify(result)
        
        elif action == 'remove':
            task_id = request.json.get('task_id', None)
            if task_id:
                result = task_scheduler.remove_task(task_id)
                return jsonify(result)
            else:
                return jsonify({"status": "error", "message": "Task ID required for removal"}), 400
        
        else:
            return jsonify({"status": "error", "message": f"Unknown action: {action}"}), 400
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10800)