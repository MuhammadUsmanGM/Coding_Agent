"""
Advanced Security Management System for Codeius AI Coding Agent
Includes code vulnerability scanning, secrets detection, and policy enforcement
"""
import os
import re
import subprocess
import tempfile
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import json
import hashlib
import yaml


class SecurityScanner:
    """Main security scanner that coordinates vulnerability scanning, secrets detection, and policy enforcement"""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).resolve()
        self.findings = []
        self.secrets = []
        self.policy_violations = []
        self.vulnerabilities = []
    
    def scan_project(self, include_secrets=True, include_vulnerabilities=True, include_policies=True) -> Dict[str, List]:
        """Perform comprehensive security scan of the project"""
        self.findings = []
        self.secrets = []
        self.policy_violations = []
        self.vulnerabilities = []
        
        results = {
            'secrets_detected': [],
            'vulnerabilities_found': [],
            'policy_violations': [],
            'summary': {
                'total_secrets': 0,
                'total_vulnerabilities': 0,
                'total_policy_violations': 0
            }
        }
        
        if include_secrets:
            results['secrets_detected'] = self.detect_secrets()
            results['summary']['total_secrets'] = len(results['secrets_detected'])
        
        if include_vulnerabilities:
            results['vulnerabilities_found'] = self.scan_vulnerabilities()
            results['summary']['total_vulnerabilities'] = len(results['vulnerabilities_found'])
        
        if include_policies:
            results['policy_violations'] = self.check_policy_enforcement()
            results['summary']['total_policy_violations'] = len(results['policy_violations'])
        
        return results
    
    def detect_secrets(self) -> List[Dict[str, str]]:
        """Detect secrets and sensitive information in codebase"""
        secrets_found = []
        
        # Common secret patterns to detect
        secret_patterns = [
            # API keys
            (r'(?i)(secret|token|password|passwd|pwd|key|api_key|api-key|access_token|auth|authorization|session).*["\']([^"\']{10,})["\']', 'Potential Secret/API Key'),
            (r'(?i)(aws_access|aws_secret|s3_access|s3_secret).*["\']([^"\']{10,})["\']', 'AWS Credentials'),
            (r'(?i)ssh-rsa [a-z0-9+/]{10,}(?:={0,2})?', 'SSH Key'),
            (r'-----BEGIN (?:RSA |EC |DSA )?(?:PRIVATE|PUBLIC) KEY-----', 'SSH/RSA Key'),
            # OAuth patterns
            (r'(?i)(client_secret|client_id).*["\']([a-z0-9_-]{10,})["\']', 'OAuth Credential'),
            # Database connection strings
            (r'(?i)(database|db|string).*["\'](?:postgresql://|mysql://|sqlite://)?(?:[a-z0-9-]+\.)+[a-z]{2,}["\']', 'Database Connection String'),
            # Email addresses (may contain login credentials)
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'Email Address'),
            # Phone numbers (may indicate contact info)
            (r'(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}', 'Phone Number'),
        ]
        
        for file_path in self._get_python_files():
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                for pattern, description in secret_patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        secrets_found.append({
                            'file': str(file_path),
                            'line_number': content[:match.start()].count('\n') + 1,
                            'pattern': pattern,
                            'description': description,
                            'match': match.group(0)[:100],  # First 100 chars of match
                            'severity': 'high' if 'key|password|secret|token' in pattern else 'medium'
                        })
            except Exception:
                # Skip files that can't be read
                continue
        
        self.secrets = secrets_found
        return secrets_found
    
    def scan_vulnerabilities(self) -> List[Dict[str, str]]:
        """Scan for code vulnerabilities using Bandit and other tools"""
        vulnerabilities = []
        
        # Try to run bandit if available
        try:
            # Find all Python files
            python_files = self._get_python_files()
            
            if not python_files:
                return vulnerabilities
            
            # Create a temporary file list if there are many files
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                for py_file in python_files:
                    f.write(str(py_file) + '\n')
                file_list = f.name
            
            try:
                # Run bandit on all Python files
                result = subprocess.run([
                    'bandit', 
                    '-r',  # Recursive
                    '-f', 'json',  # Output format
                    '-ll',  # Low severity
                    '-ii',  # Ignore N
                    str(self.project_path)
                ], capture_output=True, text=True, timeout=60)  # 1 minute timeout
                
                if result.returncode in [0, 1]:  # Bandit returns 1 if vulnerabilities found
                    try:
                        bandit_output = json.loads(result.stdout)
                        
                        for result in bandit_output.get('results', []):
                            vulnerability = {
                                'file': result['filename'],
                                'line': result['line_no'],
                                'test_id': result['test_id'],
                                'issue_severity': result['issue_severity'],
                                'issue_confidence': result['issue_confidence'],
                                'issue_text': result['issue_text'],
                                'more_info': result['more_info'],
                                'code': result.get('code', '')[:200]  # First 200 chars
                            }
                            vulnerabilities.append(vulnerability)
                    except json.JSONDecodeError:
                        # If JSON parsing fails, try to parse the human-readable output
                        lines = result.stdout.split('\n')
                        if lines:
                            vulnerabilities.append({
                                'file': 'bandit_scan_failed',
                                'line': 'N/A',
                                'test_id': 'SCAN_ERROR',
                                'issue_severity': 'HIGH',
                                'issue_confidence': 'HIGH',
                                'issue_text': 'Bandit scan failed to produce valid JSON output',
                                'more_info': '',
                                'code': result.stdout[:500]
                            })
                
            except subprocess.TimeoutExpired:
                vulnerabilities.append({
                    'file': 'bandit_scan_timeout',
                    'line': 'N/A',
                    'test_id': 'SCAN_TIMEOUT',
                    'issue_severity': 'MEDIUM',
                    'issue_confidence': 'MEDIUM',
                    'issue_text': 'Bandit scan took too long and was terminated',
                    'more_info': '',
                    'code': ''
                })
            except FileNotFoundError:
                # Bandit not installed, return a message
                vulnerabilities.append({
                    'file': 'bandit_missing',
                    'line': 'N/A',
                    'test_id': 'TOOL_MISSING',
                    'issue_severity': 'LOW',
                    'issue_confidence': 'LOW',
                    'issue_text': 'Bandit is not installed. Install with: pip install bandit',
                    'more_info': 'https://bandit.readthedocs.io/en/latest/',
                    'code': ''
                })
            finally:
                # Clean up the temporary file
                if os.path.exists(file_list):
                    os.remove(file_list)
        
        except Exception as e:
            # If anything goes wrong, return an error
            vulnerabilities.append({
                'file': 'scan_error',
                'line': 'N/A',
                'test_id': 'SCAN_ERROR',
                'issue_severity': 'HIGH',
                'issue_confidence': 'HIGH',
                'issue_text': f'Security scan error: {str(e)}',
                'more_info': '',
                'code': ''
            })
        
        self.vulnerabilities = vulnerabilities
        return vulnerabilities
    
    def check_policy_enforcement(self) -> List[Dict[str, str]]:
        """Check for policy violations in the codebase"""
        violations = []
        
        # Common policy violation patterns
        policy_patterns = [
            # Hardcoded passwords in source code 
            (r'(?i)(password|pwd|passwd)\s*[=:]\s*["\'][^"\']{3,20}["\']', 'Hardcoded Password'),
            # SQL injection vulnerability patterns
            (r'(?i)(cursor|execute|query).*[+]|\%\s*\(|\.format\(', 'Possible SQL Injection'),
            # OS command injection patterns
            (r'(?i)(os\.system|subprocess\.call|subprocess\.run|exec|eval)\([^)]*(\+|\%)', 'Possible Command Injection'),
            # Weak cryptography
            (r'(?i)(md5|sha1)\s*\(', 'Weak Cryptographic Hash'),
            # Insecure SSL/TLS
            (r'(?i)(ssl\.wrap_socket|create_default_context).*verify_mode\s*=\s*ssl\.CERT_NONE', 'Insecure SSL Configuration'),
        ]
        
        for file_path in self._get_python_files():
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                for pattern, description in policy_patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        line_number = content[:match.start()].count('\n') + 1
                        
                        violations.append({
                            'file': str(file_path),
                            'line': line_number,
                            'pattern': pattern,
                            'description': description,
                            'match': match.group(0)[:100],
                            'severity': 'high' if 'password|injection' in pattern.lower() else 'medium'
                        })
            except Exception:
                # Skip files that can't be read
                continue
        
        # Check for missing security headers in Flask/Django apps
        for file_path in self._get_python_files():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for Flask apps without security headers
                if 'from flask import' in content:
                    if not any(header in content for header in [
                        'Content-Security-Policy', 
                        'X-Frame-Options', 
                        'X-XSS-Protection',
                        'X-Content-Type-Options'
                    ]):
                        violations.append({
                            'file': str(file_path),
                            'line': 1,
                            'pattern': 'missing_security_headers',
                            'description': 'Flask app potentially missing security headers',
                            'match': 'Flask import found without security headers',
                            'severity': 'medium'
                        })
            except Exception:
                continue
        
        self.policy_violations = violations
        return violations
    
    def _get_python_files(self) -> List[Path]:
        """Get all Python files in the project"""
        python_files = []
        
        for ext in ['.py', '.pyx', '.pyw']:
            for file_path in self.project_path.rglob(f'*{ext}'):
                # Skip virtual environments, git directories, etc.
                if any(skip_dir in str(file_path) for skip_dir in ['.git', '__pycache__', '.venv', 'venv', '.tox', 'node_modules']):
                    continue
                python_files.append(file_path)
        
        return python_files
    
    def create_security_report(self, output_file: Optional[str] = None) -> str:
        """Generate a comprehensive security report"""
        scan_results = self.scan_project()
        
        report = f"""
# Security Report for Project: {self.project_path}

Date: {self._get_current_datetime()}

## Summary
- Total Secrets Detected: {scan_results['summary']['total_secrets']}
- Total Vulnerabilities Found: {scan_results['summary']['total_vulnerabilities']}
- Total Policy Violations: {scan_results['summary']['total_policy_violations']}

"""
        
        # Add secrets section
        if scan_results['secrets_detected']:
            report += "\n## Secrets Detection Results\n\n"
            for secret in scan_results['secrets_detected']:
                report += f"- **File**: {secret['file']}:{secret['line_number']}\n"
                report += f"  - **Type**: {secret['description']}\n"
                report += f"  - **Match**: {secret['match']}\n"
                report += f"  - **Severity**: {secret['severity'].upper()}\n\n"
        
        # Add vulnerabilities section
        if scan_results['vulnerabilities_found']:
            report += "\n## Vulnerability Scan Results\n\n"
            for vuln in scan_results['vulnerabilities_found']:
                report += f"- **File**: {vuln['file']}\n"
                report += f"  - **Test ID**: {vuln['test_id']}\n"
                report += f"  - **Severity**: {vuln['issue_severity']}\n"
                report += f"  - **Issue**: {vuln['issue_text']}\n\n"
        
        # Add policy violations section
        if scan_results['policy_violations']:
            report += "\n## Policy Violations\n\n"
            for violation in scan_results['policy_violations']:
                report += f"- **File**: {violation['file']}:{violation['line']}\n"
                report += f"  - **Description**: {violation['description']}\n"
                report += f"  - **Match**: {violation['match']}\n"
                report += f"  - **Severity**: {violation['severity'].upper()}\n\n"
        
        if not any([scan_results['secrets_detected'], scan_results['vulnerabilities_found'], scan_results['policy_violations']]):
            report += "\n## Security Status\n\n✅ No security issues detected!\n"
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
        
        return report
    
    def _get_current_datetime(self) -> str:
        """Get current datetime as string"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class SecurityPolicyManager:
    """Manages security policies and enforcement"""
    
    def __init__(self, policy_file: Optional[str] = None):
        self.policy_file = policy_file or '.codeius-security.yml'
        self.default_policy = {
            'secrets_detection_enabled': True,
            'vulnerability_scanning_enabled': True,
            'policy_enforcement_enabled': True,
            'minimum_severity_to_report': 'medium',  # low, medium, high
            'allowed_packages': [],  # Whitelisted packages
            'blocked_packages': [],  # Blacklisted packages
            'forbidden_functions': ['eval', 'exec', 'compile'],  # Dangerous functions to block
            'required_headers': ['Content-Security-Policy', 'X-Frame-Options']  # Security headers
        }
        
        self.policy = self._load_policy()
    
    def _load_policy(self) -> Dict:
        """Load security policy from file or use defaults"""
        if os.path.exists(self.policy_file):
            try:
                with open(self.policy_file, 'r', encoding='utf-8') as f:
                    file_policy = yaml.safe_load(f) or {}
                # Merge with defaults
                merged_policy = self.default_policy.copy()
                merged_policy.update(file_policy)
                return merged_policy
            except Exception:
                # If policy file is malformed, use defaults
                pass
        
        return self.default_policy
    
    def save_policy(self):
        """Save current policy to file"""
        with open(self.policy_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.policy, f, default_flow_style=False)
    
    def get_policy(self) -> Dict:
        """Get current policy"""
        return self.policy
    
    def update_policy(self, updates: Dict):
        """Update policy with new values"""
        self.policy.update(updates)
        self.save_policy()


# Initialize a global security scanner instance
security_scanner = SecurityScanner()
security_policy_manager = SecurityPolicyManager()