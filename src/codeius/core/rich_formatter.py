"""
Rich formatting utilities for beautiful terminal output
"""
from rich.console import Console
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme

# Custom theme
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "code": "magenta",
    "prompt": "bold blue"
})

console = Console(theme=custom_theme)

def print_code(code: str, language: str = "python"):
    """Print syntax-highlighted code"""
    try:
        syntax = Syntax(code, language, theme="monokai", line_numbers=True)
        console.print(syntax)
    except Exception as e:
        # Fallback to plain print if syntax highlighting fails
        console.print(code)

def print_markdown(text: str):
    """Print markdown with formatting"""
    try:
        md = Markdown(text)
        console.print(md)
    except:
        console.print(text)

def print_panel(content: str, title: str = None, style: str = "cyan"):
    """Print content in a panel"""
    panel = Panel(content, title=title, border_style=style)
    console.print(panel)

def print_table(headers: list, rows: list, title: str = None):
    """Print a formatted table"""
    table = Table(title=title, show_header=True, header_style="bold magenta")
    
    for header in headers:
        table.add_column(header)
    
    for row in rows:
        table.add_row(*[str(cell) for cell in row])
    
    console.print(table)

def print_success(message: str):
    """Print success message"""
    console.print(f"✓ {message}", style="success")

def print_error(message: str):
    """Print error message"""
    console.print(f"✗ {message}", style="error")

def print_warning(message: str):
    """Print warning message"""
    console.print(f"⚠ {message}", style="warning")

def print_info(message: str):
    """Print info message"""
    console.print(f"ℹ {message}", style="info")

def print_divider(char: str = "─", style: str = "dim"):
    """Print a divider line"""
    console.print(char * console.width, style=style)
