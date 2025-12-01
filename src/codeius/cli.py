# src/cli.py

import sys
import os
import time
import shutil
import json
from pathlib import Path
from threading import Thread
from typing import Generator
from codeius.core.agent import CodingAgent
from codeius.core.dashboard import Dashboard
from codeius.core.context_manager import ContextManager
from codeius.core.context_cli import (
    display_context_summary,
    semantic_search_command,
    show_file_context,
    set_project_command,
    find_element_command,
    auto_detect_project_command
)
from codeius.core.security_cli import (
    run_security_scan,
    show_security_policy,
    update_security_policy,
    create_security_report,
    run_secrets_detection,
    run_vulnerability_scan,
    run_policy_check
)
from codeius.core.visualization_manager import VisualizationManager
from codeius.core.project_analyzer import analyze_current_project
from dotenv import load_dotenv
from rich.console import Console
from rich.text import Text
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table
from rich.box import HEAVY_HEAD
from rich import print as rprint
from rich.rule import Rule
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
import pyfiglet
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.shortcuts import CompleteStyle
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.layout import Layout
from prompt_toolkit.widgets import Box, Frame, TextArea
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.processors import BeforeInput
from prompt_toolkit.filters import is_multiline, has_suggestion
load_dotenv()

console = Console()

# Global variable to store the current theme
current_theme_name = "default"

# Define theme configurations
THEMES = {
    "default": {
        "interaction_style": Style.from_dict({
            'prompt': 'bold #00FFFF',
            'completion-menu': 'bg:#262626 #ffffff',
            'completion-menu.completion.current': 'bg:#4a4a4a #ffffff',
            'completion-menu.meta.completion': 'bg:#262626 #ffffff',
            'completion-menu.meta.completion.current': 'bg:#4a4a4a #ffffff',
        }),
        "shell_style": Style.from_dict({
            'prompt': 'bold #FF4500',  # Orange color for shell mode
            'completion-menu': 'bg:#4a4a4a #ffffff',
            'completion-menu.completion.current': 'bg:#262626 #ffffff',
            'completion-menu.meta.completion': 'bg:#4a4a4a #ffffff',
            'completion-menu.meta.completion.current': 'bg:#262626 #ffffff',
        }),
        "interaction_prompt_text": HTML('<style fg="#00FFFF" bg="black"><b>✦ Type your message or @path/to/file:</b> </style> '),
        "shell_prompt_text": HTML('<style fg="#FF4500" bg="black"><b>🐚 Shell Mode:</b> </style> '),
    },
    "dark": {
        "interaction_style": Style.from_dict({
            'prompt': 'bold #6A0DAD', # Dark purple
            'completion-menu': 'bg:#1a1a1a #cccccc',
            'completion-menu.completion.current': 'bg:#3a3a3a #ffffff',
            'completion-menu.meta.completion': 'bg:#1a1a1a #cccccc',
            'completion-menu.meta.completion.current': 'bg:#3a3a3a #ffffff',
        }),
        "shell_style": Style.from_dict({
            'prompt': 'bold #FFD700',  # Gold for shell mode
            'completion-menu': 'bg:#3a3a3a #cccccc',
            'completion-menu.completion.current': 'bg:#1a1a1a #ffffff',
            'completion-menu.meta.completion': 'bg:#3a3a3a #cccccc',
            'completion-menu.meta.completion.current': 'bg:#1a1a1a #ffffff',
        }),
        "interaction_prompt_text": HTML('<style fg="#6A0DAD" bg="black"><b>✦ Dark Mode Message:</b> </style> '),
        "shell_prompt_text": HTML('<style fg="#FFD700" bg="black"><b>🐚 Dark Shell Mode:</b> </style> '),
    },
    "solarized": {
        "interaction_style": Style.from_dict({
            'prompt': 'bold #268bd2', # Solarized blue
            'completion-menu': 'bg:#002b36 #839496',
            'completion-menu.completion.current': 'bg:#073642 #fdf6e3',
            'completion-menu.meta.completion': 'bg:#002b36 #839496',
            'completion-menu.meta.completion.current': 'bg:#073642 #fdf6e3',
        }),
        "shell_style": Style.from_dict({
            'prompt': 'bold #cb4b16',  # Solarized orange for shell mode
            'completion-menu': 'bg:#073642 #839496',
            'completion-menu.completion.current': 'bg:#002b36 #fdf6e3',
            'completion-menu.meta.completion': 'bg:#073642 #839496',
            'completion-menu.meta.completion.current': 'bg:#002b36 #fdf6e3',
        }),
        "interaction_prompt_text": HTML('<style fg="#268bd2" bg="black"><b>✦ Solarized Input:</b> </style> '),
        "shell_prompt_text": HTML('<style fg="#cb4b16" bg="black"><b>🐚 Solarized Shell:</b> </style> '),
    },
    "terminal": {
        "interaction_style": Style.from_dict({
            'prompt': 'bold green',
            'completion-menu': 'bg:black green',
            'completion-menu.completion.current': 'bg:green black',
            'completion-menu.meta.completion': 'bg:black green',
            'completion-menu.meta.completion.current': 'bg:green black',
        }),
        "shell_style": Style.from_dict({
            'prompt': 'bold yellow',  # Yellow for shell mode
            'completion-menu': 'bg:green black',
            'completion-menu.completion.current': 'bg:black green',
            'completion-menu.meta.completion': 'bg:green black',
            'completion-menu.meta.completion.current': 'bg:black green',
        }),
        "interaction_prompt_text": HTML('<style fg="green" bg="black"><b>$ Enter command:</b> </style> '),
        "shell_prompt_text": HTML('<style fg="yellow" bg="black"><b>$ Shell></b> </style> '),
    },
}

def apply_theme(theme_name):
    global current_theme_name
    if theme_name in THEMES:
        current_theme_name = theme_name
        console.print(f"[bold green]Theme switched to '{theme_name}'[/bold green]")
    else:
        console.print(f"[bold red]Theme '{theme_name}' not found.[/bold red]")


def boxed_input_with_placeholder(
    placeholder="Type your message or @path/to/file",
    width=60,
    height=3,
    prompt_text="➤ "
):
    """
    Creates a rectangular input box with:
    - proper border
    - placeholder that disappears when typing
    """
    # Define styles for the input box and text area
    input_style = Style.from_dict({
        "frame.border": "#FF00FF",  # Magenta border
        "textarea": "white",
        "placeholder": "italic #888888",
        "prompt": "#00FFFF",  # Cyan for the prompt icon
    })

    # TextArea for input
    textarea = TextArea(
        multiline=True,
        wrap_lines=True,
        width=D.exact(width),
        height=D.exact(height),
        style="class:textarea",
        prompt=prompt_text,  # Leading icon
    )

    # Use true placeholder property
    textarea.placeholder = placeholder

    # Frame adds a rectangular border
    frame = Frame(
        textarea,
        style="class:frame",
        width=D.exact(width + 2),
        height=D.exact(height + 2)
    )

    # Return the layout and textarea for external use
    return HSplit([frame]), textarea, input_style

def confirm_safe_execution(result):
    console.print("The agent wants to perform these actions:", style="bold yellow")
    console.print(result)
    try:
        ask = Prompt.ask("Proceed?", choices=["y", "N"], default="N").strip().lower()
        return ask == "y"
    except Exception:
        # Fallback if prompt fails
        ask = input("Proceed? [y/N]: ").strip().lower()
        return ask == "y"

def display_mcp_servers(agent):
    """Display available MCP servers to the user"""
    # Get the MCP manager instance from the agent
    mcp_manager = agent.mcp_manager
    servers = mcp_manager.list_servers()
    
    if not servers:
        console.print("[yellow]No MCP servers available.[/yellow]")
        console.print("[dim]MCP servers provide access to various tools and services.[/dim]")
        return
    
    console.print("\n[bold blue]Available MCP Servers:[/bold blue]")
    for server in servers:
        status = "[green]ENABLED[/green]" if server.enabled else "[red]DISABLED[/red]"
        console.print(f"  [cyan]{server.name}[/cyan]: {server.description} - {status}")
        console.print(f"    Endpoint: {server.endpoint}")
        console.print(f"    Capabilities: {', '.join(server.capabilities)}")
    console.print("\n[bold]MCP servers provide additional tools like code execution and file access without external APIs.[/bold]\n")

def display_dashboard():
    """Display the real-time dashboard for code quality metrics"""
    dashboard = Dashboard()
    rich_table = dashboard.generate_rich_dashboard()
    console.print(rich_table)
    
    # Additional explanation
    console.print("\n[bold]Dashboard Legend:[/bold]")
    console.print("  [GOOD] Good - Metric is in healthy range")
    console.print("  [WARN] Warning - Metric could be improved")
    console.print("  [BAD] Poor - Metric needs attention\n")

def ocr_image(agent, image_path):
    """Process an image using OCR to extract text"""
    if not os.path.exists(image_path):
        console.print(f"[bold red]Error: Image file '{image_path}' does not exist.[/bold red]")
        return
    
    # Find the OCR provider
    ocr_provider = None
    for provider in agent.providers:
        if hasattr(provider, 'server_name') and provider.server_name == 'ocr':
            ocr_provider = provider
            break
    
    if not ocr_provider:
        console.print("[bold red]Error: OCR server not available.[/bold red]")
        return
    
    # In a real implementation, we would send the image to the OCR server
    # For now, we'll just simulate the process
    console.print(f"[bold yellow]Processing image: {image_path}[/bold yellow]")
    console.print("[bold]This would send the image to the OCR server for text extraction...[/bold]")
    console.print("[dim]In a real implementation, the image would be sent to the OCR server and the text would be returned.[/dim]")

def refactor_code(agent, file_path):
    """Analyze and refactor code in the specified file"""
    if not os.path.exists(file_path):
        console.print(f"[bold red]Error: File '{file_path}' does not exist.[/bold red]")
        return
    
    # Find the refactor provider
    refactor_provider = None
    for provider in agent.providers:
        if hasattr(provider, 'server_name') and provider.server_name == 'refactor':
            refactor_provider = provider
            break
    
    if not refactor_provider:
        console.print("[bold red]Error: Refactor server not available.[/bold red]")
        return
    
    # Read the file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        console.print(f"[bold red]Error reading file: {e}[/bold red]")
        return
    
    # In a real implementation, we would send the content to the refactor server
    # For now, we'll just simulate the process
    console.print(f"[bold yellow]Analyzing code in: {file_path}[/bold yellow]")
    console.print("[bold]This would send the code to the refactoring server for analysis...[/bold]")
    console.print("[dim]In a real implementation, the server would return issues and suggestions for refactoring.[/dim]")

def diff_files(agent, file1, file2):
    """Compare two files using the diff tool"""
    if not os.path.exists(file1):
        console.print(f"[bold red]Error: File '{file1}' does not exist.[/bold red]")
        return
    
    if not os.path.exists(file2):
        console.print(f"[bold red]Error: File '{file2}' does not exist.[/bold red]")
        return
    
    # Find the diff provider
    diff_provider = None
    for provider in agent.providers:
        if hasattr(provider, 'server_name') and provider.server_name == 'diff':
            diff_provider = provider
            break
    
    if not diff_provider:
        console.print("[bold red]Error: Diff server not available.[/bold red]")
        return
    
    # In a real implementation, we would send the file paths to the diff server
    # For now, we'll just simulate the process
    console.print(f"[bold yellow]Comparing files: {file1} vs {file2}[/bold yellow]")
    console.print("[bold]This would send the files to the diff server for comparison...[/bold]")
    console.print("[dim]In a real implementation, the server would return the differences between the files.[/dim]")

