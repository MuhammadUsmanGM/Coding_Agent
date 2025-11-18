"""
Security Management CLI commands for Codeius AI Coding Agent
"""
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from .security_manager import security_scanner, security_policy_manager
import os

console = Console()

def run_security_scan(severity_filter: Optional[str] = None):
    """Run comprehensive security scan of the current project"""
    console.print("[bold blue]🔍 Starting Security Scan...[/bold blue]")
    
    # Run the security scan
    scan_results = security_scanner.scan_project()
    
    # Display the results
    if scan_results['secrets_detected']:
        console.print(f"\n[bold red]🚨 Secrets Detected: {len(scan_results['secrets_detected'])}[/bold red]")
        secrets_table = Table(title="Secrets Found", show_header=True, header_style="bold magenta")
        secrets_table.add_column("File", style="dim")
        secrets_table.add_column("Type", style="bold")
        secrets_table.add_column("Line", style="dim")
        secrets_table.add_column("Match", style="red")
        secrets_table.add_column("Severity", style="bold")
        
        for secret in scan_results['secrets_detected']:
            if not severity_filter or secret['severity'].lower() == severity_filter.lower():
                secrets_table.add_row(
                    secret['file'],
                    secret['description'],
                    str(secret['line_number']),
                    secret['match'],
                    secret['severity'].upper()
                )
        
        console.print(secrets_table)
    
    if scan_results['vulnerabilities_found']:
        console.print(f"\n[bold red]⚠️ Vulnerabilities Found: {len(scan_results['vulnerabilities_found'])}[/bold red]")
        vulns_table = Table(title="Vulnerabilities", show_header=True, header_style="bold magenta")
        vulns_table.add_column("File", style="dim")
        vulns_table.add_column("Test ID", style="bold")
        vulns_table.add_column("Severity", style="bold red")
        vulns_table.add_column("Issue", style="red")
        
        for vuln in scan_results['vulnerabilities_found']:
            if not severity_filter or vuln['issue_severity'].lower() == severity_filter.lower():
                vulns_table.add_row(
                    vuln['file'],
                    vuln['test_id'],
                    vuln['issue_severity'],
                    vuln['issue_text'][:50] + "..." if len(vuln['issue_text']) > 50 else vuln['issue_text']
                )
        
        console.print(vulns_table)
    
    if scan_results['policy_violations']:
        console.print(f"\n[bold red]❌ Policy Violations: {len(scan_results['policy_violations'])}[/bold red]")
        policy_table = Table(title="Policy Violations", show_header=True, header_style="bold magenta")
        policy_table.add_column("File", style="dim")
        policy_table.add_column("Rule", style="bold")
        policy_table.add_column("Line", style="dim")
        policy_table.add_column("Issue", style="red")
        policy_table.add_column("Severity", style="bold")
        
        for violation in scan_results['policy_violations']:
            if not severity_filter or violation['severity'].lower() == severity_filter.lower():
                policy_table.add_row(
                    violation['file'],
                    violation['description'],
                    str(violation['line']),
                    violation['match'],
                    violation['severity'].upper()
                )
        
        console.print(policy_table)
    
    if not any([scan_results['secrets_detected'], scan_results['vulnerabilities_found'], scan_results['policy_violations']]):
        console.print("\n[bold green]✅ No security issues detected![/bold green]")
    else:
        console.print(f"\n[bold]Scan Summary:[/bold]")
        console.print(f"  • Secrets: {scan_results['summary']['total_secrets']}")
        console.print(f"  • Vulnerabilities: {scan_results['summary']['total_vulnerabilities']}")
        console.print(f"  • Policy Violations: {scan_results['summary']['total_policy_violations']}")
    
    # Generate a report file
    report_path = "security_report_" + os.getcwd().split(os.sep)[-1] + ".md"
    report = security_scanner.create_security_report(output_file=report_path)
    console.print(f"\n[bold]Report generated:[/bold] {report_path}")


def show_security_policy():
    """Display the current security policy settings"""
    policy = security_policy_manager.get_policy()
    
    console.print("[bold blue]🔒 Current Security Policy[/bold blue]")
    
    policy_table = Table(show_header=False, box=None)
    policy_table.add_column("Setting", style="bold")
    policy_table.add_column("Value", style="dim")
    
    for key, value in policy.items():
        if isinstance(value, list):
            value_str = ", ".join(map(str, value)) if value else "None"
        elif isinstance(value, bool):
            value_str = "✓ Enabled" if value else "✗ Disabled"
        else:
            value_str = str(value)
        
        policy_table.add_row(key.replace('_', ' ').title(), value_str)
    
    console.print(policy_table)


