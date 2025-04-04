# MCPS: Model Context Protocol Servers

A comprehensive set of MCP (Model Context Protocol) servers for filesystem and code manipulation. This project provides tools that allow Large Language Models (LLMs) to interact with the filesystem, Python code analysis, and LaTeX document processing.

## Overview

MCPS is a collection of specialized MCP servers that extend the capabilities of LLMs by providing them with tools to:

1. **Manipulate the filesystem** - read, write, and manage files and directories
2. **Analyze Python code** - extract imports, function definitions, and perform linting
3. **Process TeX documents** - compile and validate LaTeX files

All code in this project was created by Claude 3.7 with extended thinking and using MCP (Model Context Protocol).

## Modules

### 1. Filesystem MCP (`mcp_fs.py`)

Provides a comprehensive set of tools for filesystem operations:

- List directory contents
- Read and write files
- Create and manage directories
- Move and copy files
- Get file and directory information
- Search files by name or content
- Process text files with different encodings
- Batch file operations

### 2. Python Analysis MCP (`mcp_python.py`)

Tools for analyzing Python code files:

- Extract import statements
- Identify function definitions with signatures and line numbers
- Check code with ruff linter
- Perform comprehensive file analysis including linting, imports, and function detection

### 3. TeX Document MCP (`mcp_tex.py`)

Tools for working with LaTeX documents:

- Compile TeX files to PDF using pdflatex
- Validate LaTeX documents and identify errors and warnings
- Extract detailed diagnostics from log files

## License

[License information]

---

*This project demonstrates the power of LLMs with MCP to create tools that extend their capabilities to interact with external systems like filesystems and code analysis tools.*