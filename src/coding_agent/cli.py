# src/cli.py

import sys
import os
import time
from threading import Thread
from typing import Generator
from coding_agent.agent import CodingAgent
from coding_agent.dashboard import Dashboard
from coding_agent.context_manager import ContextManager
from coding_agent.context_cli import (
    display_context_summary,
    semantic_search_command,
    show_file_context,
    set_project_command,
    find_element_command,
    auto_detect_project_command
)
from coding_agent.security_cli import (
    run_security_scan,
    show_security_policy,
    update_security_policy,
    create_security_report,
    run_secrets_detection,
    run_vulnerability_scan,
    run_policy_check
)
from coding_agent.visualization_manager import VisualizationManager
from coding_agent.project_analyzer import analyze_current_project
from dotenv import load_dotenv
from rich.console import Console
from rich.text import Text
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table
from rich.box import HEAVY_HEAD
from rich import print as rprint
from rich.rule import Rule
from rich.progress import Progress, SpinnerColumn, TextColumn
import pyfiglet
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.shortcuts import CompleteStyle
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.patch_stdout import patch_stdout
load_dotenv()

console = Console()

def confirm_safe_execution(result):
    console.print("The agent wants to perform these actions:", style="bold yellow")
    console.print(result)
    try:
        ask = Prompt.ask("Proceed?", choices=["y", "N"], default="N").strip().lower()
        return ask == "y"
    except:
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

def add_custom_model(agent):
    """Handle adding a custom model with user input"""
    console.print("[bold #00FFFF]Adding Custom Model[/bold #00FFFF]")
    console.print("[white]Please provide the following information for your custom model:[/white]")

    try:
        # Get model name
        model_name = Prompt.ask("[bold #7CFC00]Model Name[/bold #7CFC00] (for identification)").strip()
        if not model_name:
            console.print("[bold red]Model name is required. Operation cancelled.[/bold red]")
            return

        # Get API key
        api_key = Prompt.ask("[bold #7CFC00]API Key[/bold #7CFC00]", password=True).strip()
        if not api_key:
            console.print("[bold red]API key is required. Operation cancelled.[/bold red]")
            return

        # Get base URL
        base_url = Prompt.ask("[bold #7CFC00]Base URL[/bold #7CFC00] (e.g., https://api.openai.com/v1)").strip()
        if not base_url:
            console.print("[bold red]Base URL is required. Operation cancelled.[/bold red]")
            return

        # Get model identifier
        model_id = Prompt.ask("[bold #7CFC00]Model ID[/bold #7CFC00] (e.g., gpt-4, claude-3, etc.)").strip()
        if not model_id:
            console.print("[bold red]Model ID is required. Operation cancelled.[/bold red]")
            return

        # Add the custom model
        success = agent.add_custom_model(model_name, api_key, base_url, model_id)

        if success:
            console.print(f"[bold #32CD32][GOOD] Custom model '{model_name}' has been added successfully![/bold #32CD32]")
            console.print(f"[bold]You can now use this model with: /switch {model_name.lower().replace(' ', '_')}_X[/bold]")
            console.print(f"[dim]Where X is the provider number shown in /models[/dim]")
        else:
            console.print("[bold red][BAD] Failed to add custom model. Please check the provided information.[/bold red]")

    except KeyboardInterrupt:
        console.print("\n[bold yellow]Operation cancelled by user.[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]Error adding custom model: {str(e)}[/bold red]")

def package_inspect_task(agent, package_name):
    """Handle package inspection tasks"""
    # Find the package inspector provider
    inspector_provider = None
    for provider in agent.providers:
        if hasattr(provider, 'server_name') and provider.server_name == 'package_inspector':
            inspector_provider = provider
            break

    if not inspector_provider:
        console.print("[bold red]Error: Package inspector server not available.[/bold red]")
        return

    console.print(f"[bold yellow]Inspecting package: {package_name}[/bold yellow]")
    console.print("[bold]This would send the request to the package inspector server...[/bold]")
    console.print("[dim]In a real implementation, the server would return detailed package information including dependencies, licenses, and vulnerabilities.[/dim]")


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
            version="1.0.2"
        )
        console.print(f"[bold green]Plugin '{name}' created successfully![/bold green]")
        console.print(f"Location: {plugin_path}")
        console.print("[dim]Edit this file to implement your plugin functionality.[/dim]")
    except Exception as e:
        console.print(f"[bold red]Error creating plugin: {e}[/bold red]")