def visualization_task(agent, metric_type):
    """Handle visualization tasks for plotting metrics"""
    # Find the visualization provider
    visualization_provider = None
    for provider in agent.providers:
        if hasattr(provider, 'server_name') and provider.server_name == 'visualization':
            visualization_provider = provider
            break
    
    if not visualization_provider:
        console.print("[bold red]Error: Visualization server not available.[/bold red]")
        return
    
    console.print(f"[bold yellow]Creating plot for: {metric_type}[/bold yellow]")
    console.print("[bold]This would send the request to the visualization server...[/bold]")
    console.print("[dim]In a real implementation, the server would generate a plot and display it.[/dim]")

def snippet_task(agent, action, *args):
    """Handle snippet management tasks"""
    # Find the snippet manager provider
    snippet_provider = None
    for provider in agent.providers:
        if hasattr(provider, 'server_name') and provider.server_name == 'snippet_manager':
            snippet_provider = provider
            break
    
    if not snippet_provider:
        console.print("[bold red]Error: Snippet manager server not available.[/bold red]")
        return
    
    if action == 'get' or action == 'show':
        if len(args) < 1:
            console.print("[bold red]Please specify a snippet key. Usage: /snippet get [key][/bold red]")
            return
        key = args[0]
        console.print(f"[bold yellow]Retrieving snippet: {key}[/bold yellow]")
        console.print("[bold]This would send the request to the snippet manager server...[/bold]")
        console.print("[dim]In a real implementation, the server would return the snippet content.[/dim]")
    
    elif action == 'save' or action == 'add':
        if len(args) < 2:
            console.print("[bold red]Please specify a key and content. Usage: /snippet add [key] [description] [/bold red]")
            return
        key = args[0]
        console.print(f"[bold yellow]Saving snippet: {key}[/bold yellow]")
        console.print("[bold]This would send the request to the snippet manager server...[/bold]")
        console.print("[dim]In a real implementation, the server would save the snippet.[/dim]")
    
    elif action == 'list':
        console.print("[bold yellow]Listing all snippets...[/bold yellow]")
        console.print("[bold]This would send the request to the snippet manager server...[/bold]")
        console.print("[dim]In a real implementation, the server would return the list of snippets.[/dim]")
    
    elif action == 'insert':
        if len(args) < 2:
            console.print("[bold red]Please specify a snippet key and target. Usage: /snippet insert [key] [target_file][/bold red]")
            return
        key, target = args[0], args[1]
        console.print(f"[bold yellow]Inserting snippet '{key}' into {target}[/bold yellow]")
        console.print("[bold]This would send the request to the snippet manager server...[/bold]")
        console.print("[dim]In a real implementation, the server would retrieve the snippet and insert it into the target file.[/dim]")
    
    else:
        console.print(f"[bold red]Unknown snippet action: {action}[/bold red]")
        console.print("[bold]Available actions: get, add, list, insert[/bold]")

def scrape_task(agent, target, selector):
    """Handle web scraping tasks"""
    # Find the web scraper provider
    scraper_provider = None
    for provider in agent.providers:
        if hasattr(provider, 'server_name') and provider.server_name == 'web_scraper':
            scraper_provider = provider
            break
    
    if not scraper_provider:
        console.print("[bold red]Error: Web scraper server not available.[/bold red]")
        return
    
    console.print(f"[bold yellow]Scraping {target} with selector '{selector}'[/bold yellow]")
    console.print("[bold]This would send the request to the web scraper server...[/bold]")
    console.print("[dim]In a real implementation, the server would return scraped content.[/dim]")

def config_task(agent, action, *args):
    """Handle configuration management tasks"""
    # Find the config manager provider
    config_provider = None
    for provider in agent.providers:
        if hasattr(provider, 'server_name') and provider.server_name == 'config_manager':
            config_provider = provider
            break
    
    if not config_provider:
        console.print("[bold red]Error: Config manager server not available.[/bold red]")
        return
    
    if action == 'view' or action == 'show':
        console.print(f"[bold yellow]Viewing configuration...[/bold yellow]")
        console.print("[bold]This would send the request to the config manager server...[/bold]")
        console.print("[dim]In a real implementation, the server would return the configuration values.[/dim]")
    
    elif action == 'edit':
        if len(args) < 2:
            console.print("[bold red]Please specify a key and value. Usage: /config edit [key] [value][/bold red]")
            return
        key, value = args[0], args[1]
        console.print(f"[bold yellow]Editing config: {key} = {value}[/bold yellow]")
        console.print("[bold]This would send the request to the config manager server...[/bold]")
        console.print("[dim]In a real implementation, the server would update the configuration.[/dim]")
    
    elif action == 'list' or action == 'available':
        console.print("[bold yellow]Listing available configuration files...[/bold yellow]")
        console.print("[bold]This would send the request to the config manager server...[/bold]")
        console.print("[dim]In a real implementation, the server would return the list of available config files.[/dim]")
    
    else:
        console.print(f"[bold red]Unknown config action: {action}[/bold red]")
        console.print("[bold]Available actions: view, edit, list[/bold]")

def schedule_task(agent, task_type, interval, target=None):
    """Handle scheduling tasks"""
    # Find the task scheduler provider
    scheduler_provider = None
    for provider in agent.providers:
        if hasattr(provider, 'server_name') and provider.server_name == 'task_scheduler':
            scheduler_provider = provider
            break

    if not scheduler_provider:
        console.print("[bold red]Error: Task scheduler server not available.[/bold red]")
        return

    console.print(f"[bold yellow]Scheduling task: {task_type} every {interval}{' for ' + target if target else ''}[/bold yellow]")
    console.print("[bold]This would send the request to the task scheduler server...[/bold]")
    console.print("[dim]In a real implementation, the server would schedule the task to run automatically.[/dim]")

def run_all_tests():
    """Run all tests in the tests/ directory"""
    console.print("[bold yellow]Running all tests...[/bold yellow]")
    try:
        import subprocess
        result = subprocess.run(
            ["pytest", "tests/"],
            capture_output=True,
            text=True,
            timeout=300  # 5-minute timeout
        )
        
        table = Table(title="[bold green]Test Results[/bold green]", show_header=True, header_style="bold magenta")
        table.add_column("Status", style="cyan", no_wrap=True)
        table.add_column("Output", style="white")
        
        if result.returncode == 0:
            table.add_row("✅ All tests passed!", result.stdout)
        else:
            table.add_row("❌ Tests failed!", f"{result.stdout}\n{result.stderr}")
        
        console.print(table)

    except FileNotFoundError:
        console.print("[bold red]Error: `pytest` command not found. Please ensure pytest is installed and in your PATH.[/bold red]")
    except subprocess.TimeoutExpired:
        console.print("[bold red]Error: Tests timed out after 5 minutes.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")


def run_test(file_path: str):
    """Run a specific test file using pytest"""
    if not os.path.exists(file_path):
        console.print(f"[bold red]Test file not found: {file_path}[/bold red]")
        return

    console.print(f"[bold yellow]Running tests in: {file_path}[/bold yellow]")
    try:
        import subprocess
        result = subprocess.run(
            ["pytest", file_path],
            capture_output=True,
            text=True,
            timeout=120  # 2-minute timeout
        )
        if result.stdout:
            console.print(f"[white]{result.stdout}[/white]")
        if result.stderr:
            console.print(f"[bold red]{result.stderr}[/bold red]")
        
        if result.returncode == 0:
            console.print("[bold green]✅ All tests passed![/bold green]")
        else:
            console.print(f"[bold red]❌ Tests failed with exit code: {result.returncode}[/bold red]")

    except FileNotFoundError:
        console.print("[bold red]Error: `pytest` command not found. Please ensure pytest is installed and in your PATH.[/bold red]")
    except subprocess.TimeoutExpired:
        console.print("[bold red]Error: Tests timed out after 2 minutes.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")


def execute_shell_command_safe(command):
    """Execute shell commands with security checks"""
    if not command.strip():
        return False

    # Security checks for dangerous commands
    dangerous_patterns = [
        'rm -rf', 'rm -r', 'rmdir', 'del /s', 'format', 'fdisk',
        'mkfs', 'dd if=', '>/dev/', '>/etc/',
        'cat > /etc/', 'echo > /etc/', 'chmod 777 /',
        'mv /etc/', 'cp /etc/', 'touch /etc/',
        'shutdown', 'reboot', 'poweroff', 'halt'
    ]

    cmd_lower = command.lower()
    for pattern in dangerous_patterns:
        if pattern in cmd_lower:
            console.print(f"[bold red]❌ Blocked potentially dangerous command: {command}[/bold red]")
            return False

    try:
        # Execute the command and capture output
        console.print(f"[bold cyan]Executing: {command}[/bold cyan]")

        import subprocess
        # Additional security validation to prevent command injection
        # Check for potential command injection patterns
        injection_patterns = [
            '&&', '||', ';', '`', '$(', '|',
            # Check for command substitution patterns
            '>', '>>', '<',
            # Check for redirection that could be harmful
        ]

        cmd_lower = command.lower()
        for pattern in injection_patterns:
            if pattern in cmd_lower:
                console.print(f"[bold red]❌ Blocked potentially dangerous command (injection risk): {command}[/bold red]")
                return False

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30  # Set a timeout
        )

        if result.stdout:
            console.print(f"[white]{result.stdout}[/white]")
        if result.stderr:
            console.print(f"[bold red]{result.stderr}[/bold red]")

        console.print(f"[bold green]Command completed with exit code: {result.returncode}[/bold green]")
        return True
    except subprocess.TimeoutExpired:
        console.print("[bold red]Command timed out after 30 seconds[/bold red]")
        return False
    except Exception as e:
        console.print(f"[bold red]Error executing command: {str(e)}[/bold red]")
        return False

def self_document_task(agent, doc_type, *args):
    """Handle self-documenting tasks for updating documentation"""
    # Find the self-documenting provider
    doc_provider = None
    for provider in agent.providers:
        if hasattr(provider, 'server_name') and provider.server_name == 'self_documenting':
            doc_provider = provider
            break
    
    if not doc_provider:
        console.print("[bold red]Error: Self-documenting server not available.[/bold red]")
        return
    
    if doc_type == 'authors':
        console.print(f"[bold yellow]Updating AUTHORS file with: {args}[/bold yellow]")
        console.print("[bold]This would send the request to the self-documenting server...[/bold]")
        console.print("[dim]In a real implementation, the server would update the AUTHORS file.[/dim]")
    
    elif doc_type == 'changelog':
        console.print(f"[bold yellow]Updating CHANGELOG with: {args}[/bold yellow]")
        console.print("[bold]This would send the request to the self-documenting server...[/bold]")
        console.print("[dim]In a real implementation, the server would update the CHANGELOG file.[/dim]")
    
    elif doc_type == 'readme':
        console.print(f"[bold yellow]Updating README section: {args}[/bold yellow]")
        console.print("[bold]This would send the request to the self-documenting server...[/bold]")
        console.print("[dim]In a real implementation, the server would update the README file.[/dim]")
    
    else:
        console.print(f"[bold red]Unknown documentation type: {doc_type}[/bold red]")

def automation_task(agent, task_type, *args):
    """Handle automation tasks like scaffolding, env management, and renaming"""
    # Find the automation provider
    automation_provider = None
    for provider in agent.providers:
        if hasattr(provider, 'server_name') and provider.server_name == 'automation':
            automation_provider = provider
            break

    if not automation_provider:
        console.print("[bold red]Error: Automation server not available.[/bold red]")
        return

    if task_type == 'scaffold':
        if len(args) < 1:
            console.print("[bold red]Please specify a project name. Usage: /scaffold [project_name] ([template])[/bold red]")
            return
        project_name = args[0]
        template = args[1] if len(args) > 1 else 'basic'
        console.print(f"[bold yellow]Creating project scaffold: {project_name} (template: {template})[/bold yellow]")
        console.print("[bold]This would send the request to the automation server...[/bold]")
        console.print("[dim]In a real implementation, the server would create the project structure.[/dim]")

    elif task_type == 'env':
        console.print(f"[bold yellow]Managing environment variables: {args}[/bold yellow]")
        console.print("[bold]This would send the request to the automation server...[/bold]")
        console.print("[dim]In a real implementation, the server would manage .env files.[/dim]")

    elif task_type == 'rename':
        if len(args) < 2:
            console.print("[bold red]Please specify old and new names. Usage: /rename [old_name] [new_name] ([file_path])[/bold red]")
            return
        old_name = args[0]
        new_name = args[1]
        file_path = args[2] if len(args) > 2 else 'current file'
        console.print(f"[bold yellow]Renaming variable: {old_name} → {new_name} in {file_path}[/bold yellow]")
        console.print("[bold]This would send the request to the automation server...[/bold]")
        console.print("[dim]In a real implementation, the server would rename variables in the file.[/dim]")

    elif task_type == 'shell':
        if len(args) < 1:
            console.print("[bold red]Please specify a command to execute. Usage: /shell [command][/bold red]")
            return
        command = ' '.join(args)
        execute_shell_command_safe(command)

    else:
        console.print(f"[bold red]Unknown automation task: {task_type}[/bold red]")

