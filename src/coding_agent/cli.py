# src/cli.py

import sys
from coding_agent.agent import CodingAgent
from dotenv import load_dotenv
from rich.console import Console
from rich.text import Text
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table
from rich.box import HEAVY_HEAD
from rich import print as rprint
from rich.rule import Rule
import pyfiglet
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.shortcuts import CompleteStyle
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
        console.print("[dim]MCP servers provide access to various model providers.[/dim]")
        return
    
    console.print("\n[bold blue]Available MCP Servers:[/bold blue]")
    for server in servers:
        status = "[green]ENABLED[/green]" if server.enabled else "[red]DISABLED[/red]"
        console.print(f"  [cyan]{server.name}[/cyan]: {server.description} - {status}")
        console.print(f"    Endpoint: {server.endpoint}")
        console.print(f"    Capabilities: {', '.join(server.capabilities)}")
    console.print("\n[bold]MCP servers provide access to local and remote models without API keys.[/bold]\n")

def display_help():
    """Display help information with all available commands"""
    console.print("\n[bold blue]Available Commands:[/bold blue]")
    console.print("  [cyan]/models[/cyan] - List all available AI models")
    console.print("  [cyan]/mcp[/cyan] - List available MCP servers")
    console.print("  [cyan]/switch [model_key][/cyan] - Switch to a specific model")
    console.print("  [cyan]/help[/cyan] - Show this help message")
    console.print("  [cyan]/clear[/cyan] - Clear the conversation history")
    console.print("  [cyan]/exit[/cyan] - Exit the application\n")

def display_welcome_screen():
    """Display an enhanced welcome screen with project info and instructions"""
    # Display beautiful ASCII art for CODEIUS with improved font
    ascii_art = pyfiglet.figlet_format("CODEIUS", font="slant")
    console.print(f"[bold magenta]{ascii_art}[/bold magenta]")
    
    # Create a welcome table with project information
    welcome_table = Table(title="Welcome to Codeius AI Coding Agent", 
                         title_style="bold blue",
                         box=HEAVY_HEAD,
                         border_style="bright_blue",
                         expand=True)
    
    welcome_table.add_column("Feature", style="cyan", no_wrap=True)
    welcome_table.add_column("Description", style="white")
    
    welcome_table.add_row("📝 File Operations", "Read and write source files in the workspace")
    welcome_table.add_row("📦 Git Operations", "Perform git operations (stage, commit)")
    welcome_table.add_row("🌐 Web Search", "Perform real-time web searches via a search API")
    welcome_table.add_row("🤖 AI Integration", "Powered by multiple LLM providers (Groq, Google, Local)")
    
    console.print(welcome_table)
    
    # Instructions panel
    instructions = (
        "[bold yellow]How to use:[/bold yellow]\n"
        "• Type your coding instructions in the input field\n"
        "• The agent will analyze your request and suggest actions\n"
        "• You'll be prompted to confirm any file changes or git operations\n"
        "• Type 'exit', 'quit', or 'bye' to exit the application\n"
    )
    console.print(Panel(instructions, title="[bold green]Instructions[/bold green]", expand=False))
    
    # Add a separator
    console.print(Rule(style="dim"))

def display_conversation_history(agent):
    """Display a summary of the conversation history"""
    if not agent.history:
        console.print("[italic dim]No conversation history yet.[/italic dim]")
        return
        
    console.print("\n[bold blue]Conversation History:[/bold blue]")
    for i, entry in enumerate(agent.history):
        role = entry["role"]
        content = entry["content"]
        if role == "user":
            console.print(f"[cyan]👤 You ({i+1}):[/cyan] {content[:100]}{'...' if len(content) > 100 else ''}")
        elif role == "assistant":
            content_preview = content[:100]
            # Remove any leading/trailing newlines or extra whitespace
            content_preview = content_preview.strip()
            console.print(f"[magenta]🤖 Agent ({i+1}):[/magenta] {content_preview}{'...' if len(content) > 100 else ''}")
    console.print()  # Add spacing

