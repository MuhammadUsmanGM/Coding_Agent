"""
Interactive help system for CLI
"""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

COMMANDS = {
    '/help': {
        'description': 'Show this help message',
        'usage': '/help [command]',
        'examples': ['/help', '/help /switch']
    },
    '/models': {
        'description': 'List available AI models',
        'usage': '/models',
        'examples': ['/models']
    },
    '/switch': {
        'description': 'Switch to a different model',
        'usage': '/switch <model_key>',
        'examples': ['/switch groq_0', '/switch google_1']
    },
    '/clear': {
        'description': 'Clear conversation history',
        'usage': '/clear',
        'examples': ['/clear']
    },
    '/history': {
        'description': 'Show command history',
        'usage': '/history [count]',
        'examples': ['/history', '/history 20']
    },
    '/files': {
        'description': 'List uploaded files',
        'usage': '/files',
        'examples': ['/files']
    },
    '/scan': {
        'description': 'Scan project directory',
        'usage': '/scan [path]',
        'examples': ['/scan', '/scan ./src']
    },
    '/git': {
        'description': 'Show git status',
        'usage': '/git',
        'examples': ['/git']
    },
    '/context': {
        'description': 'Show project context',
        'usage': '/context',
        'examples': ['/context']
    },
    '/exit': {
        'description': 'Exit the CLI',
        'usage': '/exit',
        'examples': ['/exit', '/quit']
    }
}

def show_help(command: str = None):
    """Show help message"""
    if command and command in COMMANDS:
        # Show help for specific command
        cmd_info = COMMANDS[command]
        
        content = f"[bold cyan]{command}[/bold cyan]\n\n"
        content += f"{cmd_info['description']}\n\n"
        content += f"[yellow]Usage:[/yellow] {cmd_info['usage']}\n\n"
        content += f"[yellow]Examples:[/yellow]\n"
        
        for example in cmd_info['examples']:
            content += f"  • {example}\n"
        
        panel = Panel(content, title="📖 Command Help", border_style="cyan")
        console.print(panel)
    else:
        # Show all commands
        table = Table(title="📖 Codeius CLI Commands", show_header=True, header_style="bold magenta")
        table.add_column("Command", style="cyan", width=15)
        table.add_column("Description", style="white")
        table.add_column("Usage", style="yellow")
        
        for cmd, info in COMMANDS.items():
            table.add_row(cmd, info['description'], info['usage'])
        
        console.print(table)
        console.print("\n[dim]Type '/help <command>' for detailed help on a specific command[/dim]\n")