def show_plugins(agent):
    """Display available plugins"""
    plugins = agent.plugin_manager.get_available_plugins()
    
    if not plugins:
        console.print("[yellow]No plugins available.[/yellow]")
        console.print("[dim]Create your own plugins by adding Python files to the plugins/ directory.[/dim]")
        return
    
    console.print("\n[bold blue]Available Plugins:[/bold blue]")
    for plugin_name, functions in plugins.items():
        console.print(f"  [cyan]{plugin_name}[/cyan]:")
        for func in functions:
            console.print(f"    - {func}")
    console.print("\n[bold]To create a plugin, add a Python file to the plugins/ directory.[/bold]\n")

def create_plugin(agent, name):
    """Create a new plugin skeleton"""
    try:
        plugin_path = agent.plugin_manager.create_plugin_skeleton(
            name=name,
            description=f"Custom plugin for {name}",
            author="User",
            version="1.0.50"
        )
        console.print(f"[bold green]Plugin '{name}' created successfully![/bold green]")
        console.print(f"Location: {plugin_path}")
        console.print("[dim]Edit this file to implement your plugin functionality.[/dim]")
    except Exception as e:
        console.print(f"[bold red]Error creating plugin: {e}[/bold red]")

def display_themes():
    """Display available themes and allow user to customize the interface"""
    console.print("\n[bold #9370DB]Visual Themes:[/bold #9370DB]")
    theme_choices = list(THEMES.keys())
    for theme in theme_choices:
        console.print(f"  [cyan]{theme}[/cyan]")

    selected_theme = Prompt.ask("\n[bold yellow]Select a theme[/bold yellow]", choices=theme_choices, default=current_theme_name).strip().lower()
    apply_theme(selected_theme)

def analyze_project_command():
    """Analyze the current project and provide insights"""
    console.print("[bold blue]🔍 Starting project analysis...[/bold blue]")

    try:
        # Show loading animation while analyzing
        import threading
        stop_event = threading.Event()
        loading_thread = threading.Thread(target=show_loading_animation, args=(stop_event,))
        loading_thread.start()

        # Perform the analysis
        report = analyze_current_project()

        # Stop the loading animation
        stop_event.set()
        loading_thread.join()
        print()  # Add a newline after the loading message is cleared

        # Display the analysis report
        from rich.markdown import Markdown
        md = Markdown(report)
        console.print(md)

        console.print("\n[bold green]✅ Project analysis complete![/bold green]")

    except Exception as e:
        # Stop the loading animation in case of error
        stop_event.set()
        if 'loading_thread' in locals():
            loading_thread.join()
        print()  # Add a newline after the loading message is cleared
        console.print(f"[bold red]❌ Error during project analysis: {str(e)}[/bold red]")

def generate_project_visualizations():
    """Generate all project visualizations"""
    console.print("[bold blue]🎨 Generating project visualizations...[/bold blue]")
    try:
        visualization_manager = VisualizationManager()
        results = []

        # Generate dependency graph
        result = visualization_manager.generate_dependency_graph()
        results.append(result)

        # Generate project structure
        result = visualization_manager.generate_project_structure()
        results.append(result)

        # Generate performance dashboard
        result = visualization_manager.generate_performance_dashboard()
        results.append(result)

        console.print("[bold green]✅ All visualizations generated successfully![/bold green]")
        for result in results:
            console.print(f"  - {result}")
    except Exception as e:
        console.print(f"[bold red]Error generating visualizations: {str(e)}[/bold red]")

def show_dependency_graph():
    """Show dependency graph visualization"""
    console.print("[bold blue]🔗 Generating dependency graph...[/bold blue]")
    try:
        visualization_manager = VisualizationManager()
        result = visualization_manager.generate_dependency_graph()
        console.print(f"[bold green]✅ {result}[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error generating dependency graph: {str(e)}[/bold red]")

def show_project_structure():
    """Show project structure visualization"""
    console.print("[bold blue]📁 Generating project structure visualization...[/bold blue]")
    try:
        visualization_manager = VisualizationManager()
        result = visualization_manager.generate_project_structure()
        console.print(f"[bold green]✅ {result}[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error generating project structure visualization: {str(e)}[/bold red]")

def show_performance_dashboard():
    """Show performance metrics dashboard"""
    console.print("[bold blue]📊 Generating performance dashboard...[/bold blue]")
    try:
        # In a real implementation, this would be generated from live data
        from codeius.core.performance import PERF_MONITOR_FILE, PerformanceMonitor
        import pickle
        if not PERF_MONITOR_FILE.exists():
            console.print("[bold yellow]No performance data available yet.[/bold yellow]")
            return

        with open(PERF_MONITOR_FILE, 'rb') as f:
            perf_monitor = pickle.load(f)

        table = Table(title="[bold green]Agent Performance Metrics[/bold green]", show_header=True, header_style="bold magenta")
        table.add_column("Operation", style="cyan", no_wrap=True)
        table.add_column("Count", style="green", justify="right")
        table.add_column("Total Time (s)", style="yellow", justify="right")
        table.add_column("Success", style="green", justify="right")
        table.add_column("Fail", style="red", justify="right")
        table.add_column("Avg. Time (s)", style="blue", justify="right")

        for op, metrics in sorted(perf_monitor.metrics.items()):
            try:
                table.add_row(
                    op,
                    str(metrics.get('count', 0)),
                    f"{metrics.get('total_duration', 0):.4f}",
                    str(metrics.get('success_count', 0)),
                    str(metrics.get('failure_count', 0)),
                    f"{metrics.get('avg_duration', 0):.4f}"
                )
            except KeyError:
                # Handle cases where a metric might be missing
                console.print(f"[bold red]Incomplete data for operation: {op}[/bold red]")
        
        console.print(table)
    except Exception as e:
        console.print(f"[bold red]Error generating performance dashboard: {str(e)}[/bold red]")

def show_analysis_summary():
    """Show analysis summary dashboard"""
    console.print("[bold blue]🔮 Generating analysis summary...[/bold blue]")
    try:
        visualization_manager = VisualizationManager()
        # For now, this is the same as performance dashboard
        result = visualization_manager.generate_performance_dashboard()
        console.print(f"[bold green]✅ {result}[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error generating analysis summary: {str(e)}[/bold red]")

def display_help():
    """Display help information with all available commands"""
    # Create a visually stunning header for the help
    help_header = Panel(
        "[bold #BA55D3]Welcome to Codeius AI Coding Agent Help Center[/bold #BA55D3]\n\n"
        "[white]Use these commands to interact with the agent:[/white]",
        title="[bold #9370DB]Command Guide[/bold #9370DB]",
        border_style="#9370DB",
        expand=False
    )
    console.print(help_header)

    # Create a visually appealing commands grid using Table
    commands_table = Table(
        title="[bold #40E0D0]Available Commands[/bold #40E0D0]",
        title_style="bold #40E0D0",
        box=HEAVY_HEAD,
        border_style="#40E0D0",
        expand=True
    )
    commands_table.add_column(" #", style="#7CFC00", justify="center", width=3)
    commands_table.add_column("Command", style="#7CFC00", width=20)
    commands_table.add_column("Description", style="white")

    commands_list = [
        ("/models", "List all available AI models"),
        ("/mcp", "List available MCP tools"),
        ("/dashboard", "Show real-time code quality dashboard"),
        ("/themes", "Show available visual themes"),
        ("/add_model", "Add a custom AI model with API key and endpoint"),
        ("/shell [command]", "Execute a direct shell command securely"),
        ("/toggle", "Toggle between Interaction and Shell modes"),
        ("/mode", "Alternative command for toggling modes"),
        ("/keys", "Show mode switching options"),
        ("/shortcuts", "Show mode switching options"),
        ("/ocr [image_path]", "Extract text from an image using OCR"),
        ("/refactor [file_path]", "Analyze and refactor code in a file"),
        ("/diff [file1] [file2]", "Compare two files or directories"),
        ("/scaffold [name] [template]", "Generate project scaffolding"),
        ("/env [action] [variables]", "Manage environment files"),
        ("/rename [old] [new] [file]", "Batch rename variables"),
        ("/plot [metric]", "Plot code metrics and data"),
        ("/update_docs [type] [args]", "Update documentation files"),
        ("/snippet [action] [args]", "Manage code snippets"),
        ("/scrape [file_or_dir_or_url] [css_selector]", "Scrape web content"),
        ("/config [action] [args]", "Manage configurations"),
        ("/schedule [task_type] [interval] [target]", "Schedule tasks to run automatically"),
        ("/inspect [package]", "Inspect package information"),
        ("/context", "Show current project context information"),
        ("/set_project [path] [name]", "Set the current project context"),
        ("/search [query]", "Semantic search across the codebase"),
        ("/find_function [name]", "Find a function by name"),
        ("/find_class [name]", "Find a class by name"),
        ("/file_context [file_path]", "Show context for a specific file"),
        ("/autodetect", "Auto-detect and set project context"),
        ("/security_scan", "Run comprehensive security scan"),
        ("/secrets_scan", "Scan for secrets and sensitive information"),
        ("/vuln_scan", "Scan for code vulnerabilities"),
        ("/policy_check", "Check for policy violations"),
        ("/security_policy", "Show current security policy settings"),
        ("/security_report", "Generate comprehensive security report"),
        ("/set_policy [key] [value]", "Update security policy setting"),
        ("/plugins", "List available plugins"),
        ("/create_plugin [name]", "Create a new plugin skeleton"),
        ("/switch [model_key]", "Switch to a specific model"),
        ("/gen_viz", "Generate all project visualizations"),
        ("/dep_graph", "Show dependency graph visualization"),
        ("/proj_struct", "Show project structure visualization"),
        ("/perf_dash", "Show performance metrics dashboard"),
        ("/performance", "Show performance metrics dashboard"),
        ("/viz_summary", "Show analysis summary dashboard"),
        ("/analyze", "Analyze the current project structure and content"),
        ("/run_test [file_path]", "Run a specific test file"),
        ("/test", "Run all tests"),
        ("/help", "Show this help message"),
        ("/clear", "Clear the conversation history"),
        ("/exit", "Exit the application")
    ]

    for idx, (command, desc) in enumerate(commands_list, 1):
        commands_table.add_row(str(idx), f"[bold #00FFFF]{command}[/bold #00FFFF]", desc)

    console.print("\n", commands_table)

    # MCP Tools section with enhanced visual
    mcp_header = Panel(
        "[bold #FFA500]MCP Tools - Enhanced Functionality[/bold #FFA500]",
        border_style="#FFA500",
        expand=False
    )
    console.print(mcp_header)

    # MCP Tools table with enhanced styling
    mcp_table = Table(
        title="[bold #9370DB]Integrated Tools[/bold #9370DB]",
        title_style="bold #9370DB",
        box=HEAVY_HEAD,
        border_style="#9370DB",
        expand=True
    )
    mcp_table.add_column("Tool", style="#7CFC00", no_wrap=True)
    mcp_table.add_column("Capabilities", style="white")

    mcp_tools_list = [
        ("code-runner", "Execute Python code in sandboxed environment"),
        ("filesystem", "Access and manage files in workspace"),
        ("duckduckgo", "Perform web searches"),
        ("code-search", "Search for functions, classes, and TODOs in code"),
        ("shell", "Execute safe shell commands"),
        ("testing", "Run automated tests"),
        ("doc-search", "Search documentation files"),
        ("database", "Query local SQLite databases"),
        ("ocr", "Extract text from images"),
        ("refactor", "Analyze and refactor code"),
        ("diff", "Compare files and directories"),
        ("automation", "Automate repetitive coding tasks"),
        ("visualization", "Create plots and visualizations"),
        ("self_documenting", "Auto-update documentation"),
        ("package_inspector", "Inspect packages and dependencies"),
        ("snippet_manager", "Manage code snippets and templates"),
        ("web_scraper", "Scrape web content from files/urls"),
        ("config_manager", "Manage configurations and credentials"),
        ("task_scheduler", "Schedule tasks to run automatically")
    ]

    for tool, cap in mcp_tools_list:
        mcp_table.add_row(f"[bold #FFA500]{tool}[/bold #FFA500]", cap)

    console.print("\n", mcp_table)

    # Add a visual separator and tips section
    console.print(Rule("[bold #8A2BE2]Tips & Tricks[/bold #8A2BE2]", style="#8A2BE2", align="center"))

    tips_table = Table(box=HEAVY_HEAD, border_style="#8A2BE2", expand=True)
    tips_table.add_column("Tip", style="#8A2BE2")
    tips_table.add_row("Use [bold #00FFFF]/models[/bold #00FFFF] to see available AI models")
    tips_table.add_row("Use [bold #00FFFF]/switch model_name[/bold #00FFFF] to change models mid-conversation")
    tips_table.add_row("Use [bold #00FFFF]/shell [command][/bold #00FFFF] to execute secure shell commands")
    tips_table.add_row("Use [bold #00FFFF]/toggle[/bold #00FFFF] to switch between Interaction and Shell modes")
    tips_table.add_row("Use [bold #00FFFF]/mode[/bold #00FFFF] as an alternative to /toggle command")
    tips_table.add_row("Use [bold #00FFFF]/context[/bold #00FFFF] to see project context information")
    tips_table.add_row("Use [bold #00FFFF]/search [query][/bold #00FFFF] for semantic code search")
    tips_table.add_row("Use [bold #00FFFF]/autodetect[/bold #00FFFF] to automatically set project context")
    tips_table.add_row("Use [bold #00FFFF]/security_scan[/bold #00FFFF] to run comprehensive security scan")
    tips_table.add_row("Use [bold #00FFFF]/secrets_scan[/bold #00FFFF] to detect sensitive information")
    tips_table.add_row("Type [bold #00FFFF]exit[/bold #00FFFF] to quit anytime")
    tips_table.add_row("Use [bold #00FFFF]/clear[/bold #00FFFF] to reset conversation history")

    console.print("\n", tips_table)
    console.print()  # Add spacing

