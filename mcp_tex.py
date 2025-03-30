#!/usr/bin/env python3
"""
TeX MCP (Model Context Protocol) Server for Resume/CV Manipulation

This server provides specialized tools for modifying and transforming TeX documents,
specifically focused on resume and CV formatting tasks.
"""

import re
import subprocess
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

# Initialize MCP
mcp = FastMCP("mcp-tex")


@mcp.tool()
def compile_tex_to_pdf(tex_path: str) -> str:
    """
    Compile a TeX file to PDF using pdflatex.

    Args:
        tex_path: Path to the TeX file

    Returns:
        Path to the generated PDF file

    Example:
        >>> compile_tex_to_pdf('/home/o/junk/cv/cv.tex')
        '/home/o/junk/cv/cv.pdf'
    """
    tex_file = Path(tex_path).expanduser().resolve()

    if not tex_file.exists():
        raise ValueError(f"TeX file does not exist: {tex_path}")

    output_dir = tex_file.parent

    # Get base filename without extension
    base_name = tex_file.stem

    # Build the pdflatex command
    # -interaction=nonstopmode: Don't stop on errors
    # -output-directory: Specify output directory
    cmd = f"pdflatex -interaction=nonstopmode -output-directory={output_dir} {tex_file}"

    try:
        # Run pdflatex (twice to resolve references)
        # FIXED: Replaced os.system with subprocess.run for better practice
        subprocess.run(cmd, check=True, shell=True)
        subprocess.run(cmd, check=True, shell=True)

        # Path to the generated PDF
        pdf_path = output_dir / f"{base_name}.pdf"

        if pdf_path.exists():
            return str(pdf_path)
        else:
            raise ValueError("PDF file was not generated. Check TeX file for errors.")
    except Exception as e:
        # Fixed B904: Added 'from e' to properly chain exceptions
        raise ValueError(f"Error compiling TeX file: {str(e)}") from e


@mcp.tool()
def validate_tex(tex_path: str) -> dict[str, Any]:
    """
    Validate a LaTeX file for correctness and return all warnings and errors.

    Args:
        tex_path: Path to the LaTeX file to validate

    Returns:
        Dictionary containing warnings and errors found in the LaTeX file

    Example:
        >>> validate_tex('/home/o/junk/cv/cv.tex')
        {
            "warnings": [
                {
                    "message": "Underfull \\hbox (badness 10000) in paragraph at lines 10--11", 
                    "lines": [10, 11]
                },
                {
                    "message": "Overfull \\hbox (12.34pt too wide) in paragraph at lines 15--16", 
                    "lines": [15, 16]
                }
            ],
            "errors": [
                {"message": "Undefined control sequence \\somecommand", "line": 20},
                {"message": "Missing $ inserted", "line": 25}
            ],
            "summary": "2 warnings, 2 errors found",
            "log_file": "/home/o/junk/cv/cv.log",
            "success": false
        }
    """
    try:
        tex_file = Path(tex_path).expanduser().resolve()

        if not tex_file.exists():
            return {"error": f"File {tex_path} does not exist"}

        if not str(tex_file).endswith('.tex'):
            return {"error": f"File {tex_path} is not a LaTeX file"}

        # Get the directory and filename of the tex file
        tex_dir = tex_file.parent
        tex_basename = tex_file.stem

        # Run LaTeX in draft mode to check for errors without generating a PDF
        # Run directly in the directory where the .tex file is located
        process = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-draftmode", tex_file.name],
            cwd=tex_dir,
            capture_output=True,
            text=True,
        )

        log_path = tex_dir / f"{tex_basename}.log"
        output = ""

        # Read the log file for more detailed information
        if log_path.exists():
            with open(log_path, encoding='utf-8', errors='replace') as log_file:
                output = log_file.read()
        else:
            output = process.stdout

        # Extract warnings and errors from the output
        warnings = []
        errors = []

        # Process the log for warnings
        warning_patterns = [
            # Underfull/Overfull boxes
            (
                r'((?:Underfull|Overfull) \\[^(]*) in paragraph at lines (\d+)--(\d+)',
                lambda m: {"message": m.group(1), "lines": [int(m.group(2)), int(m.group(3))]}
            ),
            # LaTeX warnings with line numbers
            (
                r'LaTeX Warning: ([^.]*) on (input )?line (\d+)',
                lambda m: {
                    "message": f"LaTeX Warning: {m.group(1)}",
                    "line": int(m.group(3))
                }
            ),
            # Package warnings with line numbers
            (
                r'Package ([^\s]+) Warning: ([^.]*) on (input )?line (\d+)',
                lambda m: {
                    "message": f"Package {m.group(1)} Warning: {m.group(2)}",
                    "line": int(m.group(4))
                }
            ),
            # Other warnings without line numbers
            (
                r'(?:LaTeX|Package [^\s]+) Warning: ([^.]*)',
                lambda m: {"message": m.group(0)}
            )
        ]

        for pattern, extract_func in warning_patterns:
            for match in re.finditer(pattern, output, re.MULTILINE):
                warning = extract_func(match)
                # Avoid duplicates
                if warning not in warnings:
                    warnings.append(warning)

        # Process the log for errors
        # First, split the log into chunks at each error (starting with !)
        error_chunks = re.split(r'(!(?:[^!]|$)*)', output)
        for chunk in error_chunks:
            if chunk.startswith('!'):
                # Extract the error message (first line)
                error_lines = chunk.split('\n')
                error_msg = error_lines[0].strip()
                error_dict = {"message": error_msg}

                # Look for a line number
                line_match = re.search(r'l\.(\d+)', chunk)
                if line_match:
                    error_dict["line"] = int(line_match.group(1))

                errors.append(error_dict)

        # Return log file path only if it exists
        log_file_path = str(log_path) if log_path.exists() else None

        # Fixed line too long (E501) by breaking the string initialization over multiple lines
        return {
            "warnings": warnings,
            "errors": errors,
            "summary": f"{len(warnings)} warnings, {len(errors)} errors found",
            "log_file": log_file_path,
            "success": len(errors) == 0
        }

    except Exception as e:
        return {"error": f"Failed to validate LaTeX file: {str(e)}"}


# Main execution
if __name__ == "__main__":
    pass