def display_themes():
    """Display available themes and allow user to customize the interface"""
    console.print("\n[bold #9370DB]Visual Themes:[/bold #9370DB]")
    console.print("  [cyan]default[/cyan] - Standard theme with blue and magenta accents")
    console.print("  [cyan]dark[/cyan] - Dark theme optimized for low-light environments")
    console.print("  [cyan]solarized[/cyan] - Solarized color scheme for eye comfort")
    console.print("  [cyan]terminal[/cyan] - Classic terminal look with green accents\n")
    console.print("[bold]To change theme, modify the colors in the CLI code directly.[/bold]\n")

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
        visualization_manager = VisualizationManager()
        result = visualization_manager.generate_performance_dashboard()
        console.print(f"[bold green]✅ {result}[/bold green]")
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
        ("/viz_summary", "Show analysis summary dashboard"),
        ("/analyze", "Analyze the current project structure and content"),
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
    # Display beautiful ASCII art for CODEIUS with improved font
    ascii_art = pyfiglet.figlet_format("CODEIUS", font="slant")
    console.print(f"[bold #8A2BE2]{ascii_art}[/bold #8A2BE2]")  # Deep purple color

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
        "[bold #00FFFF]Status:[/bold #00FFFF] [green]All systems operational[/green]  [bold #00FFFF]Version:[/bold #00FFFF] [magenta]1.0.2[/magenta]  [bold #00FFFF]Uptime:[/bold #00FFFF] [cyan]Ready for use[/cyan]\n\n"
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
                commands = ['/models', '/mcp', '/dashboard', '/add_model', '/shell', '/toggle', '/mode', '/keys', '/shortcuts', '/context', '/ctx', '/set_project', '/search', '/find_function', '/find_class', '/file_context', '/autodetect', '/detect', '/security_scan', '/scan', '/secrets_scan', '/vuln_scan', '/policy_check', '/security_policy', '/policy', '/security_report', '/set_policy', '/ocr', '/refactor', '/diff', '/plugins', '/create_plugin', '/scaffold', '/env', '/rename', '/plot', '/update_docs', '/inspect', '/snippet', '/scrape', '/config', '/schedule', '/analyze', '/switch', '/help', '/clear', '/exit']
                for cmd in commands:
                    if cmd.startswith(text.lower()):
                        yield Completion(cmd, start_position=-len(text))