def display_welcome_screen():
    """Display a cleaner welcome screen with project info and instructions"""

    # Import the responsive header implementation
    import sys
    import io
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich.align import Align
    import platform
    from datetime import datetime
    import shutil

    # BULLETPROOF UTF-8 ENCODING FIX FOR WINDOWS
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except AttributeError:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    console = Console(force_terminal=True, force_interactive=False)

    def can_use_unicode():
        """Check if terminal supports Unicode"""
        try:
            '█'.encode(sys.stdout.encoding or 'utf-8')
            return True
        except (UnicodeEncodeError, AttributeError):
            return False

    def get_terminal_width():
        """Get terminal width safely"""
        try:
            return shutil.get_terminal_size().columns
        except:
            return 100

    def create_ascii_letters():
        """ASCII-only fallback letters"""
        letters = {
            'C': [
                "######",
                "##    ",
                "##    ",
                "##    ",
                "##    ",
                "##    ",
                "######"
            ],
            'O': [
                "######",
                "##  ##",
                "##  ##",
                "##  ##",
                "##  ##",
                "##  ##",
                "######"
            ],
            'D': [
                "##### ",
                "##  ##",
                "##  ##",
                "##  ##",
                "##  ##",
                "##  ##",
                "##### "
            ],
            'E': [
                "######",
                "##    ",
                "##    ",
                "##### ",
                "##    ",
                "##    ",
                "######"
            ],
            'I': [
                "######",
                "  ##  ",
                "  ##  ",
                "  ##  ",
                "  ##  ",
                "  ##  ",
                "######"
            ],
            'U': [
                "##  ##",
                "##  ##",
                "##  ##",
                "##  ##",
                "##  ##",
                "##  ##",
                "######"
            ],
            'S': [
                "######",
                "##    ",
                "##    ",
                "######",
                "    ##",
                "    ##",
                "######"
            ]
        }
        return letters, '#', 6

    def create_unicode_letters():
        """Unicode block letters"""
        letters = {
            'C': [
                "██████",
                "██    ",
                "██    ",
                "██    ",
                "██    ",
                "██    ",
                "██████"
            ],
            'O': [
                "██████",
                "██  ██",
                "██  ██",
                "██  ██",
                "██  ██",
                "██  ██",
                "██████"
            ],
            'D': [
                "█████ ",
                "██  ██",
                "██  ██",
                "██  ██",
                "██  ██",
                "██  ██",
                "█████ "
            ],
            'E': [
                "██████",
                "██    ",
                "██    ",
                "█████ ",
                "██    ",
                "██    ",
                "██████"
            ],
            'I': [
                "██████",
                "  ██  ",
                "  ██  ",
                "  ██  ",
                "  ██  ",
                "  ██  ",
                "██████"
            ],
            'U': [
                "██  ██",
                "██  ██",
                "██  ██",
                "██  ██",
                "██  ██",
                "██  ██",
                "██████"
            ],
            'S': [
                "██████",
                "██    ",
                "██    ",
                "██████",
                "    ██",
                "    ██",
                "██████"
            ]
        }
        return letters, '█', 6

    def create_compact_letters():
        """Compact letters for smaller terminals"""
        letters = {
            'C': [
                "████",
                "██  ",
                "██  ",
                "██  ",
                "████"
            ],
            'O': [
                "████",
                "█  █",
                "█  █",
                "█  █",
                "████"
            ],
            'D': [
                "███ ",
                "█  █",
                "█  █",
                "█  █",
                "███ "
            ],
            'E': [
                "████",
                "██  ",
                "███ ",
                "██  ",
                "████"
            ],
            'I': [
                "████",
                " ██ ",
                " ██ ",
                " ██ ",
                "████"
            ],
            'U': [
                "█  █",
                "█  █",
                "█  █",
                "█  █",
                "████"
            ],
            'S': [
                "████",
                "██  ",
                "████",
                "  ██",
                "████"
            ]
        }
        return letters, '█', 4

    def create_tiny_letters():
        """Tiny letters for very small terminals"""
        letters = {
            'C': ["██", "█ ", "██"],
            'O': ["██", "█ █", "██"],
            'D': ["██", "█ █", "██"],
            'E': ["██", "██", "██"],
            'I': ["██", "██", "██"],
            'U': ["█ █", "█ █", "██"],
            'S': ["██", "██", "██"]
        }
        return letters, '█', 2

    def calculate_optimal_spacing(term_width, letter_width, num_letters):
        """Calculate spacing to maximize width usage"""
        # Account for panel borders and padding (roughly 20 chars)
        usable_width = term_width - 20

        # Total letter width
        total_letter_width = letter_width * num_letters

        # Calculate available space for gaps
        available_space = usable_width - total_letter_width

        # Number of gaps between letters
        num_gaps = num_letters - 1

        if available_space <= 0 or num_gaps <= 0:
            return 1  # Minimum spacing

        # Calculate spacing per gap
        spacing = max(1, available_space // num_gaps)

        # Cap maximum spacing to avoid too much spread
        return min(spacing, 8)

    def create_logo_letters(term_width):
        """Create CODEIUS letters with responsive sizing"""
        use_unicode = can_use_unicode()

        # Determine size based on terminal width
        if term_width >= 110:
            # Large: normal size
            if use_unicode:
                letters, block, letter_width = create_unicode_letters()
            else:
                letters, block, letter_width = create_ascii_letters()
        elif term_width >= 80:
            # Medium: compact size
            if use_unicode:
                letters, block, letter_width = create_compact_letters()
            else:
                letters = create_compact_letters()[0]
                block = '#'
                letter_width = 4
        elif term_width >= 50:
            # Small: tiny size
            if use_unicode:
                letters, block, letter_width = create_tiny_letters()
            else:
                letters = create_tiny_letters()[0]
                block = '#'
                letter_width = 2
        else:
            # Extra small: text only
            return None, None, None, None, 0

        word = "CODEIUS"
        num_letters = len(word)

        # Calculate optimal spacing
        spacing_size = calculate_optimal_spacing(term_width, letter_width, num_letters)
        spacing = " " * spacing_size

        # Combine letters horizontally
        num_rows = len(letters['C'])
        combined_lines = []

        for row in range(num_rows):
            line = ""
            for i, char in enumerate(word):
                line += letters[char][row]
                if i < len(word) - 1:
                    line += spacing
            combined_lines.append(line)

        return combined_lines, block, use_unicode, num_rows, letter_width

    def apply_gradient(text_lines, block_char):
        """Apply gradient coloring"""
        gradient_colors = [
            "#9D00FF", "#B100FF", "#C400FF", "#E100FF",
            "#FF00EA", "#FF00C8", "#FF0099", "#FF0066",
            "#00F0FF", "#00D4FF", "#00B8FF", "#0099FF",
        ]

        combined_text = "\n".join(text_lines)
        gradient_text = Text()

        char_count = 0
        total_chars = sum(1 for char in combined_text if char in (block_char, '█', '#'))

        for char in combined_text:
            if char in (block_char, '█', '#'):
                color_index = int((char_count / max(total_chars, 1)) * (len(gradient_colors) - 1))
                gradient_text.append(char, style=f"bold {gradient_colors[color_index]}")
                char_count += 1
            else:
                gradient_text.append(char)

        return gradient_text

    def safe_print_unicode(text, fallback_text=None):
        """Safely print Unicode with fallback"""
        try:
            console.print(text)
        except UnicodeEncodeError:
            if fallback_text:
                console.print(fallback_text)
            else:
                console.print(str(text).encode('ascii', 'replace').decode('ascii'))

    def display_header():
        """Display fully responsive header"""

        console.clear()
        term_width = get_terminal_width()

        # Create letters with responsive sizing
        letter_lines, block_char, use_unicode, num_rows, letter_width = create_logo_letters(term_width)

        try:
            if letter_lines is None:
                # Terminal too small - text only
                console.print()
                title = Text("CODEIUS", style="bold bright_magenta")
                safe_print_unicode(Align.center(title))
                console.print()
            else:
                # Apply gradient
                gradient_art = apply_gradient(letter_lines, block_char)

                # Build panel with art
                panel_content = Text()
                panel_content.append("\n")
                panel_content.append(gradient_art)
                panel_content.append("\n")

                # Adjust padding based on terminal size
                padding = (1, 4) if term_width >= 100 else (0, 2)

                main_panel = Panel(
                    Align.center(panel_content),
                    border_style="bold bright_magenta",
                    padding=padding,
                )

                safe_print_unicode(main_panel)
        except Exception as e:
            # Ultimate fallback
            console.print("\n[bold bright_magenta]CODEIUS[/bold bright_magenta]\n")

        # Subtitle
        try:
            subtitle = Text("✦ ", style="bold #FF00FF")
            subtitle.append("AI-POWERED CODING AGENT", style="bold italic bright_yellow")
            subtitle.append(" ✦", style="bold #00F0FF")
            safe_print_unicode(Align.center(subtitle))
        except:
            console.print("[bold bright_yellow]AI-POWERED CODING AGENT[/bold bright_yellow]")

        # Tagline
        try:
            if term_width >= 80:
                tagline = Text("⚡ ", style="bold bright_cyan")
                tagline.append("CODE SMARTER • BUILD FASTER • SHIP BETTER", style="bold bright_white")
                tagline.append(" ⚡", style="bold bright_cyan")
            else:
                tagline = Text("CODE SMARTER • BUILD FASTER", style="bold bright_white")
            safe_print_unicode(Align.center(tagline))
        except:
            console.print("[bright_white]CODE SMARTER - BUILD FASTER[/bright_white]")

        console.print()

        # System info
        try:
            system_info = Table.grid(padding=(0, 2))
            system_info.add_column(style="bold #FF00FF", justify="right")
            system_info.add_column(style="bold bright_white")

            system_info.add_row("⚙ SYSTEM", platform.system())
            system_info.add_row("🐍 PYTHON", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
            system_info.add_row("🕐 TIME", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            system_info.add_row("⚡ STATUS", Text("ONLINE", style="bold bright_green"))

            info_panel = Panel(
                system_info,
                title="[bold #00F0FF]SYSTEM STATUS[/bold #00F0FF]",
                border_style="bright_cyan",
                padding=(0, 1),
            )
            safe_print_unicode(Align.center(info_panel))
        except Exception as e:
            console.print(f"[bright_cyan]System: {platform.system()} | Python: {sys.version_info.major}.{sys.version_info.minor}[/bright_cyan]")

        console.print()

        # Ready indicator
        try:
            ready_text = Text("● ", style="bold bright_green")
            ready_text.append("READY TO CODE", style="bold bright_green")
            ready_text.append(" ●", style="bold bright_green")
            safe_print_unicode(Align.center(ready_text))
        except:
            console.print("[bold bright_green]READY TO CODE[/bold bright_green]")

        console.print()

    # Display the responsive header
    display_header()

    # Check if API keys are set and show warning if not
    import os
    groq_key = os.getenv("GROQ_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")

    if not groq_key and not google_key:
        api_warning = Panel(
            "[bold #FF4500]API KEY SETUP REQUIRED[/bold #FF4500]\n\n"
            "[white]Please set your API keys in environment variables:[/white]\n"
            "[#7CFC00]GROQ_API_KEY[/#7CFC00] and [#7CFC00]GOOGLE_API_KEY[/#7CFC00]\n\n"
            "[white]Get keys from:[/white]\n"
            "[#00FFFF]• Groq: https://console.groq.com/keys[/#00FFFF]\n"
            "[#00FFFF]• Google: https://aistudio.google.com/app/apikey[/#00FFFF]\n\n"
            "[bold #BA55D3]Run: export GROQ_API_KEY=your_key (Linux/MacOS)[/bold #BA55D3]\n"
            "[bold #BA55D3]Run: set GROQ_API_KEY=your_key (Windows)[/bold #BA55D3]",
            title="[bold #FF4500]API Setup Required[/bold #FF4500]",
            border_style="#FF4500",
            expand=False
        )
        console.print(api_warning)
        console.print()  # Extra spacing

    # Create a cleaner welcome panel
    welcome_panel = Panel(
        "[bold #7CFC00]AI-powered coding assistant with multiple tools and visual interface[/bold #7CFC00]\n\n"
        "[white]• Read/Write files • Git operations • Web search • Multi-LLM support[/white]\n"
        "[white]• MCP servers for extended tools • Real-time dashboards[/white]\n\n"
        "[#BA55D3]Commands:[/ #BA55D3] [bold #00FFFF]/help[/bold #00FFFF] for commands, [bold #00FFFF]/models[/bold #00FFFF] for LLMs, [bold #00FFFF]/mcp[/bold #00FFFF] for tools",
        title="[bold #9370DB on #00008B]Welcome to Codeius AI Coding Agent[/bold #9370DB on #00008B]",
        border_style="#9370DB",
        padding=(1, 1),
        expand=False
    )
    console.print(welcome_panel)

    # Create a cleaner status panel
    status_panel = Panel(
        "[bold #00FFFF]Status:[/bold #00FFFF] [green]All systems operational[/green]  [bold #00FFFF]Version:[/bold #00FFFF] [magenta]1.0.50[/magenta]  [bold #00FFFF]Uptime:[/bold #00FFFF] [cyan]Ready for use[/cyan]\n\n"
        "[bold #7CFC00]How to use:[/bold #7CFC00] Type coding instructions, confirm file operations, [bold]exit[/bold] to quit, or use [bold #00FFFF]/commands[/bold #00FFFF]",
        title="[bold #40E0D0]System Status[/bold #40E0D0]",
        border_style="#40E0D0",
        expand=False,
        padding=(1, 1)
    )
    console.print(status_panel)
    console.print()  # Add spacing

def show_loading_animation(stop_event):
    """Show a loading animation while waiting for agent response"""
    symbols = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']  # Spinning animation
    i = 0
    while not stop_event.is_set():
        # Use sys.stdout for direct output without Rich formatting to avoid conflicts
        sys.stdout.write(f'\r{symbols[i % len(symbols)]} Processing your request...')
        sys.stdout.flush()
        i += 1
        time.sleep(0.1)
    sys.stdout.write('\r')  # Clear the loading message
    sys.stdout.flush()


def show_dynamic_loading_animation(stop_event):
    """Show a dynamic loading animation with text that changes every 10 seconds"""
    import random

    # Different phrases to display during processing
    phrases = [
        "Thinking...",
        "Processing your query...",
        "Analyzing your code...",
        "Consulting documentation...",
        "Generating response...",
        "Searching for answers...",
        "Compiling thoughts...",
        "Fetching information...",
        "Running analysis...",
        "Calculating best response...",
        "Evaluating possibilities...",
        "Building solution...",
        "Refining output...",
        "Cross-referencing sources..."
    ]

    current_phrase = random.choice(phrases)
    symbols = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']  # Spinning animation
    i = 0
    start_time = time.time()

    while not stop_event.is_set():
        # Change the phrase every 10 seconds
        if time.time() - start_time >= 10:
            start_time = time.time()
            current_phrase = random.choice(phrases)

        # Use sys.stdout for direct output without Rich formatting to avoid conflicts
        sys.stdout.write(f'\r{symbols[i % len(symbols)]} {current_phrase}')
        sys.stdout.flush()
        i += 1
        time.sleep(0.1)

    sys.stdout.write('\r')  # Clear the loading message
    sys.stdout.flush()

def show_processing_progress(description="Processing"):
    """Show a progress bar for longer operations"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:
        task = progress.add_task(f"[#00FFFF]{description}...", total=100)
        while not progress.finished:
            progress.update(task, advance=1)
            time.sleep(0.05)
            if progress._tasks[task].completed >= 100:
                break
        progress.update(task, completed=100, description=f"[#32CD32]{description} completed!")
        time.sleep(0.5)  # Brief pause to show completion

def format_agent_response(response_text):
    """Format agent response with rich styling for better readability"""
    # Add visual styling to different parts of the response
    import re

    # Format action steps with special markers
    response_text = re.sub(r'(\*\*Agent Plan:\*\*|Agent Plan:)', r'[bold #9370DB]\1[/bold #9370DB]', response_text)

    # Format file operations
    response_text = re.sub(r'(`[^`]+`)', r'[bold #FFD700]\1[/bold #FFD700]', response_text)

    # Format success indicators
    response_text = re.sub(r'(\[GOOD\])', r'[bold #32CD32]\1[/bold #32CD32]', response_text)

    # Format error indicators
    response_text = re.sub(r'(\[BAD\])', r'[bold #FF4500]\1[/bold #FF4500]', response_text)

    # Format warning indicators
    response_text = re.sub(r'(\[WARN\])', r'[bold #FFA500]\1[/bold #FFA500]', response_text)

    # Format web search indicators
    response_text = re.sub(r'(🌐)', r'[bold #00FFFF]\1[/bold #00FFFF]', response_text)

    # Format agent explanations
    response_text = re.sub(r'(-\s[^\.!\n]*\.|- [^\n]*)', r'[#BA55D3]\1[/#BA55D3]', response_text)

    return response_text

def display_conversation_history(agent):
    """Display a summary of the conversation history"""
    # Access history through the conversation manager since it's been refactored
    try:
        # Try to access the history via conversation manager first
        if hasattr(agent, 'conversation_manager') and agent.conversation_manager:
            history = agent.conversation_manager.history
        else:
            # Fallback to direct agent.history if conversation manager is not available
            history = getattr(agent, 'history', [])
    except AttributeError:
        # If there's any issue accessing the history, default to empty list
        history = []

    if not history:
        console.print(Panel("[italic dim]No conversation history yet.[/italic dim]", border_style="dim", expand=False))
        return

    # Create a visually appealing conversation history table
    history_table = Table(
        title="[bold #9370DB]Conversation History[/bold #9370DB]",
        title_style="bold #9370DB",
        box=HEAVY_HEAD,
        border_style="#9370DB",
        expand=True
    )
    history_table.add_column("#", style="#7CFC00", justify="right", width=3)
    history_table.add_column("Role", style="#7CFC00", width=10)
    history_table.add_column("Content Preview", style="white")

    for i, entry in enumerate(history):
        role = entry["role"]
        content = entry["content"]
        content_preview = content[:80]  # Shortened preview
        content_preview = content_preview.strip()
        content_preview = f"{content_preview}{'...' if len(content) > 80 else ''}"

        if role == "user":
            history_table.add_row(
                str(i+1),
                "[bold #7CFC00]You[/bold #7CFC00]",
                f"[#7CFC00]{content_preview}[/#7CFC00]"
            )
        elif role == "assistant":
            history_table.add_row(
                str(i+1),
                "[bold #BA55D3]Agent[/bold #BA55D3]",
                f"[#BA55D3]{content_preview}[/#BA55D3]"
            )

    console.print("\n", history_table)
    console.print(Panel(f"[white]Total messages: {len(history)}[/white]", border_style="#40E0D0", expand=False))
    console.print()  # Add spacing

def display_models(agent):
    """Display available AI models to the user (excluding MCP tools)"""
    models = agent.get_available_models()
    current_model = agent.get_current_model_info()

    if not models:
        console.print(Panel("[yellow]No AI models available.[/yellow]", border_style="yellow", expand=False))
        return

    # Create a visually appealing table for models
    models_table = Table(
        title="[bold #9370DB]Available AI Models[/bold #9370DB]",
        title_style="bold #9370DB",
        box=HEAVY_HEAD,
        border_style="#9370DB",
        expand=True
    )
    models_table.add_column("Model Key", style="#7CFC00", no_wrap=True)
    models_table.add_column("Name", style="white")
    models_table.add_column("Provider", style="cyan")
    models_table.add_column("Status", style="#32CD32")

    for key, model_info in models.items():
        if current_model and key == current_model['key']:
            # Highlight the currently active model
            models_table.add_row(
                f"[bold green]→ {key}[/bold green]",
                model_info['name'],
                model_info['provider'],
                "[bold green]ACTIVE[/bold green]"
            )
        else:
            models_table.add_row(key, model_info['name'], model_info['provider'], "Available")

    console.print("\n", models_table)
    console.print(Panel("[bold]To switch models, use: /switch [model_key][/bold]", border_style="#40E0D0", expand=False))
    console.print()

def display_mcp_tools(agent):
    """Display available MCP tools to the user"""
    # Get all MCP tools from the agent
    mcp_tools = agent.get_available_mcp_tools()
    
    if not mcp_tools:
        console.print("[yellow]No MCP tools available.[/yellow]")
        console.print("[dim]MCP tools provide access to various utilities without requiring API keys.[/dim]")
        return
    
    console.print("\n[bold blue]Available MCP Tools:[/bold blue]")
    for key, tool_info in mcp_tools.items():
        console.print(f"  [cyan]{key}[/cyan]: {tool_info['name']} [MCP Tool]")
    console.print("\n[bold]MCP tools provide specialized functionality like code search, shell execution, etc.[/bold]\n")

class CustomCompleter(Completer):
    def __init__(self, agent):
        self.agent = agent

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if text.startswith('/'):
            # Split the text to see if we're in a command or sub-command
            parts = text.split(' ', 1)
            command = parts[0].lower()
            
            if command == '/switch' or command.startswith('/switch'):
                # Show all models when user types /switch (with or without space)
                # The key is to check if we're after the /switch command
                if len(parts) > 1:
                    # User has started typing a model name after /switch, suggest matching models
                    typed_model = parts[1].lower()
                    models = self.agent.get_available_models()
                    current_model = self.agent.get_current_model_info()
                    for key, info in models.items():
                        if typed_model in key.lower() or typed_model in info['name'].lower():
                            # Highlight current model differently if possible
                            suffix = " [Current]" if (current_model and key == current_model['key']) else ""
                            yield Completion(key, start_position=-len(typed_model), 
                                           display=f"{key} [{info['name']}]",
                                           display_meta=f"{info['provider']}{suffix}")
                else:
                    # Show all models when user types /switch without any additional text
                    models = self.agent.get_available_models()
                    current_model = self.agent.get_current_model_info()
                    for key, info in models.items():
                        # Highlight current model in the suggestions
                        suffix = " [Current]" if (current_model and key == current_model['key']) else ""
                        yield Completion(key, 
                                       display=f"{key} [{info['name']}]",
                                       display_meta=f"{info['provider']}{suffix}")
            elif command in ['/help', '/clear', '/mcp', '/models', '/dashboard', '/add_model', '/ocr', '/refactor', '/diff', '/plugins', '/create_plugin', '/scaffold', '/env', '/rename', '/plot', '/update_docs', '/inspect', '/snippet', '/scrape', '/config', '/schedule', '/analyze', '/exit']:
                # Don't provide additional completions if these commands are fully typed
                pass
            else:
                # Provide command suggestions for commands that don't require parameters
                commands = [
                    '/models', '/mcp', '/dashboard', '/themes', '/add_model', '/shell',
                    '/toggle', '/mode', '/keys', '/shortcuts', '/context', '/ctx',
                    '/set_project', '/search', '/find_function', '/find_class',
                    '/file_context', '/autodetect', '/detect', '/security_scan',
                    '/scan', '/secrets_scan', '/vuln_scan', '/policy_check',
                    '/security_policy', '/policy', '/security_report', '/set_policy',
                    '/ocr', '/refactor', '/diff', '/plugins', '/create_plugin',
                    '/scaffold', '/env', '/rename', '/plot', '/update_docs',
                    '/inspect', '/snippet', '/scrape', '/config', '/schedule',
                    '/analyze', '/switch', '/help', '/clear', '/exit'
                ]
                for cmd in commands:
                    if cmd.startswith(text.lower()):
                        yield Completion(cmd, start_position=-len(text))
        elif '@' in text:
            # Handle path completion when '@' is present
            at_pos = text.rfind('@')
            path_prefix = text[at_pos+1:]
            
            # Base directory for completion is the current working directory
            base_dir = os.getcwd()
            
            # The part of the path to complete
            path_to_complete = os.path.join(base_dir, path_prefix)
            
            # Directory of the path to complete
            dirname = os.path.dirname(path_to_complete)
            
            # The prefix to match against in the directory
            prefix = os.path.basename(path_to_complete)

            try:
                if os.path.isdir(dirname):
                    for filename in os.listdir(dirname):
                        if filename.lower().startswith(prefix.lower()):
                            full_path = os.path.join(dirname, filename)
                            # The completion text should be relative to the input after '@'
                            completion_text = os.path.join(os.path.dirname(path_prefix), filename)
                            if os.path.isdir(full_path):
                                yield Completion(completion_text + '/', start_position=-len(prefix), display_meta='directory')
                            else:
                                yield Completion(completion_text, start_position=-len(prefix), display_meta='file')
            except OSError:
                # Ignore errors like permission denied
                pass

# Global variable to track Ctrl+C presses
    # Global variable to track Ctrl+C presses
first_ctrl_c_time = None

# Keybindings for agent mode
kb_agent = KeyBindings()

@kb_agent.add("enter", eager=True)
def _(event):
    if event.current_buffer.text and event.current_buffer.text.strip():
        event.app.exit(result=event.current_buffer.text)
    else:
        event.app.exit(result="")

def init_command():
    """Command to initialize the agent with API keys and configuration files."""
    console.print("[bold green]Welcome to the Codeius AI Coding Agent setup![/bold green]")
    console.print("Let's set up your API keys and configuration files.")

    # Create .codeius directory
    codeius_dir = Path('.codeius')
    codeius_dir.mkdir(exist_ok=True)

    console.print(f"[bold green]Created .codeius directory at: {codeius_dir.absolute()}[/bold green]")

    # Check for existing .env before overwriting
    env_exists = os.path.exists('.env')
    if env_exists:
        overwrite_env = Prompt.ask(
            "[bold yellow]A .env file already exists. Do you want to overwrite it?[/bold yellow]",
            choices=["y", "n"],
            default="n"
        )
        if overwrite_env.lower() != 'y':
            console.print("[bold yellow].env file kept unchanged.[/bold yellow]")
        else:
            api_choice = Prompt.ask(
                "Which API do you want to set up?",
                choices=["Google", "Groq", "Custom"],
                default="Google"
            )

            env_vars = {}
            if api_choice == "Google":
                api_key = Prompt.ask("Enter your Google API Key")
                env_vars["GOOGLE_API_KEY"] = api_key
            elif api_choice == "Groq":
                api_key = Prompt.ask("Enter your Groq API Key")
                env_vars["GROQ_API_KEY"] = api_key
            elif api_choice == "Custom":
                name = Prompt.ask("Enter a name for your custom model")
                api_key = Prompt.ask("Enter the API Key for your custom model")
                model = Prompt.ask("Enter the model name")
                base_url = Prompt.ask("Enter the base URL for the API")
                env_vars[f"CUSTOM_MODEL_{name.upper()}_API_KEY"] = api_key
                env_vars[f"CUSTOM_MODEL_{name.upper()}_MODEL"] = model
                env_vars[f"CUSTOM_MODEL_{name.upper()}_BASE_URL"] = base_url

            with open('.env', 'w') as f:
                for key, value in env_vars.items():
                    f.write(f"{key}={value}\n")

            console.print("[bold green]Successfully created .env file![/bold green]")
    else:
        api_choice = Prompt.ask(
            "Which API do you want to set up?",
            choices=["Google", "Groq", "Custom"],
            default="Google"
        )

        env_vars = {}
        if api_choice == "Google":
            api_key = Prompt.ask("Enter your Google API Key")
            env_vars["GOOGLE_API_KEY"] = api_key
        elif api_choice == "Groq":
            api_key = Prompt.ask("Enter your Groq API Key")
            env_vars["GROQ_API_KEY"] = api_key
        elif api_choice == "Custom":
            name = Prompt.ask("Enter a name for your custom model")
            api_key = Prompt.ask("Enter the API Key for your custom model")
            model = Prompt.ask("Enter the model name")
            base_url = Prompt.ask("Enter the base URL for the API")
            env_vars[f"CUSTOM_MODEL_{name.upper()}_API_KEY"] = api_key
            env_vars[f"CUSTOM_MODEL_{name.upper()}_MODEL"] = model
            env_vars[f"CUSTOM_MODEL_{name.upper()}_BASE_URL"] = base_url

        with open('.env', 'w') as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")

        console.print("[bold green]Successfully created .env file![/bold green]")

    # Create default configuration files in .codeius directory
    create_default_config_files(codeius_dir)

    console.print("[bold green]✅ Codeius has been initialized successfully![/bold green]")
    console.print("[bold]You can now run 'codeius' to start the agent.[/bold]")


def create_default_config_files(codeius_dir: Path):
    """Create default configuration files in the .codeius directory."""

    # Create settings.json with default settings
    settings_file = codeius_dir / "settings.json"
    if not settings_file.exists():
        default_settings = {
            "max_tokens": 2048,
            "conversation_history_limit": 50,
            "max_file_size_mb": 10,
            "max_concurrent_operations": 5,
            "rate_limit_requests": 100,
            "rate_limit_window_seconds": 60,
            "mcp_server_timeout": 30,
            "mcp_server_retry_attempts": 3,
            "workspace_root": ".",
            "groq_api_model": "llama3-70b-8192",
            "google_api_model": "gemini-1.5-flash",
            "enable_security_scanning": True,
            "security_scan_on_file_write": False,
            "default_theme": "default"
        }
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(default_settings, f, indent=2)
        console.print(f"[bold green]Created settings.json[/bold green]")

    # Create default Agent.md file with instructions
    agent_file = codeius_dir / "Agent.md"
    if not agent_file.exists():
        default_agent_instructions = """# Codeius AI Agent Instructions

You are an advanced AI coding assistant named Codeius. You help users with programming tasks by reading and writing files, performing git operations, running tests, searching code, executing shell commands, and conducting web searches.

## Capabilities

- Read and write source files in the workspace
- Perform git operations (stage, commit)
- Perform web searches using DuckDuckGo
- Start and interact with background processes
- Analyze code for quality, security, and style issues
- Refactor code when requested
- Generate documentation
- Create project scaffolding
- Manage environment variables
- Execute shell commands securely
- Run tests with pytest

## Response Format

When you need to perform actions, respond with JSON in this format:

```json
{
  "explanation": "Describe your plan",
  "actions": [
    {"type": "read_file", "path": "..."},
    {"type": "write_file", "path": "...", "content": "..."},
    {"type": "append_to_file", "path": "...", "content": "..."},
    {"type": "delete_file", "path": "..."},
    {"type": "list_files", "pattern": "..."},
    {"type": "create_directory", "path": "..."},
    {"type": "git_commit", "message": "..."},
    {"type": "web_search", "query": "..."},
    {"type": "analyze_code", "path": "..."},
    {"type": "start_process", "command": "..."},
    {"type": "send_input", "pid": 123, "data": "..."},
    {"type": "read_output", "pid": 123},
    {"type": "read_error", "pid": 123},
    {"type": "stop_process", "pid": 123}
  ]
}
```

If only a conversation or non-code answer is needed, reply conversationally.
"""
        with open(agent_file, 'w', encoding='utf-8') as f:
            f.write(default_agent_instructions)
        console.print(f"[bold green]Created Agent.md[/bold green]")

    # Create default security policy
    security_policy_file = codeius_dir / "security_policy.yml"
    if not security_policy_file.exists():
        default_security_policy = """# Default Security Policy for Codeius AI Coding Agent

secrets_detection_enabled: true
vulnerability_scanning_enabled: true
policy_enforcement_enabled: true
minimum_severity_to_report: medium  # low, medium, high

# Allowed packages (whitelist)
allowed_packages: []

# Blocked packages (blacklist)
blocked_packages: []

# Forbidden functions that could be dangerous
forbidden_functions:
  - eval
  - exec
  - compile
  - open
  - input

# Required security headers for web applications
required_headers:
  - Content-Security-Policy
  - X-Frame-Options
  - X-XSS-Protection
  - X-Content-Type-Options

# File access restrictions
file_access:
  allowed_extensions:
    - .py
    - .js
    - .ts
    - .tsx
    - .json
    - .md
    - .txt
    - .yaml
    - .yml
    - .html
    - .css
    - .xml
  blocked_paths:
    - /etc/
    - /root/
    - /proc/
    - /sys/
"""
        with open(security_policy_file, 'w', encoding='utf-8') as f:
            f.write(default_security_policy)
        console.print(f"[bold green]Created security_policy.yml[/bold green]")

    # Create default project template if needed
    templates_dir = codeius_dir / "templates"
    templates_dir.mkdir(exist_ok=True)
    console.print(f"[bold green]Created templates directory[/bold green]")

    # Create a basic README for the .codeius directory
    readme_file = codeius_dir / "README.md"
    if not readme_file.exists():
        readme_content = """# .codeius Directory

This directory contains configuration files for the Codeius AI Coding Agent.

## Files

- `settings.json` - Agent settings and configuration
- `Agent.md` - Instructions for the AI agent
- `security_policy.yml` - Security policy configuration
- `templates/` - Project templates for scaffolding

## Purpose

This directory provides project-specific configuration for Codeius, allowing you to customize the agent's behavior, security policies, and capabilities for this specific project.
"""
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        console.print(f"[bold green]Created README.md[/bold green]")


def ensure_global_config():
    """Ensure global config directory and files exist in user's home directory."""
    global_dir = Path.home() / ".codeius"
    global_dir.mkdir(exist_ok=True)

    # Create global settings if they don't exist
    global_settings_file = global_dir / "settings.json"
    if not global_settings_file.exists():
        default_global_settings = {
            "max_tokens": 2048,
            "conversation_history_limit": 50,
            "max_file_size_mb": 10,
            "max_concurrent_operations": 5,
            "rate_limit_requests": 100,
            "rate_limit_window_seconds": 60,
            "mcp_server_timeout": 30,
            "mcp_server_retry_attempts": 3,
            "workspace_root": ".",
            "groq_api_model": "llama3-70b-8192",
            "google_api_model": "gemini-1.5-flash",
            "enable_security_scanning": True,
            "security_scan_on_file_write": False,
            "default_theme": "default",
            "first_run": True  # Track if this is the first run
        }
        with open(global_settings_file, 'w', encoding='utf-8') as f:
            json.dump(default_global_settings, f, indent=2)

        # Create global Agent.md
        global_agent_file = global_dir / "Agent.md"
        if not global_agent_file.exists():
            default_agent_instructions = """# Global Codeius AI Agent Instructions

You are an advanced AI coding assistant named Codeius. You help users with programming tasks by reading and writing files, performing git operations, running tests, searching code, executing shell commands, and conducting web searches.

## Capabilities

- Read and write source files in the workspace
- Perform git operations (stage, commit)
- Perform web searches using DuckDuckGo
- Start and interact with background processes
- Analyze code for quality, security, and style issues
- Refactor code when requested
- Generate documentation
- Create project scaffolding
- Manage environment variables
- Execute shell commands securely
- Run tests with pytest

## Response Format

When you need to perform actions, respond with JSON in this format:

```json
{
  "explanation": "Describe your plan",
  "actions": [
    {"type": "read_file", "path": "..."},
    {"type": "write_file", "path": "...", "content": "..."},
    {"type": "append_to_file", "path": "...", "content": "..."},
    {"type": "delete_file", "path": "..."},
    {"type": "list_files", "pattern": "..."},
    {"type": "create_directory", "path": "..."},
    {"type": "git_commit", "message": "..."},
    {"type": "web_search", "query": "..."},
    {"type": "analyze_code", "path": "..."},
    {"type": "start_process", "command": "..."},
    {"type": "send_input", "pid": 123, "data": "..."},
    {"type": "read_output", "pid": 123},
    {"type": "read_error", "pid": 123},
    {"type": "stop_process", "pid": 123}
  ]
}
```

If only a conversation or non-code answer is needed, reply conversationally.
"""
            with open(global_agent_file, 'w', encoding='utf-8') as f:
                f.write(default_agent_instructions)

        # Create global security policy
        global_security_policy_file = global_dir / "security_policy.yml"
        if not global_security_policy_file.exists():
            default_security_policy = """# Global Security Policy for Codeius AI Coding Agent

secrets_detection_enabled: true
vulnerability_scanning_enabled: true
policy_enforcement_enabled: true
minimum_severity_to_report: medium  # low, medium, high

# Allowed packages (whitelist)
allowed_packages: []

# Blocked packages (blacklist)
blocked_packages: []

# Forbidden functions that could be dangerous
forbidden_functions:
  - eval
  - exec
  - compile
  - open
  - input

# Required security headers for web applications
required_headers:
  - Content-Security-Policy
  - X-Frame-Options
  - X-XSS-Protection
  - X-Content-Type-Options

# File access restrictions
file_access:
  allowed_extensions:
    - .py
    - .js
    - .ts
    - .tsx
    - .json
    - .md
    - .txt
    - .yaml
    - .yml
    - .html
    - .css
    - .xml
  blocked_paths:
    - /etc/
    - /root/
    - /proc/
    - /sys/
"""
            with open(global_security_policy_file, 'w', encoding='utf-8') as f:
                f.write(default_security_policy)

        # Create global README
        global_readme_file = global_dir / "README.md"
        if not global_readme_file.exists():
            global_readme_content = """# Global .codeius Directory

This directory contains global configuration files for the Codeius AI Coding Agent.

## Files

- `settings.json` - Global agent settings and configuration
- `Agent.md` - Global instructions for the AI agent
- `security_policy.yml` - Global security policy configuration

## Purpose

This directory provides global configuration for Codeius that applies across all projects, unless overridden by project-specific configurations.
"""
            with open(global_readme_file, 'w', encoding='utf-8') as f:
                f.write(global_readme_content)

        console.print(f"[bold green]Created global configuration at: {global_dir}[/bold green]")


def main():
    # Ensure global config exists on any run of the agent
    ensure_global_config()

    if '--init' in sys.argv:
        init_command()
        sys.exit(0)

    if len(sys.argv) > 1 and sys.argv[1] == 'web':
        from codeius.api.server import run_gui
        run_gui()
        sys.exit(0)

    global first_ctrl_c_time  # Use the global variable to track Ctrl+C presses
    display_welcome_screen()
    apply_theme(current_theme_name) # Apply the default theme at startup

    agent = CodingAgent()
    # Plugins already loaded during agent initialization, no need to load again

    # Track the current mode (interaction or shell) - using a mutable container to allow updates
    mode_container = {'interaction': True}

    # Create a custom completer that handles both commands and model suggestions
    completer = CustomCompleter(agent)

    while True:
        try:
            # Create a prompt session with enhanced styling and custom completion based on current mode
            def get_current_style():
                global current_theme_name
                if mode_container['interaction']:
                    return THEMES[current_theme_name]["interaction_style"]
                else:
                    return THEMES[current_theme_name]["shell_style"]

            def get_current_prompt_text():
                global current_theme_name
                if mode_container['interaction']:
                    return THEMES[current_theme_name]["interaction_prompt_text"]
                else:
                    return THEMES[current_theme_name]["shell_prompt_text"]

            # Create session with updated style
            session = PromptSession(
                completer=completer,
                style=get_current_style(),
                complete_while_typing=True,
            )

            # Get input based on mode
            if mode_container['interaction']:
                # Use the beautiful input box with placeholder where user types inside for interaction mode
                try:
                    term_width = shutil.get_terminal_size().columns
                except:
                    term_width = 100

                # Calculate box size - leave room for borders, account for prompt icon
                inner_width = min(term_width - 6, 80)  # Reduce max width to accommodate the prompt icon

                # Use boxed_input_with_placeholder function for the bordered input
                try:
                    # Use the new boxed_input_with_placeholder function with custom placeholder
                    input_layout, agent_textarea, agent_input_style = boxed_input_with_placeholder(
                        placeholder="Ask Gemini, or type /help",
                        width=inner_width,
                        height=3,
                        prompt_text="⭐ "
                    )

                    # Create a prompt session specifically for the agent input
                    agent_session = PromptSession(
                        message=HTML(""),  # Message is handled by the textarea's prompt
                        completer=completer,
                        style=agent_input_style,
                        complete_while_typing=True,
                        key_bindings=kb_agent, # Use specific keybindings for agent mode
                        bottom_toolbar=None, # No bottom toolbar by default
                        accept_default=True
                    )

                    # Run the application with the custom layout
                    prompt = agent_session.prompt(
                        get_current_prompt_text(),
                        default=agent_textarea.text, # Pre-fill with existing text
                        multiline=True, # Enable multiline input
                        wrap_lines=True, # Wrap lines in input
                        complete_style=CompleteStyle.MULTI_COLUMN, # Enable multi-column completion
                        style=agent_input_style,
                        input_processors=[
                            BeforeInput(filter=~is_multiline() & ~has_suggestion)
                        ],
                    ).strip()
                except:
                    # Fallback if boxed_input_with_placeholder fails
                    prompt = session.prompt(
                        get_current_prompt_text(),
                        default='',
                        complete_style=CompleteStyle.MULTI_COLUMN,
                        style=get_current_style()
                    ).strip()
            else:
                # For shell mode, keep the old prompt
                prompt = session.prompt(
                    get_current_prompt_text(),
                    default='',
                    complete_style=CompleteStyle.MULTI_COLUMN,
                    style=get_current_style()
                ).strip()

            if not prompt: continue

            # Handle special commands
            if prompt.startswith('/'):
                if prompt.lower() == '/models':
                    display_models(agent)
                    continue
                elif prompt.lower() == '/mcp':
                    display_mcp_tools(agent)
                    continue
                elif prompt.lower() == '/dashboard':
                    display_dashboard()
                    continue
                elif prompt.lower() == '/themes':
                    display_themes()
                    continue
                elif prompt.lower() == '/keys' or prompt.lower() == '/shortcuts':
                    display_help()
                    continue
                    # Extract image path from the command
                    parts = prompt.split(' ', 1)
                    if len(parts) > 1:
                        image_path = parts[1].strip()
                        ocr_image(agent, image_path)
                    else:
                        console.print("[bold red]Please specify an image path. Usage: /ocr [image_path][/bold red]")
                    continue
                elif prompt.lower().startswith('/refactor '):
                    # Extract file path from the command
                    parts = prompt.split(' ', 1)
                    if len(parts) > 1:
                        file_path = parts[1].strip()
                        refactor_code(agent, file_path)
                    else:
                        console.print("[bold red]Please specify a file path. Usage: /refactor [file_path][/bold red]")
                    continue
                elif prompt.lower().startswith('/diff '):
                    # Extract file paths from the command
                    parts = prompt.split(' ', 2)  # Split into at most 3 parts: '/diff', 'file1', 'file2'
                    if len(parts) == 3:
                        file1, file2 = parts[1].strip(), parts[2].strip()
                        diff_files(agent, file1, file2)
                    else:
                        console.print("[bold red]Please specify two file paths. Usage: /diff [file1] [file2][/bold red]")
                    continue
                elif prompt.lower() == '/plugins':
                    show_plugins(agent)
                    continue
                elif prompt.lower().startswith('/create_plugin '):
                    parts = prompt.split(' ', 1)
                    if len(parts) > 1:
                        plugin_name = parts[1].strip()
                        create_plugin(agent, plugin_name)
                    else:
                        console.print("[bold red]Please specify a plugin name. Usage: /create_plugin [name][/bold red]")
                    continue
                elif prompt.lower().startswith('/scaffold '):
                    parts = prompt.split(' ')
                    args = [part.strip() for part in parts[1:] if part.strip()]
                    automation_task(agent, 'scaffold', *args)
                    continue
                elif prompt.lower() == '/shell':
                    console.print("[bold red]Please specify a command to execute. Usage: /shell [command][/bold red]")
                    continue
                elif prompt.lower().startswith('/shell '):
                    parts = prompt.split(' ', 1)  # Split into at most 2 parts: '/shell' and 'command'
                    if len(parts) > 1:
                        command = parts[1].strip()
                        execute_shell_command_safe(command)
                    else:
                        console.print("[bold red]Please specify a command to execute. Usage: /shell [command][/bold red]")
                    continue
                elif prompt.lower().startswith('/env '):
                    parts = prompt.split(' ')
                    args = [part.strip() for part in parts[1:] if part.strip()]
                    automation_task(agent, 'env', *args)
                    continue
                elif prompt.lower().startswith('/rename '):
                    parts = prompt.split(' ')
                    args = [part.strip() for part in parts[1:] if part.strip()]
                    automation_task(agent, 'rename', *args)
                    continue
                elif prompt.lower().startswith('/plot '):
                    parts = prompt.split(' ', 1)
                    if len(parts) > 1:
                        metric_type = parts[1].strip()
                        visualization_task(agent, metric_type)
                    else:
                        console.print("[bold red]Please specify a metric type. Usage: /plot [metric_type][/bold red]")
                    continue
                elif prompt.lower().startswith('/update_docs '):
                    parts = prompt.split(' ', 2)
                    if len(parts) > 1:
                        doc_type = parts[1].strip()
                        doc_args = parts[2].split(' ') if len(parts) > 2 else []
                        self_document_task(agent, doc_type, *doc_args)
                    else:
                        console.print("[bold red]Please specify a documentation type. Usage: /update_docs [type] [args][/bold red]")
                    continue
                elif prompt.lower().startswith('/inspect '):
                    parts = prompt.split(' ', 1)
                    if len(parts) > 1:
                        package_name = parts[1].strip()
                        package_inspect_task(agent, package_name)
                    else:
                        console.print("[bold red]Please specify a package name. Usage: /inspect [package_name][/bold red]")
                    continue
                elif prompt.lower().startswith('/snippet '):
                    parts = prompt.split(' ', 2)
                    if len(parts) > 1:
                        action = parts[1].strip()
                        snippet_args = parts[2].split(' ') if len(parts) > 2 else []
                        snippet_task(agent, action, *snippet_args)
                    else:
                        console.print("[bold red]Please specify an action. Usage: /snippet [action] [args][/bold red]")
                        console.print("[bold]Available actions: get, add, list, insert[/bold]")
                    continue
                elif prompt.lower().startswith('/scrape '):
                    parts = prompt.split(' ', 1)
                    if len(parts) > 1:
                        url = parts[1].strip()
                        web_scrape_task(agent, url)
                    else:
                        console.print("[bold red]Please specify a URL. Usage: /scrape [url][/bold red]")
                    continue
                elif prompt.lower().startswith('/config '):
                    parts = prompt.split(' ', 2)
                    if len(parts) > 1:
                        action = parts[1].strip()
                        config_args = parts[2].split(' ') if len(parts) > 2 else []
                        config_task(agent, action, *config_args)
                    else:
                        console.print("[bold red]Please specify an action. Usage: /config [action] [args][/bold red]")
                        console.print("[bold]Available actions: get, set, list, edit[/bold]")
                    continue
                elif prompt.lower().startswith('/schedule '):
                    parts = prompt.split(' ', 2)
                    if len(parts) > 1:
                        action = parts[1].strip()
                        schedule_args = parts[2].split(' ') if len(parts) > 2 else []
                        schedule_task(agent, action, *schedule_args)
                    else:
                        console.print("[bold red]Please specify an action. Usage: /schedule [action] [args][/bold red]")
                        console.print("[bold]Available actions: add, list, remove, run[/bold]")
                    continue
                elif prompt.lower().startswith('/analyze '):
                    analyze_project_command()
                    continue
                elif prompt.lower() in ['/switch', '/switch '] and len(prompt.split()) == 1:
                    # If just /switch without arguments, ask for model interactively
                    available_models = agent.get_available_models()
                    if available_models:
                        console.print("\n[bold]Available Models:[/bold]")
                        for key, model_info in available_models.items():
                            console.print(f"  [cyan]{key}[/cyan] - {model_info.get('name', 'Unknown')}")
                        model_key = Prompt.ask("\n[bold yellow]Enter model key to switch to[/bold yellow]").strip()
                        if model_key:
                            result = agent.switch_model(model_key)
                            console.print(f"[bold green]{result}[/bold green]")
                        else:
                            console.print("[bold red]No model key provided[/bold red]")
                    else:
                        console.print("[bold red]No models available to switch to[/bold red]")
                    continue
                elif prompt.lower().startswith('/switch '):
                    # Extract model key from the command
                    parts = prompt.split(' ', 1)
                    if len(parts) > 1:
                        model_key = parts[1].strip()
                        result = agent.switch_model(model_key)
                        console.print(f"[bold green]{result}[/bold green]")
                    else:
                        console.print("[bold red]Please specify a model key. Usage: /switch [model_key][/bold red]")
                    continue
                elif prompt.lower() == '/help':
                    display_help()
                    continue
                elif prompt.lower() == '/clear':
                    agent.reset_history()
                    console.print("[bold green]Conversation history cleared[/bold green]")
                    continue
                elif prompt.lower() == '/exit':
                    # Allow user to exit using /exit command
                    # Display conversation history before exiting
                    history_check = getattr(agent, 'history', [])
                    if hasattr(agent, 'conversation_manager') and hasattr(agent.conversation_manager, 'history'):
                        history_check = agent.conversation_manager.history

                    if len(history_check) > 0 and len([h for h in history_check if h["role"] == "user"]) % 3 == 0:
                        show_history = Prompt.ask("\n[bold yellow]Show conversation history?[/bold yellow] [Y/n]", default="Y").strip().lower()
                        if show_history in ("y", "yes", ""):
                            display_conversation_history(agent)

                    # Create a visually appealing goodbye message
                    goodbye_table = Table(
                        title="[bold #FFD700]Thank You![/bold #FFD700]",
                        box=HEAVY_HEAD,
                        border_style="#7CFC00",
                        expand=True,
                        title_style="bold #FFD700 on #00008B"
                    )
                    goodbye_table.add_column("Message", style="#7CFC00", justify="center")
                    goodbye_table.add_row("[bold #7CFC00]Thank you for using Codeius AI Coding Agent![/bold #7CFC00]")
                    goodbye_table.add_row("[#00FFFF]We hope you enjoyed the experience[/#00FFFF]")
                    goodbye_table.add_row("[bold #BA55D3]Come back soon![/bold #BA55D3]")
                    console.print("\n", goodbye_table)
                    time.sleep(1)  # Brief pause to enjoy the goodbye message
                    break
                elif prompt.lower() == '/toggle' or prompt.lower() == '/mode':
                    # Toggle between interaction and shell modes
                    mode_container['interaction'] = not mode_container['interaction']
                    if mode_container['interaction']:
                        console.print("[bold green]Mode: Interaction Mode - AI Agent Ready[/bold green]")
                    else:
                        console.print("[bold yellow]Mode: Shell Mode - Direct Command Execution[/bold yellow]")
                    continue
                elif prompt.lower() == '/add_model':
                    # Interactive model setup
                    console.print("\n[bold #40E0D0]Add Custom Model Setup[/bold #40E0D0]")
                    model_name = Prompt.ask("[bold yellow]Enter a name for the model[/bold yellow]").strip()
                    if not model_name:
                        console.print("[bold red]Model name is required[/bold red]")
                        continue

                    api_key = Prompt.ask("[bold yellow]Enter API key[/bold yellow]", password=True).strip()
                    if not api_key:
                        console.print("[bold red]API key is required[/bold red]")
                        continue

                    base_url = Prompt.ask("[bold yellow]Enter base URL (e.g., https://api.openai.com/v1)[/bold yellow]").strip()
                    if not base_url:
                        console.print("[bold red]Base URL is required[/bold red]")
                        continue

                    model_id = Prompt.ask("[bold yellow]Enter model ID (e.g., gpt-4, claude-3-opus)[/bold yellow]").strip()
                    if not model_id:
                        console.print("[bold red]Model ID is required[/bold red]")
                        continue

                    # Add the custom model
                    success = agent.add_custom_model(model_name, api_key, base_url, model_id)
                    if success:
                        console.print(f"[bold green]Successfully added {model_name}![/bold green]")
                        console.print(f"[bold]Use /switch {model_name} to use this model[/bold]")
                    else:
                        console.print(f"[bold red]Failed to add {model_name}[/bold red]")
                    continue
            elif prompt.lower() in ['exit', 'quit', 'q']:
                # If user types just "exit", "quit", or "q", also show history before exiting
                # Display conversation history before exiting
                history_check = getattr(agent, 'history', [])
                if hasattr(agent, 'conversation_manager') and hasattr(agent.conversation_manager, 'history'):
                    history_check = agent.conversation_manager.history

                if len(history_check) > 0 and len([h for h in history_check if h["role"] == "user"]) % 3 == 0:
                    show_history = Prompt.ask("\n[bold yellow]Show conversation history?[/bold yellow] [Y/n]", default="Y").strip().lower()
                    if show_history in ("y", "yes", ""):
                        display_conversation_history(agent)

                # Create a visually appealing goodbye message
                goodbye_table = Table(
                    title="[bold #FFD700]Thank You![/bold #FFD700]",
                    box=HEAVY_HEAD,
                    border_style="#7CFC00",
                    expand=True,
                    title_style="bold #FFD700 on #00008B"
                )
                goodbye_table.add_column("Message", style="#7CFC00", justify="center")
                goodbye_table.add_row("[bold #7CFC00]Thank you for using Codeius AI Coding Agent![/bold #7CFC00]")
                goodbye_table.add_row("[#00FFFF]We hope you enjoyed the experience[/#00FFFF]")
                goodbye_table.add_row("[bold #BA55D3]Come back soon![/bold #BA55D3]")
                console.print("\n", goodbye_table)
                time.sleep(1)  # Brief pause to enjoy the goodbye message
                break

            # Handle shell mode: if in shell mode and not a special command, execute prompt as shell command
            if not mode_container['interaction'] and not prompt.startswith('/'):
                execute_shell_command_safe(prompt)
                continue

            # Process the prompt with the agent, showing dynamic loading animation
            import threading
            stop_event = threading.Event()
            loading_thread = threading.Thread(target=show_dynamic_loading_animation, args=(stop_event,))
            loading_thread.start()

            try:
                result = agent.ask(prompt)
            finally:
                # Stop the loading animation
                stop_event.set()
                loading_thread.join()
                sys.stdout.write('\n')  # Add a newline after the loading animation stops
                sys.stdout.flush()

            console.print(Panel(result, title="[bold #BA55D3]Codeius Agent Response[/bold #BA55D3]", border_style="#BA55D3", expand=False))
        except KeyboardInterrupt:
            import time
            current_time = time.time()

            # Check if the first Ctrl+C happened less than 2 seconds ago
            if first_ctrl_c_time is not None and (current_time - first_ctrl_c_time) < 2.0:
                # Second Ctrl+C detected - exit now
                console.print("\n[bold #FF4500]Double Ctrl+C detected – exiting immediately...[/bold #FF4500]")
                # Display conversation history before exiting
                console.print(Panel("[bold #FFD700]Conversation Summary[/bold #FFD700]", expand=False, border_style="#FFD700"))
                display_conversation_history(agent)

                # Create a visually appealing goodbye message
                goodbye_table = Table(
                    title="[bold #FFD700]Thank You![/bold #FFD700]",
                    box=HEAVY_HEAD,
                    border_style="#7CFC00",
                    expand=True,
                    title_style="bold #FFD700 on #00008B"
                )
                goodbye_table.add_column("Message", style="#7CFC00", justify="center")
                goodbye_table.add_row("[bold #7CFC00]Thank you for using Codeius AI Coding Agent![/bold #7CFC00]")
                goodbye_table.add_row("[#00FFFF]We hope you enjoyed the experience[/#00FFFF]")
                goodbye_table.add_row("[bold #BA55D3]Come back soon![/bold #BA55D3]")
                console.print("\n", goodbye_table)
                time.sleep(1)  # Brief pause to enjoy the goodbye message
                break
            else:
                # First Ctrl+C - set the timer and warn the user
                first_ctrl_c_time = current_time
                console.print("\n[bold yellow]Ctrl+C detected – press again within 2 seconds to exit[/bold yellow]")
                # Continue the loop without breaking
                continue
        except Exception as e:
            console.print(f"[bold red][BAD] Error: {e}[/bold red]")

if __name__ == "__main__":
    from codeius.api.server import run_gui
    run_gui()