def display_models(agent):
    """Display available models to the user"""
    models = agent.get_available_models()
    current_model = agent.get_current_model_info()
    
    if not models:
        console.print("[yellow]No models available.[/yellow]")
        return
    
    console.print("\n[bold blue]Available Models:[/bold blue]")
    for key, model_info in models.items():
        if current_model and key == current_model['key']:
            # Highlight the currently active model
            console.print(f"  [green]→ {key}[/green]: {model_info['name']} ({model_info['provider']}) [Current]")
        else:
            console.print(f"  [cyan]{key}[/cyan]: {model_info['name']} ({model_info['provider']})")
    console.print("\n[bold]To switch models, use: /switch [model_key][/bold]\n")

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
            elif command in ['/help', '/clear', '/mcp', '/models', '/exit']:
                # Don't provide additional completions if these commands are fully typed
                pass
            else:
                # Provide command suggestions for commands that don't require parameters
                commands = ['/models', '/mcp', '/switch', '/help', '/clear', '/exit']
                for cmd in commands:
                    if cmd.startswith(text.lower()):
                        yield Completion(cmd, start_position=-len(text))

def main():
    display_welcome_screen()

    agent = CodingAgent()

    # Create a custom completer that handles both commands and model suggestions
    completer = CustomCompleter(agent)

    # Create a prompt session with styling and custom completion for a better input experience
    style = Style.from_dict({
        'prompt': 'bold cyan',
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
            prompt_text = HTML('<style fg="cyan" bg="black">⌨️ Enter your query: </style> ')
            prompt = session.prompt(
                prompt_text,
                default='',
                complete_style=CompleteStyle.MULTI_COLUMN
            ).strip()

            if not prompt: continue
            
            # Handle special commands
            if prompt.startswith('/'):
                if prompt.lower() == '/models':
                    display_models(agent)
                    continue
                elif prompt.lower() == '/mcp':
                    display_mcp_servers(agent)
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
                    console.print("[bold green]✅ Conversation history cleared.[/bold green]")
                    continue
                elif prompt.lower() == '/exit':
                    # Allow user to exit using /exit command
                    # Display conversation history before exiting
                    console.print(Panel("[bold yellow]Conversation Summary[/bold yellow]", expand=False))
                    display_conversation_history(agent)
                    console.print("\n[bold green]👋 Thank you for using Codeius! Goodbye![/bold green]")
                    break
                else:
                    console.print(f"[bold red]Unknown command: {prompt}[/bold red]")
                    console.print("[bold yellow]Available commands: /models, /mcp, /switch [model_key], /help, /clear, /exit, /quit, /bye[/bold yellow]")
                    continue

            if prompt.lower() == "exit":
                # Display conversation history before exiting
                console.print(Panel("[bold yellow]Conversation Summary[/bold yellow]", expand=False))
                display_conversation_history(agent)
                console.print("\n[bold green]👋 Thank you for using Codeius! Goodbye![/bold green]")
                break
            result = agent.ask(prompt)
            if result.startswith("**Agent Plan:**"):  # Looks like JSON action plan is parsed
                if confirm_safe_execution(result):
                    console.print("\n[bold green]✅ Action(s) executed successfully.[/bold green]\n")
                else:
                    console.print("[bold red]❌ Action(s) cancelled.[/bold red]\n")
            else:
                # Enhanced agent response display 
                agent_panel = Panel(
                    result, 
                    title="[bold magenta]🤖 Codeius Agent[/bold magenta]", 
                    expand=False,
                    border_style="bright_magenta"
                )
                console.print(agent_panel)
                console.print()  # Add blank line for readability
                
            # Optionally show recent conversation history
            if len(agent.history) > 0 and len([h for h in agent.history if h["role"] == "user"]) % 3 == 0:
                show_history = Prompt.ask("\n[bold yellow]Show conversation history?[/bold yellow] [Y/n]", default="Y").strip().lower()
                if show_history in ("y", "yes", ""):
                    display_conversation_history(agent)
        except KeyboardInterrupt:
            console.print("\n[bold yellow]⚠️  Ctrl+C detected – use 'exit' to quit safely.[/bold yellow]")
        except Exception as e:
            console.print(f"[bold red]❌ Error: {e}[/bold red]")

if __name__ == "__main__":
    main()