def main():
    display_welcome_screen()

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
                if mode_container['interaction']:
                    # Standard interaction mode style
                    return Style.from_dict({
                        'prompt': 'bold #00FFFF',
                        'completion-menu': 'bg:#262626 #ffffff',
                        'completion-menu.completion.current': 'bg:#4a4a4a #ffffff',
                        'completion-menu.meta.completion': 'bg:#262626 #ffffff',
                        'completion-menu.meta.completion.current': 'bg:#4a4a4a #ffffff',
                    })
                else:
                    # Shell mode style - different colors
                    return Style.from_dict({
                        'prompt': 'bold #FF4500',  # Orange color for shell mode
                        'completion-menu': 'bg:#4a4a4a #ffffff',
                        'completion-menu.completion.current': 'bg:#262626 #ffffff',
                        'completion-menu.meta.completion': 'bg:#4a4a4a #ffffff',
                        'completion-menu.meta.completion.current': 'bg:#262626 #ffffff',
                    })

            def get_current_prompt_text():
                if mode_container['interaction']:
                    return HTML('<style fg="#00FFFF" bg="black"><b>⌨️ Enter your query:</b> </style> ')
                else:
                    return HTML('<style fg="#FF4500" bg="black"><b>🐚 Shell Mode:</b> </style> ')

            # Create session with updated style
            session = PromptSession(
                completer=completer,
                style=get_current_style(),
                complete_while_typing=True,
            )

            # Styled prompt with enhanced visual indicator and auto-completion
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
                elif prompt.lower().startswith('/ocr '):
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
                    parts = prompt.split(' ', 2)
                    if len(parts) > 1:
                        target = parts[1].strip()
                        selector = parts[2].strip() if len(parts) > 2 else '*'
                        scrape_task(agent, target, selector)
                    else:
                        console.print("[bold red]Please specify a target and selector. Usage: /scrape [file_or_dir_or_url] [css_selector][/bold red]")
                        continue
                elif prompt.lower().startswith('/config '):
                    parts = prompt.split(' ', 2)
                    if len(parts) > 1:
                        action = parts[1].strip()
                        config_args = parts[2].split(' ') if len(parts) > 2 else []
                        config_task(agent, action, *config_args)
                    else:
                        console.print("[bold red]Please specify an action. Usage: /config [action] [args][/bold red]")
                        console.print("[bold]Available actions: view, edit, list[/bold]")
                        continue
                elif prompt.lower().startswith('/schedule '):
                    parts = prompt.split(' ', 3)
                    if len(parts) > 2:
                        task_type = parts[1].strip()
                        interval = parts[2].strip()
                        target = parts[3].strip() if len(parts) > 3 else None
                        schedule_task(agent, task_type, interval, target)
                    else:
                        console.print("[bold red]Please specify task type and interval. Usage: /schedule [task_type] [interval] [target][/bold red]")
                        console.print("[bold]Examples: /schedule 'test' 'every 30 mins'; /schedule 'script' 'daily at 09:00' 'my_script.py'[/bold]")
                        continue
                elif prompt.lower() == '/add_model' or prompt.lower() == '/addmodel':
                    add_custom_model(agent)
                    continue
                elif prompt.lower() == '/toggle' or prompt.lower() == '/mode':
                    # Toggle between interaction and shell modes
                    mode_container['interaction'] = not mode_container['interaction']
                    if mode_container['interaction']:
                        console.print("[bold green]Mode: Interaction Mode - AI Agent Ready[/bold green]")
                    else:
                        console.print("[bold yellow]Mode: Shell Mode - Direct Command Execution[/bold yellow]")
                    continue
                elif prompt.lower() == '/context' or prompt.lower() == '/ctx':
                    display_context_summary(agent.context_manager)
                    continue
                elif prompt.lower() == '/set_project' or prompt.lower().startswith('/set_project '):
                    parts = prompt.split(' ', 2)  # Split into at most 3 parts: command, path, optional name
                    if len(parts) >= 2:
                        project_path = parts[1].strip()
                        project_name = parts[2].strip() if len(parts) > 2 else None
                        set_project_command(agent.context_manager, project_path, project_name)
                    else:
                        console.print("[bold red]Please specify a project path. Usage: /set_project [path] [optional_name][/bold red]")
                    continue
                elif prompt.lower().startswith('/search '):
                    parts = prompt.split(' ', 1)
                    if len(parts) > 1:
                        query = parts[1].strip()
                        semantic_search_command(agent.context_manager, query)
                    else:
                        console.print("[bold red]Please specify a search query. Usage: /search [query][/bold red]")
                    continue
                elif prompt.lower().startswith('/find_function '):
                    parts = prompt.split(' ', 1)
                    if len(parts) > 1:
                        func_name = parts[1].strip()
                        find_element_command(agent.context_manager, 'function', func_name)
                    else:
                        console.print("[bold red]Please specify a function name. Usage: /find_function [function_name][/bold red]")
                    continue
                elif prompt.lower().startswith('/find_class '):
                    parts = prompt.split(' ', 1)
                    if len(parts) > 1:
                        class_name = parts[1].strip()
                        find_element_command(agent.context_manager, 'class', class_name)
                    else:
                        console.print("[bold red]Please specify a class name. Usage: /find_class [class_name][/bold red]")
                    continue
                elif prompt.lower() == '/autodetect' or prompt.lower() == '/detect':
                    auto_detect_project_command(agent.context_manager)
                    continue
                elif prompt.lower().startswith('/file_context '):
                    parts = prompt.split(' ', 1)
                    if len(parts) > 1:
                        file_path = parts[1].strip()
                        show_file_context(agent.context_manager, file_path)
                    else:
                        console.print("[bold red]Please specify a file path. Usage: /file_context [file_path][/bold red]")
                    continue
                elif prompt.lower() == '/security_scan' or prompt.lower() == '/scan':
                    run_security_scan()
                    continue
                elif prompt.lower() == '/secrets_scan':
                    run_secrets_detection()
                    continue
                elif prompt.lower() == '/vuln_scan':
                    run_vulnerability_scan()
                    continue
                elif prompt.lower() == '/policy_check':
                    run_policy_check()
                    continue
                elif prompt.lower() == '/security_policy' or prompt.lower() == '/policy':
                    show_security_policy()
                    continue
                elif prompt.lower() == '/security_report':
                    create_security_report()
                    continue
                elif prompt.lower().startswith('/set_policy '):
                    parts = prompt.split(' ', 2)  # Split into command, key, value
                    if len(parts) == 3:
                        _, key, value = parts
                        update_security_policy(key.strip(), value.strip())
                    else:
                        console.print("[bold red]Usage: /set_policy [setting_key] [value][/bold red]")
                    continue
                elif prompt.lower() == '/gen_viz' or prompt.lower() == '/visualize':
                    generate_project_visualizations()
                    continue
                elif prompt.lower() == '/dep_graph':
                    show_dependency_graph()
                    continue
                elif prompt.lower() == '/proj_struct':
                    show_project_structure()
                    continue
                elif prompt.lower() == '/perf_dash':
                    show_performance_dashboard()
                    continue
                elif prompt.lower() == '/viz_summary':
                    show_analysis_summary()
                    continue
                elif prompt.lower() == '/analyze':
                    analyze_project_command()
                    continue
                elif prompt.lower().startswith('/switch '):
                    parts = prompt.split(' ', 1)
                    if len(parts) > 1:
                        model_key = parts[1].strip()
                        result = agent.switch_model(model_key)
                        console.print(Panel(result, title="[bold green]Model Switch[/bold green]", expand=False))
                        continue
                    else:
                        console.print("[bold red]Please specify a model. Use /models to see available models.[/bold red]")
                        continue
                elif prompt.lower() == '/help':
                    display_help()
                    continue
                elif prompt.lower() == '/clear':
                    agent.reset_history()
                    console.print("[bold #32CD32][GOOD] Conversation history cleared.[/bold #32CD32]")
                    continue
                elif prompt.lower() == '/cls' or prompt.lower() == '/clear_screen':
                    # Clear the entire screen with a visual effect
                    console.clear()
                    display_welcome_screen()
                    continue
                elif prompt.lower() == '/keys' or prompt.lower() == '/shortcuts':
                    console.print("\n[bold #9370DB]Mode Switching Options:[/bold #9370DB]")
                    console.print("  [bold]/toggle[/bold]: Command to toggle between Interaction and Shell modes")
                    console.print("  [bold]Shift+![/bold]: Conceptual keyboard shortcut for mode switching")
                    console.print("  [dim]Use /toggle command as the primary method for switching modes[/dim]")
                    console.print()
                    continue
                elif prompt.lower() == '/exit':
                    # Allow user to exit using /exit command
                    # Display conversation history before exiting
                    console.print(Panel("[bold yellow]Conversation Summary[/bold yellow]", expand=False))
                    display_conversation_history(agent)
                    console.print("\n[bold #32CD32]Thank you for using Codeius! Goodbye![/bold #32CD32]")
                    break
                elif prompt.lower().startswith('/create_project '):
                    # Extract project details from the command
                    parts = prompt.split(' ', 2)  # Split into at most 3 parts: '/create_project', 'type', 'name'
                    if len(parts) >= 3:
                        project_type = parts[1].strip().lower()
                        project_name = parts[2].strip()

                        # Import and execute the appropriate template function based on project type
                        try:
                            # Use the project_templates module to create the project
                            from .project_templates import create_project
                            create_project(project_type, project_name)
                        except Exception as e:
                            console.print(f"[bold red]Error creating project: {str(e)}[/bold red]")
                    else:
                        console.print("[bold red]Please specify both project type and name. Usage: /create_project [type] [name][/bold red]")
                        console.print("[bold yellow]Available types: fastapi, flask, django, react, nodejs, ai_ml[/bold yellow]")
                    continue
                else:
                    console.print(f"[bold red]Unknown command: {prompt}[/bold red]")
                    console.print("[bold yellow]Available commands: Use /help to see full list of available commands[/bold yellow]")
                    continue

            if prompt.lower() == "exit":
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

            # Handle shell mode: if in shell mode, execute prompt as shell command
            if not mode_container['interaction'] and not prompt.startswith('/'):
                execute_shell_command_safe(prompt)
                continue

            # Show loading animation while waiting for agent response
            console.print(f"[bold #00FFFF]Processing query...[/bold #00FFFF]")
            import threading
            stop_event = threading.Event()
            loading_thread = threading.Thread(target=show_loading_animation, args=(stop_event,))
            loading_thread.start()

            try:
                result = agent.ask(prompt)
            finally:
                stop_event.set()  # Stop the loading animation
                loading_thread.join()  # Wait for the thread to finish
                print()  # Add a newline after the loading message is cleared

            # Save the conversation to history - fixed for refactored architecture
            try:
                # Try to access the history via conversation manager first
                if hasattr(agent, 'conversation_manager') and hasattr(agent.conversation_manager, 'add_message'):
                    agent.conversation_manager.add_message("user", prompt)
                    agent.conversation_manager.add_message("assistant", result if not result.startswith("**Agent Plan:") else result)
                else:
                    # Fallback to direct history if conversation manager is not available
                    agent.history.append({"role": "user", "content": prompt})
                    agent.history.append({"role": "assistant", "content": result if not result.startswith("**Agent Plan:") else result})
            except AttributeError:
                # If there's any issue accessing the history, use the direct method
                if hasattr(agent, 'history'):
                    agent.history.append({"role": "user", "content": prompt})
                    agent.history.append({"role": "assistant", "content": result if not result.startswith("**Agent Plan:") else result})

            if result.startswith("**Agent Plan:**"):  # Looks like JSON action plan is parsed
                if confirm_safe_execution(result):
                    success_panel = Panel(
                        "[bold #32CD32]Success![/bold #32CD32]\n\n[white]Action(s) executed successfully.[/white]",
                        border_style="#32CD32",
                        expand=False,
                        padding=(1, 1)
                    )
                    console.print(success_panel)
                    console.print()  # Add blank line
                else:
                    cancel_panel = Panel(
                        "[bold #FF4500]Cancelled![/bold #FF4500]\n\n[white]Action(s) were not executed.[/white]",
                        border_style="#FF4500",
                        expand=False,
                        padding=(1, 1)
                    )
                    console.print(cancel_panel)
                    console.print()  # Add blank line
            else:
                # Enhanced agent response display with improved visual hierarchy
                # Format the response with rich styling
                formatted_result = format_agent_response(result)
                agent_panel = Panel(
                    formatted_result,
                    title="[bold #BA55D3]🤖 Codeius Agent Response[/bold #BA55D3]",
                    expand=False,
                    border_style="#BA55D3",  # Medium purple border
                    padding=(1, 1),
                    highlight=True
                )
                console.print(agent_panel)
                console.print()  # Add blank line for readability

            # Optionally show recent conversation history
            history_check = getattr(agent, 'history', [])
            if hasattr(agent, 'conversation_manager') and hasattr(agent.conversation_manager, 'history'):
                history_check = agent.conversation_manager.history

            if len(history_check) > 0 and len([h for h in history_check if h["role"] == "user"]) % 3 == 0:
                show_history = Prompt.ask("\n[bold yellow]Show conversation history?[/bold yellow] [Y/n]", default="Y").strip().lower()
                if show_history in ("y", "yes", ""):
                    display_conversation_history(agent)
        except KeyboardInterrupt:
            console.print("\n[bold #FF4500]Ctrl+C detected – exiting safely...[/bold #FF4500]")
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
        except Exception as e:
            console.print(f"[bold red][BAD] Error: {e}[/bold red]")

if __name__ == "__main__":
    main()