# src/cli.py

import sys
import os
import time
from threading import Thread
from typing import Generator
from coding_agent.agent import CodingAgent
from coding_agent.dashboard import Dashboard
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
    console.print("  ✅ Good - Metric is in healthy range")
    console.print("  ⚠️  Warning - Metric could be improved")
    console.print("  ❌ Poor - Metric needs attention\n")

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
            version="1.0.0"
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

def display_help():
    """Display help information with all available commands"""
    # Create a visually appealing help table
    help_table = Table(
        title="[bold #9370DB]Available Commands[/bold #9370DB]",
        title_style="bold #9370DB",
        box=HEAVY_HEAD,
        border_style="#9370DB",
        expand=True
    )
    help_table.add_column("Command", style="#7CFC00", no_wrap=True)
    help_table.add_column("Description", style="white")

    help_table.add_row("/models", "List all available AI models")
    help_table.add_row("/mcp", "List available MCP tools")
    help_table.add_row("/dashboard", "Show real-time code quality dashboard")
    help_table.add_row("/themes", "Show available visual themes")
    help_table.add_row("/ocr [image_path]", "Extract text from an image using OCR")
    help_table.add_row("/refactor [file_path]", "Analyze and refactor code in a file")
    help_table.add_row("/diff [file1] [file2]", "Compare two files or directories")
    help_table.add_row("/scaffold [name] [template]", "Generate project scaffolding")
    help_table.add_row("/env [action] [variables]", "Manage environment files")
    help_table.add_row("/rename [old] [new] [file]", "Batch rename variables")
    help_table.add_row("/plot [metric]", "Plot code metrics and data")
    help_table.add_row("/update_docs [type] [args]", "Update documentation files")
    help_table.add_row("/snippet [action] [args]", "Manage code snippets")
    help_table.add_row("/scrape [file_or_dir_or_url] [css_selector]", "Scrape web content")
    help_table.add_row("/config [action] [args]", "Manage configurations")
    help_table.add_row("/schedule [task_type] [interval] [target]", "Schedule tasks to run automatically")
    help_table.add_row("/inspect [package]", "Inspect package information")
    help_table.add_row("/plugins", "List available plugins")
    help_table.add_row("/create_plugin [name]", "Create a new plugin skeleton")
    help_table.add_row("/switch [model_key]", "Switch to a specific model")
    help_table.add_row("/help", "Show this help message")
    help_table.add_row("/clear", "Clear the conversation history")
    help_table.add_row("/exit", "Exit the application")

    console.print("\n", help_table)

    # MCP Tools table
    mcp_table = Table(
        title="[bold #9370DB]MCP Tools Available[/bold #9370DB]",
        title_style="bold #9370DB",
        box=HEAVY_HEAD,
        border_style="#9370DB",
        expand=True
    )
    mcp_table.add_column("Tool", style="#7CFC00", no_wrap=True)
    mcp_table.add_column("Description", style="white")

    mcp_table.add_row("code-runner", "Execute Python code in sandboxed environment")
    mcp_table.add_row("filesystem", "Access and manage files in workspace")
    mcp_table.add_row("duckduckgo", "Perform web searches")
    mcp_table.add_row("code-search", "Search for functions, classes, and TODOs in code")
    mcp_table.add_row("shell", "Execute safe shell commands")
    mcp_table.add_row("testing", "Run automated tests")
    mcp_table.add_row("doc-search", "Search documentation files")
    mcp_table.add_row("database", "Query local SQLite databases")
    mcp_table.add_row("ocr", "Extract text from images")
    mcp_table.add_row("refactor", "Analyze and refactor code")
    mcp_table.add_row("diff", "Compare files and directories")
    mcp_table.add_row("automation", "Automate repetitive coding tasks")
    mcp_table.add_row("visualization", "Create plots and visualizations")
    mcp_table.add_row("self_documenting", "Auto-update documentation")
    mcp_table.add_row("package_inspector", "Inspect packages and dependencies")
    mcp_table.add_row("snippet_manager", "Manage code snippets and templates")
    mcp_table.add_row("web_scraper", "Scrape web content from files/urls")
    mcp_table.add_row("config_manager", "Manage configurations and credentials")
    mcp_table.add_row("task_scheduler", "Schedule tasks to run automatically")

    console.print("\n", mcp_table)
    console.print()

