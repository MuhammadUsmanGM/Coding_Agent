"""
Language Detector Module for Codeius AI Coding Agent
Automatically detects programming languages in project files and suggests relevant tools.
"""
import os
import re
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

class LanguageDetector:
    """Detects programming languages and suggests relevant tools for projects."""
    
    def __init__(self):
        # Extension to language mapping
        self.extension_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'JavaScript',
            '.tsx': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.cxx': 'C++',
            '.cc': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.go': 'Go',
            '.rs': 'Rust',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.kts': 'Kotlin',
            '.scala': 'Scala',
            '.sql': 'SQL',
            '.html': 'HTML',
            '.htm': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.sass': 'Sass',
            '.less': 'Less',
            '.json': 'JSON',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.toml': 'TOML',
            '.xml': 'XML',
            '.md': 'Markdown',
            '.rst': 'reStructuredText',
            '.sh': 'Shell',
            '.bash': 'Shell',
            '.zsh': 'Shell',
            '.fish': 'Shell',
            '.pl': 'Perl',
            '.pm': 'Perl',
            '.lua': 'Lua',
            '.dart': 'Dart',
            '.ex': 'Elixir',
            '.exs': 'Elixir',
            '.erl': 'Erlang',
            '.hrl': 'Erlang',
            '.hs': 'Haskell',
            '.lhs': 'Haskell',
            '.jl': 'Julia',
            '.clj': 'Clojure',
            '.cljs': 'ClojureScript',
            '.coffee': 'CoffeeScript',
            '.elm': 'Elm',
            '.nim': 'Nim',
            '.cr': 'Crystal',
            '.gd': 'GDScript',
            '.v': 'V',
            '.zig': 'Zig',
            '.gdns': 'GDScript',
            '.gdnlib': 'GDScript',
            '.cfg': 'Configuration',
            '.ini': 'Configuration',
            '.env': 'Environment',
            '.dockerfile': 'Docker',
            'Dockerfile': 'Docker',
            '.proto': 'Protocol Buffers',
            '.graphql': 'GraphQL',
            '.gql': 'GraphQL',
            '.sol': 'Solidity',
            '.vue': 'Vue',
            '.svelte': 'Svelte',
        }

        # Filename to language mapping
        self.filename_map = {
            'requirements.txt': 'Python',
            'Pipfile': 'Python',
            'pyproject.toml': 'Python',
            'setup.py': 'Python',
            'poetry.lock': 'Python',
            'Gemfile': 'Ruby',
            'package.json': 'JavaScript/Node.js',
            'yarn.lock': 'JavaScript/Node.js',
            'pnpm-lock.yaml': 'JavaScript/Node.js',
            'go.mod': 'Go',
            'Cargo.toml': 'Rust',
            'Cargo.lock': 'Rust',
            'composer.json': 'PHP',
            'pom.xml': 'Java/Maven',
            'build.gradle': 'Java/Gradle',
            'build.sbt': 'Scala/SBT',
            'mix.exs': 'Elixir',
            'rebar.config': 'Erlang',
            '.gitignore': 'Generic',
            'README.md': 'Generic',
            'Dockerfile': 'Docker',
            '.dockerignore': 'Docker',
            'docker-compose.yml': 'Docker',
            'Makefile': 'Generic',
            'CMakeLists.txt': 'CMake',
            'configure': 'Shell',
            'autogen.sh': 'Shell',
            'Jenkinsfile': 'Jenkins',
            '.travis.yml': 'Travis CI',
            '.github/workflows': 'GitHub Actions',
            'azure-pipelines.yml': 'Azure Pipelines',
            'cloudbuild.yaml': 'Cloud Build',
        }

        # Tool recommendations by language
        self.tool_recommendations = {
            'Python': {
                'formatters': ['black', 'autopep8', 'yapf'],
                'linters': ['flake8', 'pylint', 'pycodestyle', 'bandit', 'mypy'],
                'test_frameworks': ['pytest', 'unittest', 'nose'],
                'suggested_config': {
                    'black': {'line_length': 88},
                    'flake8': {'max_line_length': 88, 'ignore': ['E203', 'W503']},
                    'pytest': {'test_paths': ['tests', 'test']}
                }
            },
            'JavaScript': {
                'formatters': ['prettier', 'eslint --fix'],
                'linters': ['eslint', 'jshint', 'jscs'],
                'test_frameworks': ['jest', 'mocha', 'jasmine', 'ava', 'tape'],
                'suggested_config': {
                    'eslint': {
                        'extends': ['eslint:recommended', 'plugin:prettier/recommended'],
                        'parserOptions': {'ecmaVersion': 2020, 'source_type': 'module'}
                    },
                    'prettier': {
                        'semi': True,
                        'trailing_comma': 'es5',
                        'single_quote': True,
                        'print_width': 80,
                        'tab_width': 2
                    }
                }
            },
            'TypeScript': {
                'formatters': ['prettier', 'eslint --fix'],
                'linters': ['eslint', '@typescript-eslint/eslint-plugin'],
                'test_frameworks': ['jest', 'mocha', 'jasmine', 'ava', 'vitest'],
                'suggested_config': {
                    'eslint': {
                        'extends': ['eslint:recommended', '@typescript-eslint/recommended', 'plugin:prettier/recommended'],
                        'parser': '@typescript-eslint/parser',
                        'plugins': ['@typescript-eslint']
                    },
                    'prettier': {
                        'semi': True,
                        'trailing_comma': 'es5',
                        'single_quote': True,
                        'print_width': 80,
                        'tab_width': 2
                    }
                }
            },
            'Java': {
                'formatters': ['google-java-format', 'prettier --parser java'],
                'linters': ['checkstyle', 'findbugs', 'pmd', 'spotbugs'],
                'test_frameworks': ['junit', 'testng', 'mockito'],
                'suggested_config': {}
            },
            'C++': {
                'formatters': ['clang-format'],
                'linters': ['cppcheck', 'cpplint', 'clang-tidy'],
                'test_frameworks': ['googletest', 'catch2', 'doctest'],
                'suggested_config': {
                    'clang-format': {
                        'BasedOnStyle': 'Google',
                        'IndentWidth': 2,
                        'TabWidth': 2,
                        'UseTab': 'Never'
                    }
                }
            },
            'Go': {
                'formatters': ['gofmt', 'goimports'],
                'linters': ['golangci-lint', 'golint', 'govet'],
                'test_frameworks': ['testing', 'testify'],
                'suggested_config': {}
            },
            'Rust': {
                'formatters': ['rustfmt'],
                'linters': ['clippy'],
                'test_frameworks': ['cargo test'],
                'suggested_config': {}
            },
            'PHP': {
                'formatters': ['php-cs-fixer', 'pint'],
                'linters': ['phpstan', 'psalm', 'phpmd', 'phpcs'],
                'test_frameworks': ['phpunit', 'codeception'],
                'suggested_config': {}
            },
            'Ruby': {
                'formatters': ['rubocop --auto-correct'],
                'linters': ['rubocop', 'brakeman', 'reek'],
                'test_frameworks': ['rspec', 'minitest'],
                'suggested_config': {
                    'rubocop': {
                        'inherit_gem': {'rubocop-performance': ['config/default.yml']},
                        'AllCops': {
                            'TargetRubyVersion': 2.7
                        }
                    }
                }
            }
        }

    def detect_language_from_file(self, file_path: str) -> str:
        """Detect language based on file extension and special filenames."""
        path_obj = Path(file_path)
        ext = path_obj.suffix.lower()
        filename = path_obj.name.lower()
        
        # Check if it's a special filename that indicates language
        if filename in self.filename_map:
            return self.filename_map[filename]
        
        # Check the extension
        if ext in self.extension_map:
            return self.extension_map[ext]
        
        return 'Unknown'

    def analyze_file_content(self, file_path: str, sample_size: int = 1024) -> str:
        """Analyze file content to detect language (for files with no clear extension)."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                sample = f.read(sample_size)

                # Look for language-specific patterns
                patterns = {
                    'Python': [
                        r'import\s+\w+', r'from\s+\w+\s+import', r'def\s+\w+\s*\(', 
                        r'class\s+\w+\s*:', r'if\s+__name__\s*==\s*[\'"]__main__[\'"]'
                    ],
                    'JavaScript': [
                        r'function\s+\w+\s*\(', r'const\s+\w+\s*=', r'let\s+\w+\s*=',
                        r'var\s+\w+\s*=', r'import\s+.+\s+from', r'export\s+', r'console\.',
                        r'require\s*\('
                    ],
                    'TypeScript': [
                        r':\s*(string|number|boolean|any|void)', 
                        r'interface\s+\w+', r'type\s+\w+', r'enum\s+\w+',
                        r'implements\s+\w+', r'namespace\s+\w+'
                    ],
                    'Java': [
                        r'public\s+class\s+\w+', r'private\s+class\s+\w+', r'import\s+java\.',
                        r'package\s+[\w.]+;', r'public\s+static\s+void\s+main'
                    ],
                    'C++': [
                        r'#include\s+<.*>', r'#include\s+"[^"]*"', r'int\s+main\s*\(',
                        r'using\s+namespace\s+std;',
                        r'std::\w+', r'cout\s*<<', r'cin\s*>>'
                    ],
                    'Go': [
                        r'package\s+\w+', r'import\s*\(', r'func\s+\w+\s*\(',
                        r'fmt\.', r'go\s+func'
                    ],
                    'Rust': [
                        r'use\s+std::', r'fn\s+main\s*\(', r'fn\s+\w+\s*\(',
                        r'mod\s+\w+;', r'extern\s+crate'
                    ],
                    'PHP': [
                        r'<\?php', r'function\s+\w+\s*\(', r'\$\w+\s*=', 
                        r'use\s+function', r'use\s+const'
                    ],
                    'Ruby': [
                        r'def\s+\w+', r'require\s+[\'"][^\'"]*[\'"]', r'include\s+\w+',
                        r'class\s+<<\s*self', r'attr_accessor', r'end\s*$', 
                    ],
                    'Shell': [
                        r'^#!.*(/bash|/sh|/zsh)', r'echo\s+', r'export\s+\w+=',
                        r'\$\w+', r'\$\{[^}]+\}', r'if\s+\[', r'fi\s*$', 
                        r'for\s+\w+\s+in', r'done\s*$'
                    ]
                }

                for lang, lang_patterns in patterns.items():
                    for pattern in lang_patterns:
                        if re.search(pattern, sample, re.MULTILINE | re.IGNORECASE):
                            return lang
        except Exception:
            pass
            
        return 'Unknown'

    def scan_project(self, project_path: str) -> Dict[str, List[str]]:
        """Scan the entire project to detect all languages and files."""
        project_path = Path(project_path)
        language_files = defaultdict(list)
        
        # Extensions to ignore (non-source files)
        ignore_extensions = {
            '.log', '.tmp', '.bak', '.old', '.orig', '.rej', '.swp', '.swo',
            '.zip', '.tar', '.gz', '.rar', '.7z', '.jar', '.war', '.ear',
            '.img', '.iso', '.dmg', '.pdf', '.doc', '.docx', '.xls',
            '.xlsx', '.ppt', '.pptx', '.odt', '.ods', '.odp', '.jpg',
            '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico',
            '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm',
            '.wav', '.ogg', '.exe', '.dll', '.so', '.dylib', '.bin', '.out',
            '.obj', '.o', '.a', '.lib', '.pdb', '.ilk', '.apk', '.class',
            '.pyc', '.pyo', '.egg', '.whl', '.lock'
        }
        
        # Directories to ignore
        ignore_dirs = {
            '.git', '.svn', '.hg', '__pycache__', 'node_modules', 
            'vendor', 'target', 'build', 'dist', 'release', 'debug',
            '.vscode', '.idea', '.gradle', '.nuget', 'Pods', 'build',
            'dist', 'site-packages', '.pytest_cache', '.mypy_cache',
            'venv', 'env', '.env', 'ENV', '.venv', 'dist', 'site-packages',
            '__pycache__', '.pytest_cache', '.ruff_cache', '.coverage', 
            'htmlcov', '.hypothesis', '.tox', '.eggs', 'pip-wheel-metadata',
            '.serverless', '.terraform', '.netlify', '.nyc_output', 'lcov-report'
        }
        
        for root, dirs, files in os.walk(project_path):
            # Remove ignored directories from consideration
            dirs[:] = [d for d in dirs if d not in ignore_dirs]

            for file in files:
                file_path = Path(root) / file
                file_ext = file_path.suffix.lower()

                # Skip files with ignored extensions
                if file_ext in ignore_extensions:
                    continue

                # Skip hidden files
                if file.startswith('.'):
                    continue

                # Detect language
                language = self.detect_language_from_file(str(file_path))

                # If undetermined by extension, analyze content
                if language == 'Unknown':
                    language = self.analyze_file_content(str(file_path))

                if language != 'Unknown':
                    relative_path = str(file_path.relative_to(project_path))
                    language_files[language].append(relative_path)

        return dict(language_files)

    def get_tool_recommendations(self, detected_languages: List[str]) -> Dict[str, List[str]]:
        """Get tool recommendations for the detected languages."""
        recommendations = {
            'formatters': [],
            'linters': [],
            'test_frameworks': []
        }
        
        for lang in detected_languages:
            if lang in self.tool_recommendations:
                lang_tools = self.tool_recommendations[lang]
                
                # Add formatters
                if 'formatters' in lang_tools:
                    for formatter in lang_tools['formatters']:
                        if formatter not in recommendations['formatters']:
                            recommendations['formatters'].append(formatter)
                
                # Add linters
                if 'linters' in lang_tools:
                    for linter in lang_tools['linters']:
                        if linter not in recommendations['linters']:
                            recommendations['linters'].append(linter)
                
                # Add test frameworks
                if 'test_frameworks' in lang_tools:
                    for test_framework in lang_tools['test_frameworks']:
                        if test_framework not in recommendations['test_frameworks']:
                            recommendations['test_frameworks'].append(test_framework)
        
        return recommendations

    def generate_report(self, project_path: str) -> str:
        """Generate a comprehensive language detection and tool recommendation report."""
        language_files = self.scan_project(project_path)
        
        if not language_files:
            return "**Language Detection Report**\n\nNo source files detected in the project."
        
        report_lines = ["**Language Detection & Tool Recommendation Report**", "="*55]
        total_files = sum(len(files) for files in language_files.values())
        report_lines.append(f"Total source files analyzed: {total_files}\n")
        
        for lang, files in language_files.items():
            report_lines.append(f"**{lang}** ({len(files)} files):")
            
            # Show first 5 files for brevity
            for file_path in files[:5]:
                report_lines.append(f"  - {file_path}")
            
            # If there are more files, indicate how many more
            if len(files) > 5:
                report_lines.append(f"  ... and {len(files) - 5} more files")
            
            report_lines.append("")  # Empty line for spacing
        
        # Get tool recommendations
        detected_langs = list(language_files.keys())
        tools = self.get_tool_recommendations(detected_langs)
        
        if tools['formatters']:
            report_lines.append("**Suggested Formatters:**")
            for fmt in tools['formatters']:
                report_lines.append(f"  - {fmt}")
            report_lines.append("")
        
        if tools['linters']:
            report_lines.append("**Suggested Linters:**")
            for linter in tools['linters']:
                report_lines.append(f"  - {linter}")
            report_lines.append("")
        
        if tools['test_frameworks']:
            report_lines.append("**Suggested Test Frameworks:**")
            for test_fw in tools['test_frameworks']:
                report_lines.append(f"  - {test_fw}")
            report_lines.append("")
        
        report_lines.append(f"Languages detected: {', '.join(detected_langs)}")
        
        return '\n'.join(report_lines)