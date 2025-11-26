"""
Context Management CLI commands for Codeius AI Coding Agent
"""
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from .context_manager import ContextManager, CodeContext

console = Console()

def display_context_summary(context_manager: ContextManager):
    """Display a summary of the current project context"""
    summary = context_manager.get_context_summary()
    
    if "error" in summary:
        console.print(f"[bold red]{summary['error']}[/bold red]")
        return
    
    # Create a summary panel
    summary_text = Text()
    summary_text.append(f"Project: [bold]{summary['project_name']}[/bold]\n")
    summary_text.append(f"Path: [italic]{summary['root_path']}[/italic]\n")
    summary_text.append(f"Files: {summary['files_count']}\n")
    summary_text.append(f"Functions: {summary['functions_count']}\n")
    summary_text.append(f"Classes: {summary['classes_count']}\n")
    summary_text.append(f"Last accessed: {summary['last_accessed']}")
    
    console.print(Panel(
        summary_text,
        title="[bold blue]Project Context Summary[/bold blue]",
        border_style="blue"
    ))
    
    # Display recent files if any
    if summary['recent_files']:
        console.print("\n[bold]Recent Files:[/bold]")
        for i, file_path in enumerate(summary['recent_files'][-5:], 1):
            console.print(f"  {i}. {file_path}")


def semantic_search_command(context_manager: ContextManager, query: str):
    """Perform semantic search across the codebase"""
    if not context_manager.current_project:
        console.print("[bold red]No project context set. Use /set_project first.[/bold red]")
        return
    
    results = context_manager.semantic_search(query)
    
    if not results:
        console.print(f"[bold yellow]No results found for query: '{query}'[/bold yellow]")
        return
    
    # Create a table for results
    table = Table(title=f"Search Results for '{query}'", show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=3)
    table.add_column("Name", style="bold")
    table.add_column("Type", style="italic")
    table.add_column("File", style="dim")
    table.add_column("Lines", style="dim")
    
    for i, result in enumerate(results, 1):
        result_type = result.context_type
        file_path = result.file_path
        line_range = f"{result.line_start}-{result.line_end}"
        
        table.add_row(str(i), result.name, result_type, file_path, line_range)
    
    console.print(table)


def show_file_context(context_manager: ContextManager, file_path: str):
    """Show context information for a specific file"""
    if not context_manager.current_project:
        console.print("[bold red]No project context set. Use /set_project first.[/bold red]")
        return
    
    file_context = context_manager.get_file_context(file_path)
    
    if not file_context:
        console.print(f"[bold red]File not found in project context: {file_path}[/bold red]")
        return
    
    # Create a panel for file context
    panel_content = Text()
    panel_content.append(f"File: [bold]{file_context['file_path']}[/bold]\n\n")
    
    # Functions in file
    if file_context['functions']:
        panel_content.append("[bold]Functions:[/bold]\n")
        for func in file_context['functions']:
            panel_content.append(f"  • [italic]{func}[/italic]\n")
        panel_content.append("\n")
    
    # Classes in file
    if file_context['classes']:
        panel_content.append("[bold]Classes:[/bold]\n")
        for cls in file_context['classes']:
            panel_content.append(f"  • [italic]{cls}[/italic]\n")
        panel_content.append("\n")
    
    # Imports
    if file_context['imports']:
        panel_content.append("[bold]Imports:[/bold]\n")
        for imp in file_context['imports']:
            panel_content.append(f"  • {imp}\n")
        panel_content.append("\n")
    
    # Related files
    if file_context['related_files']:
        panel_content.append("[bold]Related Files:[/bold]\n")
        for rel_file in file_context['related_files']:
            panel_content.append(f"  • {rel_file}\n")
        panel_content.append("\n")
    
    console.print(Panel(
        panel_content,
        title=f"[bold blue]Context for {file_path}[/bold blue]",
        border_style="blue"
    ))


def set_project_command(context_manager: ContextManager, project_path: str, project_name: Optional[str] = None):
    """Set the current project context"""
    try:
        context_manager.set_project(project_path, project_name)
        console.print(f"[bold green]Project context set to: {context_manager.current_project.project_name}[/bold green]")
        console.print(f"[dim]Path: {context_manager.current_project.root_path}[/dim]")

        # Show a summary of the project structure
        summary = context_manager.get_context_summary()
        console.print(f"\n[dim]Analysis complete:[/dim] {summary['files_count']} files, {summary['functions_count']} functions, {summary['classes_count']} classes")
    except ValueError as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")


def auto_detect_project_command(context_manager: ContextManager):
    """Automatically detect and set project context for current directory"""
    current_dir = os.getcwd()

    # Look for project indicators to determine project type and name
    project_indicators = [
        'pyproject.toml', 'setup.py', 'requirements.txt', 'package.json',
        'Gemfile', 'composer.json', 'pom.xml', 'build.gradle', 'Cargo.toml'
    ]

    project_name = os.path.basename(current_dir)
    project_path = current_dir

    # Try to detect a more specific project name from configuration files
    for indicator in project_indicators:
        indicator_path = os.path.join(current_dir, indicator)
        if os.path.exists(indicator_path):
            # For now, just use the directory name, but in a full implementation
            # we could parse the file to get the actual project name
            break

    set_project_command(context_manager, project_path, project_name)


def find_element_command(context_manager: ContextManager, element_type: str, name: str):
    """Find a specific function or class by name"""
    if not context_manager.current_project:
        console.print("[bold red]No project context set. Use /set_project first.[/bold red]")
        return
    
    result = None
    if element_type.lower() == 'function':
        result = context_manager.find_function(name)
    elif element_type.lower() == 'class':
        result = context_manager.find_class(name)
    
    if result:
        console.print(f"[bold green]Found {element_type}: {result.name}[/bold green]")
        console.print(f"[dim]File: {result.file_path} (lines {result.line_start}-{result.line_end})[/dim]")
        
        # Show first few lines of content
        if result.content:
            content_preview = "\n".join(result.content[:10])  # Show first 10 lines
            console.print(Panel(
                content_preview,
                title=f"[bold]{result.name}[/bold]",
                border_style="green"
            ))
    else:
        console.print(f"[bold yellow]Could not find {element_type} named '{name}'[/bold yellow]")