def display_welcome_screen():
    """Display an enhanced welcome screen with project info and instructions"""
    # Display beautiful ASCII art for CODEIUS with improved font
    ascii_art = pyfiglet.figlet_format("CODEIUS", font="slant")
    console.print(f"[bold #8A2BE2]{ascii_art}[/bold #8A2BE2]")  # Deep purple color

    # Create a welcome table with project information
    welcome_table = Table(
        title="[bold #9370DB on #00008B]Welcome to Codeius AI Coding Agent[/bold #9370DB on #00008B]",
        title_style="bold #9370DB",
        box=HEAVY_HEAD,
        border_style="#9370DB",
        expand=True,
        padding=(0, 1)
    )

    welcome_table.add_column("Feature", style="#7CFC00", no_wrap=True)  # Chartreuse green
    welcome_table.add_column("Description", style="white")

    welcome_table.add_row("File Operations", "Read and write source files in the workspace")
    welcome_table.add_row("Git Operations", "Perform git operations (stage, commit)")
    welcome_table.add_row("Web Search", "Perform real-time web searches via DuckDuckGo (no API key needed)")
    welcome_table.add_row("AI Integration", "Powered by multiple LLM providers (Groq, Google)")
    welcome_table.add_row("MCP Servers", "Access additional tools via MCP protocol (code search, shell, testing, docs, databases)")
    welcome_table.add_row("Dashboard", "Real-time code quality, test coverage, and build metrics")

    console.print(welcome_table)

    # Create a visually appealing status panel
    status_panel = Panel(
        "[bold #00FFFF]Status:[/bold #00FFFF] [green]All systems operational[/green]\n"
        "[bold #00FFFF]Version:[/bold #00FFFF] [magenta]1.0.0[/magenta]\n"
        "[bold #00FFFF]Uptime:[/bold #00FFFF] [cyan]Ready for use[/cyan]\n",
        title="[bold #40E0D0]System Status[/bold #40E0D0]",
        border_style="#40E0D0",
        expand=False
    )
    console.print(status_panel)

    # Instructions panel with gradient-like effect
    console.print("\n[bold #7CFC00]How to Use:[/bold #7CFC00]")
    instructions_text = (
        "- Type your coding instructions in the input field\n"
        "- The agent will analyze your request and suggest actions\n"
        "- You'll be prompted to confirm any file changes or git operations\n"
        "- Type 'exit', 'quit', or 'bye' to exit the application\n"
        "- Use commands starting with [bold #00FFFF]/[/bold #00FFFF] for special features\n"
    )
    console.print(Panel(
        instructions_text,
        title="[bold #40E0D0]Instructions[/bold #40E0D0]",
        expand=False,
        border_style="#40E0D0"  # Turquoise
    ))

    # Add a decorative separator with gradient effect
    console.print(Rule("[bold #BA55D3]Powered by Advanced AI and Cutting-Edge Technology[/bold #BA55D3]", style="#BA55D3", align="center"))
    console.print()  # Extra spacing

def show_loading_animation(stop_event):
    """Show a loading animation while waiting for agent response"""
    symbols = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']  # Spinning animation
    i = 0
    while not stop_event.is_set():
        sys.stdout.write(f'\r[bold #00FFFF]{symbols[i % len(symbols)]} Processing your request...[/bold #00FFFF]')
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
    response_text = re.sub(r'(✅)', r'[bold #32CD32]\1[/bold #32CD32]', response_text)

    # Format error indicators
    response_text = re.sub(r'(❌)', r'[bold #FF4500]\1[/bold #FF4500]', response_text)

    # Format warning indicators
    response_text = re.sub(r'(⚠️)', r'[bold #FFA500]\1[/bold #FFA500]', response_text)

    # Format web search indicators
    response_text = re.sub(r'(🌐)', r'[bold #00FFFF]\1[/bold #00FFFF]', response_text)

    # Format agent explanations
    response_text = re.sub(r'(-\s[^\.!\n]*\.|- [^\n]*)', r'[#BA55D3]\1[/#BA55D3]', response_text)

    return response_text

def display_conversation_history(agent):
    """Display a summary of the conversation history"""
    if not agent.history:
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

    for i, entry in enumerate(agent.history):
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
    console.print(Panel(f"[white]Total messages: {len(agent.history)}[/white]", border_style="#40E0D0", expand=False))
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
            elif command in ['/help', '/clear', '/mcp', '/models', '/dashboard', '/ocr', '/refactor', '/diff', '/plugins', '/create_plugin', '/scaffold', '/env', '/rename', '/plot', '/update_docs', '/inspect', '/snippet', '/scrape', '/config', '/schedule', '/exit']:
                # Don't provide additional completions if these commands are fully typed
                pass
            else:
                # Provide command suggestions for commands that don't require parameters
                commands = ['/models', '/mcp', '/dashboard', '/ocr', '/refactor', '/diff', '/plugins', '/create_plugin', '/scaffold', '/env', '/rename', '/plot', '/update_docs', '/inspect', '/snippet', '/scrape', '/config', '/schedule', '/switch', '/help', '/clear', '/exit']
                for cmd in commands:
                    if cmd.startswith(text.lower()):
                        yield Completion(cmd, start_position=-len(text))

