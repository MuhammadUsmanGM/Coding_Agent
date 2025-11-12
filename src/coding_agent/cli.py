# src/cli.py

import sys
from coding_agent.agent import CodingAgent
from dotenv import load_dotenv
from rich.console import Console
from rich.text import Text
from rich.prompt import Prompt
from rich.panel import Panel
from rich import print as rprint
import pyfiglet
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

def main():
    # Display beautiful ASCII art for CODEIUS
    ascii_art = pyfiglet.figlet_format("CODEIUS", font="standard")
    console.print(f"[bold magenta]{ascii_art}[/bold magenta]")
    console.print(Panel("[bold green]AI Coding Agent[/bold green] - Type your instructions ('exit' to quit)", expand=False))
    
    agent = CodingAgent()

    while True:
        try:
            # Use prompt-toolkit for a more advanced input box experience
            prompt = Prompt.ask("\n[bold cyan]You[/bold cyan]", default="").strip()
            
            if not prompt: continue
            if prompt.lower() in ("exit", "quit", "bye"):
                console.print("\n[bold green]👋 Goodbye![/bold green]")
                break
            result = agent.ask(prompt)
            if result.startswith("**Agent Plan:**"):  # Looks like JSON action plan is parsed
                if confirm_safe_execution(result):
                    console.print("\n[bold green]Action(s) executed.[/bold green]\n")
                else:
                    console.print("[bold red]Cancelled.[/bold red]\n")
            else:
                console.print(Panel(result, title="[bold magenta]Agent[/bold magenta]", expand=False))
                console.print()  # Add blank line for readability
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Ctrl+C detected – use 'exit' to quit.[/bold yellow]")
        except Exception as e:
            console.print(f"[bold red]Error: {e}[/bold red]")

if __name__ == "__main__":
    main()
