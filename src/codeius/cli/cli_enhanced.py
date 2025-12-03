"""
Enhanced CLI with rich formatting and improved UX
"""
import sys
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from codeius.core.rich_formatter import (
    print_code, print_markdown, print_success, 
    print_error, print_info, print_warning, print_panel, print_table, console
)
from codeius.core.history_manager import history_manager
from codeius.cli.help import show_help
from codeius.core.agent import CodingAgent

console_cli = Console()

def print_welcome():
    """Print welcome banner"""
    welcome = """
    ╔═══════════════════════════════════════╗
    ║   🤖 Codeius AI - Enhanced CLI       ║
    ║   Intelligent Coding Assistant        ║
    ╚═══════════════════════════════════════╝
    """
    console.print(welcome, style="bold cyan")
    print_info("Type '/help' for commands, '/exit' to quit")
    console.print()

def format_ai_response(response: str):
    """Format and display AI response with syntax highlighting"""
    if '```' in response:
        # Has code blocks - render with syntax highlighting
        parts = response.split('```')
        for i, part in enumerate(parts):
            if i % 2 == 0:
                # Regular text
                if part.strip():
                    print_markdown(part)
            else:
                # Code block
                lines = part.strip().split('\n')
                lang = lines[0].strip() if lines and lines[0].strip() else 'python'
                code = '\n'.join(lines[1:]) if len(lines) > 1 else part
                
                # Only print if there's actual code
                if code.strip():
                    print_code(code, lang)
    else:
        # No code - render as markdown
        print_markdown(response)

def handle_command(agent: CodingAgent, command: str) -> bool:
    """Handle CLI commands. Returns True to continue, False to exit"""
    parts = command.split()
    cmd = parts[0].lower()
    args = parts[1:] if len(parts) > 1 else []
    
    if cmd in ['/exit', '/quit']:
        print_success("Goodbye! 👋")
        return False
    
    elif cmd == '/help':
        show_help(args[0] if args else None)
    
    elif cmd == '/history':
        # Usage: /history [count] or /history search <query> [-r]
        if args and args[0] == 'search':
            query = args[1] if len(args) > 1 else ""
            use_regex = '-r' in args
            
            results = history_manager.search(query, use_regex)
            if results:
                print_panel(f"Found {len(results)} matches for '{query}'", "🔍 History Search", "cyan")
                for i, hist_cmd in enumerate(results[-10:], 1): # Show last 10 matches
                    console.print(f"  {i}. [dim]{hist_cmd}[/dim]")
            else:
                print_warning(f"No matches found for '{query}'")
        else:
            count = int(args[0]) if args and args[0].isdigit() else 10
            recent = history_manager.get_recent(count)
            
            if recent:
                print_panel(f"Last {len(recent)} commands:", "📜 Command History", "cyan")
                for i, hist_cmd in enumerate(recent, 1):
                    console.print(f"  {i}. [dim]{hist_cmd}[/dim]")
            else:
                print_info("No command history yet")
    
    elif cmd == '/clear':
        agent.reset_history()
        print_success("Conversation history cleared")
    
    elif cmd == '/models':
        models = agent.get_available_models()
        if models:
            headers = ["Key", "Model", "Provider"]
            rows = [[key, info['name'], info['provider']] for key, info in models.items()]
            print_table(headers, rows, "🤖 Available Models")
            
            current = agent.get_current_model_info()
            if current:
                print_info(f"Current: {current['name']} ({current['provider']})")
        else:
            print_warning("No models available")
    
    elif cmd == '/switch':
        if not args:
            print_error("Usage: /switch <model_key>")
            print_info("Use '/models' to see available models")
        else:
            result = agent.switch_model(args[0])
            if "Switched to" in result:
                print_success(result)
            else:
                print_error(result)
    
    elif cmd == '/context':
        try:
            from codeius.core.project_scanner import project_scanner
            import os
            
            structure = project_scanner.scan_directory(os.getcwd())
            file_count = len(structure['files'])
            dir_count = len(structure['directories'])
            
            print_panel(
                f"📁 Files: {file_count}\n📂 Directories: {dir_count}\n💾 Total Size: {structure['total_size']:,} bytes",
                "🧠 Project Context",
                "cyan"
            )
        except Exception as e:
            print_error(f"Failed to get context: {str(e)}")
    
    elif cmd == '/git':
        try:
            import subprocess
            result = subprocess.run(['git', 'status', '--short'], capture_output=True, text=True)
            
            if result.returncode == 0:
                if result.stdout.strip():
                    print_panel(result.stdout, "🔀 Git Status", "yellow")
                else:
                    print_success("Clean working tree - no changes")
            else:
                print_warning("Not a git repository")
        except:
            print_error("Git not available")
    
                should_continue = handle_command(agent, user_input)
                history_manager.add_command(user_input, success=True)
                
                if not should_continue:
                    break
                continue
            
            # Regular AI interaction
            with console.status("[bold green]🤔 Thinking..."):
                response = agent.ask(user_input)
            
            console.print()
            format_ai_response(response)
            
            history_manager.add_command(user_input, success=True)
            
        except KeyboardInterrupt:
            console.print("\n[dim]Press Ctrl+C again or type '/exit' to quit[/dim]")
            try:
                # Give user a second chance
                Prompt.ask("[bold blue]🤖 Codeius[/bold blue]")
            except KeyboardInterrupt:
                print_success("\nGoodbye! 👋")
                break
        except EOFError:
            print_success("\nGoodbye! 👋")
            break
        except Exception as e:
            print_error(f"Error: {str(e)}")
            history_manager.add_command(user_input, success=False)

if __name__ == '__main__':
    run_enhanced_cli()