def update_security_policy(key: str, value: str):
    """Update a specific security policy setting"""
    # Convert the string value to appropriate Python type
    if value.lower() in ('true', 'yes', 'on', '1'):
        converted_value = True
    elif value.lower() in ('false', 'no', 'off', '0'):
        converted_value = False
    elif value.isdigit():
        converted_value = int(value)
    else:
        # Check if it's a list (comma-separated values)
        if ',' in value:
            converted_value = [item.strip() for item in value.split(',')]
        else:
            converted_value = value
    
    updates = {key: converted_value}
    security_policy_manager.update_policy(updates)
    
    console.print(f"[bold green]✅ Policy updated:[/bold green] {key} = {converted_value}")
    console.print("[dim]Changes saved to security policy file.[/dim]")


def create_security_report():
    """Create a comprehensive security report"""
    console.print("[bold blue]📝 Generating Security Report...[/bold blue]")
    
    report = security_scanner.create_security_report()
    
    # Show the first part of the report
    lines = report.split('\n')
    preview_lines = lines[:20]  # Show first 20 lines
    
    console.print(Panel(
        "\n".join(preview_lines) + ("\n..." if len(lines) > 20 else ""),
        title="[bold]Security Report Preview[/bold]",
        border_style="blue"
    ))
    
    report_filename = f"security_report_{hash(os.getcwd()) % 10000}.md"
    security_scanner.create_security_report(output_file=report_filename)
    console.print(f"\n[bold]Full report saved as:[/bold] {report_filename}")


def run_secrets_detection():
    """Run only the secrets detection scan"""
    console.print("[bold blue]🔍 Running Secrets Detection...[/bold blue]")
    
    secrets = security_scanner.detect_secrets()
    
    if secrets:
        console.print(f"\n[bold red]🚨 {len(secrets)} Secrets Detected![/bold red]")
        
        secrets_table = Table(title="Secrets Found", show_header=True, header_style="bold magenta")
        secrets_table.add_column("File", style="dim")
        secrets_table.add_column("Type", style="bold")
        secrets_table.add_column("Line", style="dim")
        secrets_table.add_column("Match", style="red")
        secrets_table.add_column("Severity", style="bold")
        
        for secret in secrets:
            secrets_table.add_row(
                secret['file'],
                secret['description'],
                str(secret['line_number']),
                secret['match'],
                secret['severity'].upper()
            )
        
        console.print(secrets_table)
    else:
        console.print("[bold green]✅ No secrets detected![/bold green]")


def run_vulnerability_scan():
    """Run only the vulnerability scan"""
    console.print("[bold blue]🔍 Running Vulnerability Scan...[/bold blue]")
    
    vulnerabilities = security_scanner.scan_vulnerabilities()
    
    if vulnerabilities:
        console.print(f"\n[bold red]⚠️ {len(vulnerabilities)} Vulnerabilities Found![/bold red]")
        
        vulns_table = Table(title="Vulnerabilities", show_header=True, header_style="bold magenta")
        vulns_table.add_column("File", style="dim")
        vulns_table.add_column("Test ID", style="bold")
        vulns_table.add_column("Severity", style="bold red")
        vulns_table.add_column("Issue", style="red")
        
        for vuln in vulnerabilities:
            vulns_table.add_row(
                vuln['file'],
                vuln['test_id'],
                vuln['issue_severity'],
                vuln['issue_text'][:50] + "..." if len(vuln['issue_text']) > 50 else vuln['issue_text']
            )
        
        console.print(vulns_table)
    else:
        console.print("[bold green]✅ No vulnerabilities detected![/bold green]")


def run_policy_check():
    """Run only the policy enforcement check"""
    console.print("[bold blue]🔍 Running Policy Check...[/bold blue]")
    
    violations = security_scanner.check_policy_enforcement()
    
    if violations:
        console.print(f"\n[bold red]❌ {len(violations)} Policy Violations Found![/bold red]")
        
        policy_table = Table(title="Policy Violations", show_header=True, header_style="bold magenta")
        policy_table.add_column("File", style="dim")
        policy_table.add_column("Rule", style="bold")
        policy_table.add_column("Line", style="dim")
        policy_table.add_column("Issue", style="red")
        policy_table.add_column("Severity", style="bold")
        
        for violation in violations:
            policy_table.add_row(
                violation['file'],
                violation['description'],
                str(violation['line']),
                violation['match'],
                violation['severity'].upper()
            )
        
        console.print(policy_table)
    else:
        console.print("[bold green]✅ No policy violations detected![/bold green]")