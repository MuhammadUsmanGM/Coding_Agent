"""
Dashboard module for code quality, test coverage, and build metrics
"""
import os
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
import datetime
from rich.table import Table
from rich.progress import Progress
from rich.console import Console


@dataclass
class QualityMetrics:
    """Data class to hold quality metrics"""
    code_quality_score: float
    test_coverage: float
    build_status: str  # "success", "failure", "unknown"
    issues_found: int
    last_updated: datetime.datetime
    files_scanned: int


class Dashboard:
    """Manages real-time dashboards for code quality, test coverage, and build metrics"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.console = Console()
        self.metrics = QualityMetrics(
            code_quality_score=0.0,
            test_coverage=0.0,
            build_status="unknown",
            issues_found=0,
            last_updated=datetime.datetime.now(),
            files_scanned=0
        )
        
    def update_metrics(self):
        """Update all metrics by running analysis tools"""
        self.metrics.last_updated = datetime.datetime.now()
        
        # Update code quality (example using basic file count as placeholder)
        self._update_code_quality()
        
        # Update test coverage (example using basic scan as placeholder)
        self._update_test_coverage()
        
        # Update build status (example using basic scan as placeholder)
        self._update_build_status()
    
    def _update_code_quality(self):
        """Update code quality metrics"""
        # Count Python files for basic quality metrics
        try:
            py_files = list(self.project_root.rglob("*.py"))
            self.metrics.files_scanned = len(py_files)
            
            # Calculate a basic quality score based on number of files and some heuristics
            # This is a simplified approach - in real usage, you'd run tools like pylint, flake8, etc.
            total_lines = 0
            for file_path in py_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        total_lines += len(lines)
                except:
                    continue
            
            # Simplified quality score calculation
            if total_lines > 0:
                avg_lines_per_file = total_lines / len(py_files) if py_files else 0
                # Normalize to 0-100 scale (simplified)
                quality_score = min(100, (len(py_files) * 10 + avg_lines_per_file / 10))
                self.metrics.code_quality_score = min(100.0, quality_score)
            else:
                self.metrics.code_quality_score = 0.0
                
        except Exception as e:
            print(f"Error calculating code quality: {e}")
            self.metrics.code_quality_score = 0.0
    
    def _update_test_coverage(self):
        """Update test coverage metrics"""
        # Count test files for basic coverage metrics
        try:
            test_files = list(self.project_root.rglob("test_*.py")) + list(self.project_root.rglob("*_test.py"))
            
            # Simplified test coverage calculation
            # In a real scenario, you would run coverage tools like pytest-cov
            total_files = len(list(self.project_root.rglob("*.py")))
            test_files_count = len(test_files)
            
            if total_files > 0:
                self.metrics.test_coverage = min(100.0, (test_files_count / total_files) * 100)
            else:
                self.metrics.test_coverage = 0.0
                
        except Exception as e:
            print(f"Error calculating test coverage: {e}")
            self.metrics.test_coverage = 0.0
    
    def _update_build_status(self):
        """Update build status"""
        # Check for common build artifacts or run basic syntax check
        try:
            # Basic syntax check using Python
            py_files = list(self.project_root.rglob("*.py"))
            error_count = 0
            
            for file_path in py_files[:20]:  # Limit to first 20 files to avoid long checks
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        code = f.read()
                    compile(code, str(file_path), 'exec')
                except SyntaxError:
                    error_count += 1
            
            if error_count == 0:
                self.metrics.build_status = "success"
            else:
                self.metrics.build_status = "failure"
                self.metrics.issues_found = error_count
                
        except Exception as e:
            print(f"Error checking build status: {e}")
            self.metrics.build_status = "unknown"
    
    def generate_dashboard(self) -> str:
        """Generate dashboard as a string representation"""
        self.update_metrics()
        
        output = []
        output.append(f"[bold blue]Code Dashboard[/bold blue] - Last updated: {self.metrics.last_updated.strftime('%Y-%m-%d %H:%M:%S')}")
        output.append("")
        
        # Code Quality Section
        output.append(f"[bold]Code Quality Score:[/bold] {self.metrics.code_quality_score:.1f}/100")
        quality_bar = self._create_progress_bar(self.metrics.code_quality_score)
        output.append(quality_bar)
        output.append("")
        
        # Test Coverage Section
        output.append(f"[bold]Test Coverage:[/bold] {self.metrics.test_coverage:.1f}%")
        coverage_bar = self._create_progress_bar(self.metrics.test_coverage)
        output.append(coverage_bar)
        output.append("")
        
        # Build Status Section
        status_emoji = "✅" if self.metrics.build_status == "success" else "❌" if self.metrics.build_status == "failure" else "❓"
        output.append(f"[bold]Build Status:[/bold] {status_emoji} {self.metrics.build_status.title()}")
        output.append("")
        
        # Additional Metrics
        output.append(f"[bold]Files Scanned:[/bold] {self.metrics.files_scanned}")
        output.append(f"[bold]Issues Found:[/bold] {self.metrics.issues_found}")
        
        return "\n".join(output)
    
    def _create_progress_bar(self, value: float) -> str:
        """Create a text-based progress bar"""
        bar_length = 20
        filled_length = int(bar_length * value / 100)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        return f"[{bar}] {value:.1f}%"
    
    def generate_rich_dashboard(self) -> Table:
        """Generate a Rich table dashboard"""
        self.update_metrics()
        
        table = Table(title=f"Code Dashboard - Updated: {self.metrics.last_updated.strftime('%Y-%m-%d %H:%M:%S')}", 
                      title_style="bold blue",
                      show_header=True,
                      header_style="bold magenta")
        
        table.add_column("Metric", style="dim", width=15)
        table.add_column("Value", justify="right", style="bold")
        table.add_column("Status", style="dim")
        
        # Code Quality Row
        quality_status = "✅" if self.metrics.code_quality_score >= 70 else "⚠️" if self.metrics.code_quality_score >= 40 else "❌"
        table.add_row(
            "Code Quality",
            f"{self.metrics.code_quality_score:.1f}/100",
            quality_status
        )
        
        # Test Coverage Row
        coverage_status = "✅" if self.metrics.test_coverage >= 80 else "⚠️" if self.metrics.test_coverage >= 50 else "❌"
        table.add_row(
            "Test Coverage", 
            f"{self.metrics.test_coverage:.1f}%",
            coverage_status
        )
        
        # Build Status Row
        build_status = "✅" if self.metrics.build_status == "success" else "❌" if self.metrics.build_status == "failure" else "❓"
        table.add_row(
            "Build Status",
            self.metrics.build_status.title(),
            build_status
        )
        
        # Additional metrics
        table.add_row("Files Scanned", str(self.metrics.files_scanned), "")
        table.add_row("Issues Found", str(self.metrics.issues_found), "")
        
        return table