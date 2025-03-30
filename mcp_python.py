#!/usr/bin/env python3
"""
Python-specific MCP (Model Context Protocol) Server Tools

This module provides tools for an LLM to analyze Python code files.
"""

import json
import re
import subprocess
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

# Initialize MCP
mcp = FastMCP("mcp-python")


@mcp.tool()
def get_python_imports(file_path: str) -> list[str]:
    """
    Extract all import statements from a Python file.

    Args:
        file_path: Path to the Python file

    Returns:
        List of import statements found in the file

    Example:
        >>> get_python_imports('/home/user/project/app.py')
        [
            "import os",
            "import sys",
            "from datetime import datetime",
            "from pathlib import Path"
        ]

        >>> get_python_imports('/home/user/project/utils.py')
        [
            "import json",
            "from typing import List, Dict, Any",
            "from collections import defaultdict"
        ]
    """
    path = Path(file_path).expanduser().resolve()

    if not path.exists() or not path.is_file():
        raise ValueError(f"File does not exist: {file_path}")

    if not path.suffix.lower() == ".py":
        raise ValueError(f"Not a Python file: {file_path}")

    import_pattern = re.compile(
        r"^(?:from\s+\S+\s+import\s+\S+|import\s+\S+)", re.MULTILINE
    )

    try:
        with open(path) as f:
            content = f.read()
            matches = import_pattern.findall(content)
            return matches
    except Exception as e:
        # Fixed B904: Added 'from e' to properly chain exceptions
        raise ValueError(f"Error extracting imports: {str(e)}") from e


@mcp.tool()
def extract_function_names(file_path: str) -> list[dict[str, Any]]:
    """
    Extract function definitions from a Python file.

    Args:
        file_path: Path to the Python file

    Returns:
        List of function names with line numbers

    Example:
        >>> extract_function_names('/home/user/project/main.py')
        [
            {
                "function_name": "initialize_app",
                "line_number": 10,
                "signature": "def initialize_app(config_path, log_level='info'):"
            },
            {
                "function_name": "process_data",
                "line_number": 25,
                "signature": "def process_data(input_file, output_dir):"
            }
        ]

        >>> extract_function_names('/home/user/project/utils.py')
        [
            {
                "function_name": "parse_config",
                "line_number": 5,
                "signature": "def parse_config(config_file):"
            },
            {
                "function_name": "validate_input",
                "line_number": 15,
                "signature": "def validate_input(data):"
            }
        ]
    """
    path = Path(file_path).expanduser().resolve()

    if not path.exists() or not path.is_file():
        raise ValueError(f"File does not exist: {file_path}")

    if not path.suffix.lower() == ".py":
        raise ValueError(f"Not a Python file: {file_path}")

    function_pattern = re.compile(r"^def\s+([^\s\(]+)\s*\(", re.MULTILINE)

    functions = []
    try:
        with open(path) as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                match = function_pattern.search(line)
                if match:
                    functions.append(
                        {
                            "function_name": match.group(1),
                            "line_number": i + 1,
                            "signature": line.strip(),
                        }
                    )
        return functions
    except Exception as e:
        # Fixed B904: Added 'from e' to properly chain exceptions
        raise ValueError(f"Error extracting function names: {str(e)}") from e


