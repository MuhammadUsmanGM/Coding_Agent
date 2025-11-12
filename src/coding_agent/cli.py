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
    welcome_table.add_row("🤖 AI Integration", "Powered by multiple LLM providers (Groq, Google)")
    
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

def main():
    display_welcome_screen()

    agent = CodingAgent()

    # Create a prompt session with styling for a better input experience
    style = Style.from_dict({
        'prompt': 'bold cyan',
    })
    
    session = PromptSession(style=style)

    while True:
        try:
            # Styled prompt with more distinct visual indicator
            prompt_text = HTML('<style fg="cyan" bg="black">⌨️ Enter your query: </style> ')
            prompt = session.prompt(prompt_text, default='').strip()

            if not prompt: continue
            if prompt.lower() in ("exit", "quit", "bye"):
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