def main():
    # Show startup animation using sys.stdout for direct output without Rich
    import sys
    for i in range(3):
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(0.3)
    sys.stdout.write("\n")
    sys.stdout.flush()

    display_welcome_screen()

    console.print(Panel("[bold #32CD32]Initialization complete![/bold #32CD32]\n[white]Ready to assist with your coding tasks.[/white]", border_style="#32CD32", expand=False))
    time.sleep(0.5)  # Brief pause for visual effect

    agent = CodingAgent()

    # Create a custom completer that handles both commands and model suggestions
    completer = CustomCompleter(agent)

    # Create a prompt session with enhanced styling and custom completion
    style = Style.from_dict({
        'prompt': 'bold #00FFFF',
        'completion-menu': 'bg:#262626 #ffffff',
        'completion-menu.completion.current': 'bg:#4a4a4a #ffffff',
        'completion-menu.meta.completion': 'bg:#262626 #ffffff',
        'completion-menu.meta.completion.current': 'bg:#4a4a4a #ffffff',
    })

    session = PromptSession(
        completer=completer,
        style=style,
        complete_while_typing=True,
    )

    while True:
        try:
            # Styled prompt with more distinct visual indicator and auto-completion
            prompt_text = HTML('<style fg="#00FFFF" bg="black">🤖 Enter your query: </style> ')
            prompt = session.prompt(
                prompt_text,
                default='',
                complete_style=CompleteStyle.MULTI_COLUMN,
                style=Style.from_dict({
                    'prompt': 'bold #00FFFF',
                    'text': 'white',
                    'completion-menu': 'bg:#262626 #ffffff',
                    'completion-menu.completion.current': 'bg:#4a4a4a #ffffff',
                    'completion-menu.meta.completion': 'bg:#262626 #ffffff',
                    'completion-menu.meta.completion.current': 'bg:#4a4a4a #ffffff',
                })
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
                    console.print("[bold #32CD32]✅ Conversation history cleared.[/bold #32CD32]")
                    continue
                elif prompt.lower() == '/cls' or prompt.lower() == '/clear_screen':
                    # Clear the entire screen with a visual effect
                    console.clear()
                    display_welcome_screen()
                    continue
                elif prompt.lower() == '/exit':
                    # Allow user to exit using /exit command
                    # Display conversation history before exiting
                    console.print(Panel("[bold yellow]Conversation Summary[/bold yellow]", expand=False))
                    display_conversation_history(agent)
                    console.print("\n[bold #32CD32]👋 Thank you for using Codeius! Goodbye![/bold #32CD32]")
                    break
                else:
                    console.print(f"[bold red]Unknown command: {prompt}[/bold red]")
                    console.print("[bold yellow]Available commands: /models, /mcp, /themes, /cls, /dashboard, /switch [model_key], /help, /clear, /exit[/bold yellow]")
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

            if result.startswith("**Agent Plan:**"):  # Looks like JSON action plan is parsed
                if confirm_safe_execution(result):
                    success_panel = Panel(
                        "[bold #32CD32]✅ Success![/bold #32CD32]\n\n[white]Action(s) executed successfully.[/white]",
                        border_style="#32CD32",
                        expand=False,
                        padding=(1, 1)
                    )
                    console.print(success_panel)
                    console.print()  # Add blank line
                else:
                    cancel_panel = Panel(
                        "[bold #FF4500]❌ Cancelled![/bold #FF4500]\n\n[white]Action(s) were not executed.[/white]",
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
            if len(agent.history) > 0 and len([h for h in agent.history if h["role"] == "user"]) % 3 == 0:
                show_history = Prompt.ask("\n[bold yellow]Show conversation history?[/bold yellow] [Y/n]", default="Y").strip().lower()
                if show_history in ("y", "yes", ""):
                    display_conversation_history(agent)
        except KeyboardInterrupt:
            console.print("\n[bold #FF4500]⚠️  Ctrl+C detected – exiting safely...[/bold #FF4500]")
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
            console.print(f"[bold red]❌ Error: {e}[/bold red]")

if __name__ == "__main__":
    main()