@mcp.tool()
def check_python_with_ruff(file_path: str, fix: bool = False) -> dict[str, Any]:
    """
    Check a Python file with the ruff linter using uv, if available.

    Args:
        file_path: Path to the Python file to check
        fix: If True, attempt to fix issues automatically

    Returns:
        Dictionary containing linting results and execution info

    Example:
        >>> check_python_with_ruff('/home/user/project/app.py')
        {
            "success": True,
            "has_issues": False,
            "issues_count": 0,
            "formatted_output": "",
            "command_used": "uv run ruff check /home/user/project/app.py"
        }

        >>> check_python_with_ruff('/home/user/project/buggy.py')
        {
            "success": True,
            "has_issues": True,
            "issues_count": 3,
            "formatted_output": "app.py:10:1: F401 'os' imported but unused...",
            "command_used": "uv run ruff check /home/user/project/buggy.py"
        }
    """
    file_path = Path(file_path).expanduser().resolve()

    if not file_path.exists() or not file_path.is_file():
        raise ValueError(f"File does not exist: {file_path}")

    if not file_path.suffix.lower() == ".py":
        raise ValueError(f"Not a Python file: {file_path}")

    # Get the starting directory (where the file is located)
    current_dir = file_path.parent
    project_dir = current_dir

    # Check if uv is being used in the project by looking for pyproject.toml and uv.lock
    uv_project_found = False

    # Try to find pyproject.toml in the current or parent directories
    while current_dir != current_dir.parent:  # Stop at filesystem root
        pyproject_path = current_dir / "pyproject.toml"
        uv_lock_path = current_dir / "uv.lock"

        # If either pyproject.toml exists or uv.lock exists, consider it a uv project
        if pyproject_path.exists() or uv_lock_path.exists():
            uv_project_found = True
            project_dir = current_dir
            break

        current_dir = current_dir.parent

    if not uv_project_found:
        # Fixed E501: Split the long line into multiple lines for readability
        error_msg = (
            "No Python project found (missing pyproject.toml or uv.lock) "
            "in current or parent directories"
        )
        return {
            "success": False,
            "error": error_msg,
            "command_used": None,
            "has_issues": None,
            "issues_count": None,
            "formatted_output": None,
        }

    # Check if uv command is available
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            return {
                "success": False,
                "error": "uv command not available",
                "command_used": "uv --version",
                "has_issues": None,
                "issues_count": None,
                "formatted_output": None,
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error checking for uv: {str(e)}",
            "command_used": "uv --version",
            "has_issues": None,
            "issues_count": None,
            "formatted_output": None,
        }

    # Construct the ruff command
    cmd = ["uv", "run", "ruff", "check"]

    # Add options based on parameters
    if fix:
        cmd.append("--fix")
    cmd.extend(["--output-format", "json"])

    # Add the file path
    cmd.append(str(file_path))

    # Run the ruff command
    try:
        result = subprocess.run(
            cmd, cwd=str(project_dir), capture_output=True, text=True
        )

        # Parse the output
        if result.stdout:
            try:
                issues = json.loads(result.stdout)
                issues_count = len(issues)
            except json.JSONDecodeError:
                issues_count = None
        else:
            # Count the issues based on newlines in the output
            issues_count = (
                len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
            )

        # Check if there are issues
        has_issues = (
            issues_count > 0 if issues_count is not None else result.returncode != 0
        )

        return {
            "success": True,
            "has_issues": has_issues,
            "issues_count": issues_count,
            "formatted_output": result.stdout,
            "raw_errors": result.stderr if result.stderr else None,
            "command_used": " ".join(cmd),
            "exit_code": result.returncode,
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error running ruff: {str(e)}",
            "command_used": " ".join(cmd),
            "has_issues": None,
            "issues_count": None,
            "formatted_output": None,
        }


@mcp.tool()
def analyze_python_file(file_path: str) -> dict[str, Any]:
    """
    Perform a comprehensive analysis of a Python file including imports,
    function definitions, and linting (if available).

    Args:
        file_path: Path to the Python file to analyze

    Returns:
        Dictionary containing analysis results

    Example:
        >>> analyze_python_file('/home/user/project/app.py')
        {
            "file_path": "/home/user/project/app.py",
            "imports": ["import os", "import sys", "from pathlib import Path"],
            "functions": [
                {"function_name": "main", "line_number": 5, "signature": "def main():"}
            ],
            "linting": {
                "success": True,
                "has_issues": False,
                "issues_count": 0
            },
            "lines_count": 42,
            "is_package": False
        }
    """
    file_path = Path(file_path).expanduser().resolve()

    if not file_path.exists() or not file_path.is_file():
        raise ValueError(f"File does not exist: {file_path}")

    if not file_path.suffix.lower() == ".py":
        raise ValueError(f"Not a Python file: {file_path}")

    # Get imports
    try:
        imports = get_python_imports(str(file_path))
    except Exception as e:
        imports = {"error": str(e)}

    # Get functions
    try:
        functions = extract_function_names(str(file_path))
    except Exception as e:
        functions = {"error": str(e)}

    # Try linting
    try:
        linting = check_python_with_ruff(str(file_path))
    except Exception as e:
        linting = {"success": False, "error": str(e)}

    # Count lines
    try:
        with open(file_path) as f:
            lines = f.readlines()
            lines_count = len(lines)
    except OSError:
        lines_count = None

    # Check if file is part of a package
    is_package = False
    init_file = file_path.parent / "__init__.py"
    if init_file.exists() and init_file.is_file():
        is_package = True

    # Compile final results
    # Fixed E501: Breaking up dictionary creation to avoid long line
    result = {
        "file_path": str(file_path),
        "imports": imports,
        "functions": functions,
        "linting": linting,
        "lines_count": lines_count,
        "is_package": is_package,
    }
    
    return result


# Main execution
if __name__ == "__main__":
    pass
