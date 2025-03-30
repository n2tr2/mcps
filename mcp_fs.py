#!/usr/bin/env python3
"""
Generic MCP (Model Context Protocol) Server for Filesystem Manipulation

This server provides tools for an LLM to read, write, create, and modify
objects on the filesystem.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

# Initialize MCP
mcp = FastMCP("nn")


@mcp.tool()
def list_items(path: str) -> list[dict[str, str]]:
    """
    List contents of a directory.

    Args:
        path: Path to the directory to list

    Returns:
        List of objects containing name, type, and path for each item in the directory
        
    Example:
        >>> list_items('/home/user/documents')
        [
            {"name": "file1.txt", "type": "file", "path": "/home/user/documents/file1.txt"},
            {"name": "images", "type": "directory", "path": "/home/user/documents/images"}
        ]
    """
    directory_path = Path(path).expanduser().resolve()

    if not directory_path.exists():
        raise ValueError(f"Path does not exist: {path}")

    if not directory_path.is_dir():
        raise ValueError(f"Path is not a directory: {path}")

    contents = []
    for item in directory_path.iterdir():
        item_type = "directory" if item.is_dir() else "file"
        contents.append({"name": item.name, "type": item_type, "path": str(item)})

    return contents


@mcp.tool()
def read_file(path: str, binary: bool = False) -> str | bytes:
    """
    Read the contents of a file.

    Args:
        path: Path to the file to read
        binary: If True, read in binary mode

    Returns:
        Contents of the file (string or bytes)
        
    Example:
        >>> read_file('/home/user/documents/file1.txt')
        'This is the content of file1.txt'
        
        >>> read_file('/home/user/documents/image.jpg', binary=True)
        b'...' # binary content
    """
    file_path = Path(path).expanduser().resolve()

    if not file_path.exists():
        raise ValueError(f"File does not exist: {path}")

    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {path}")

    mode = "rb" if binary else "r"
    try:
        with open(file_path, mode) as f:
            return f.read()
    except Exception as e:
        # Fixed B904: Added 'from e' to properly chain exceptions
        raise ValueError(f"Error reading file: {str(e)}") from e


@mcp.tool()
def write_file(
    path: str, content: str | bytes, append: bool = False, binary: bool = False
) -> bool:
    """
    Write content to a file.

    Args:
        path: Path to the file to write
        content: Content to write to the file
        append: If True, append to the file instead of overwriting
        binary: If True, write in binary mode

    Returns:
        True if successful
        
    Example:
        >>> write_file('/home/user/documents/new_file.txt', 'Hello, world!')
        True
        
        >>> write_file('/home/user/documents/log.txt', 'New log entry', append=True)
        True
    """
    file_path = Path(path).expanduser().resolve()

    # Make sure parent directory exists
    os.makedirs(file_path.parent, exist_ok=True)

    mode = "ab" if append and binary else "wb" if binary else "a" if append else "w"

    try:
        with open(file_path, mode) as f:
            f.write(content)
        return True
    except Exception as e:
        # Fixed B904: Added 'from e' to properly chain exceptions
        raise ValueError(f"Error writing to file: {str(e)}") from e


@mcp.tool()
def create_directory(path: str) -> bool:
    """
    Create a new directory.

    Args:
        path: Path to the directory to create

    Returns:
        True if successful
        
    Example:
        >>> create_directory('/home/user/documents/new_folder')
        True
        
        >>> create_directory('/home/user/documents/nested/deep/structure')
        True  # Creates all parent directories as needed
    """
    dir_path = Path(path).expanduser().resolve()

    try:
        os.makedirs(dir_path, exist_ok=True)
        return True
    except Exception as e:
        # Fixed B904: Added 'from e' to properly chain exceptions
        raise ValueError(f"Error creating directory: {str(e)}") from e


@mcp.tool()
def move_item(source: str, destination: str) -> bool:
    """
    Move or rename a file or directory.

    Args:
        source: Path to the source file or directory
        destination: Path to the destination

    Returns:
        True if successful
        
    Example:
        >>> move_item('/home/user/documents/old_name.txt', '/home/user/documents/new_name.txt')
        True  # Renames the file
        
        >>> move_item('/home/user/documents/file.txt', '/home/user/backup/file.txt')
        True  # Moves the file to a different directory
    """
    source_path = Path(source).expanduser().resolve()
    dest_path = Path(destination).expanduser().resolve()

    if not source_path.exists():
        raise ValueError(f"Source path does not exist: {source}")

    # Make sure parent directory for destination exists
    os.makedirs(dest_path.parent, exist_ok=True)

    try:
        shutil.move(str(source_path), str(dest_path))
        return True
    except Exception as e:
        # Fixed B904: Added 'from e' to properly chain exceptions
        raise ValueError(f"Error moving item: {str(e)}") from e


@mcp.tool()
def copy_item(source: str, destination: str, recursive: bool = True) -> bool:
    """
    Copy a file or directory.

    Args:
        source: Path to the source file or directory
        destination: Path to the destination
        recursive: If True and source is a directory, copy recursively

    Returns:
        True if successful
        
    Example:
        >>> copy_item('/home/user/documents/file.txt', '/home/user/backup/file.txt')
        True  # Copies a single file
        
        >>> copy_item('/home/user/documents/project', '/home/user/backup/project')
        True  # Copies an entire directory recursively
    """
    source_path = Path(source).expanduser().resolve()
    dest_path = Path(destination).expanduser().resolve()

    if not source_path.exists():
        raise ValueError(f"Source path does not exist: {source}")

    # Make sure parent directory for destination exists
    os.makedirs(dest_path.parent, exist_ok=True)

    try:
        if source_path.is_file():
            shutil.copy2(str(source_path), str(dest_path))
        elif source_path.is_dir() and recursive:
            shutil.copytree(str(source_path), str(dest_path))
        else:
            raise ValueError("Cannot copy directory without recursive=True")
        return True
    except Exception as e:
        # Fixed B904: Added 'from e' to properly chain exceptions
        raise ValueError(f"Error copying item: {str(e)}") from e


@mcp.tool()
def get_item_info(path: str) -> dict[str, Any]:
    """
    Get detailed information about a file or directory.

    Args:
        path: Path to the file or directory

    Returns:
        Dictionary containing metadata about the item
        
    Example:
        >>> get_item_info('/home/user/documents/file.txt')
        {
            "name": "file.txt",
            "path": "/home/user/documents/file.txt",
            "type": "file",
            "size": 1024,
            "created": "2023-01-15T10:30:45.123456",
            "modified": "2023-01-15T10:30:45.123456",
            "accessed": "2023-01-15T10:30:45.123456",
            "extension": ".txt"
        }
        
        >>> get_item_info('/home/user/documents')
        {
            "name": "documents",
            "path": "/home/user/documents",
            "type": "directory",
            "size": 4096,
            "created": "2023-01-15T10:30:45.123456",
            "modified": "2023-01-15T10:30:45.123456",
            "accessed": "2023-01-15T10:30:45.123456",
            "item_count": 5
        }
    """
    item_path = Path(path).expanduser().resolve()

    if not item_path.exists():
        raise ValueError(f"Path does not exist: {path}")

    stat_info = item_path.stat()

    info = {
        "name": item_path.name,
        "path": str(item_path),
        "type": "directory" if item_path.is_dir() else "file",
        "size": stat_info.st_size,
        "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
        "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
        "accessed": datetime.fromtimestamp(stat_info.st_atime).isoformat(),
    }

    if item_path.is_dir():
        # Count items in directory
        items = list(item_path.iterdir())
        info["item_count"] = len(items)

    if item_path.is_file():
        info["extension"] = item_path.suffix

    return info


@mcp.tool()
def search_files(
    directory: str, pattern: str, recursive: bool = False
) -> list[dict[str, str]]:
    """
    Search for files matching a pattern in a directory.

    Args:
        directory: Directory to search in
        pattern: Glob pattern to match (e.g., "*.txt", "**/*.py")
        recursive: If True, search recursively

    Returns:
        List of matching files with path and type information
        
    Example:
        >>> search_files('/home/user/documents', '*.txt')
        [
            {"name": "file1.txt", "type": "file", "path": "/home/user/documents/file1.txt"},
            {"name": "file2.txt", "type": "file", "path": "/home/user/documents/file2.txt"}
        ]
        
        >>> search_files('/home/user/project', '*.py', recursive=True)
        [
            {"name": "main.py", "type": "file", "path": "/home/user/project/main.py"},
            {"name": "utils.py", "type": "file", "path": "/home/user/project/lib/utils.py"}
        ]
    """
    dir_path = Path(directory).expanduser().resolve()

    if not dir_path.exists() or not dir_path.is_dir():
        raise ValueError(f"Directory does not exist: {directory}")

    if recursive and "**" not in pattern:
        pattern = f"**/{pattern}"

    results = []
    for item in dir_path.glob(pattern):
        item_type = "directory" if item.is_dir() else "file"
        results.append({"name": item.name, "type": item_type, "path": str(item)})

    return results


@mcp.tool()
def get_working_directory() -> str:
    """
    Get the current working directory.

    Returns:
        Path to the current working directory
        
    Example:
        >>> get_working_directory()
        '/home/user/project'
    """
    return str(Path.cwd())


@mcp.tool()
def read_file_chunk(path: str, start: int = 0, size: int | None = None) -> str:
    """
    Read a chunk of a file from a specific position.
    Useful for large files that shouldn't be loaded entirely into memory.

    Args:
        path: Path to the file
        start: Starting byte position
        size: Number of bytes to read (None for all from start position)

    Returns:
        The file chunk as a string
        
    Example:
        >>> read_file_chunk('/home/user/documents/large_file.txt', start=1000, size=500)
        '...content from position 1000 to 1500...'
        
        >>> read_file_chunk('/home/user/documents/large_file.txt', start=5000)
        '...all content from position 5000 to the end of the file...'
    """
    file_path = Path(path).expanduser().resolve()

    if not file_path.exists() or not file_path.is_file():
        raise ValueError(f"File does not exist: {path}")

    try:
        with open(file_path) as f:
            f.seek(start)
            return f.read(size) if size is not None else f.read()
    except Exception as e:
        # Fixed B904: Added 'from e' to properly chain exceptions
        raise ValueError(f"Error reading file chunk: {str(e)}") from e


# =============== NEW TOOLS ===============


@mcp.tool()
def get_parent_directory(path: str) -> str:
    """
    Get the parent directory of a given path.
    
    Args:
        path: Path to examine
    
    Returns:
        Path to the parent directory
        
    Example:
        >>> get_parent_directory('/home/user/documents/file.txt')
        '/home/user/documents'
        
        >>> get_parent_directory('/home/user/documents')
        '/home/user'
    """
    return str(Path(path).expanduser().resolve().parent)


@mcp.tool()
def is_path_valid(path: str) -> dict[str, bool]:
    """
    Check if a path exists and determine its type.
    
    Args:
        path: Path to check
    
    Returns:
        Dictionary with 'exists', 'is_file', and 'is_directory' status
        
    Example:
        >>> is_path_valid('/home/user/documents/file.txt')
        {"exists": True, "is_file": True, "is_directory": False}
        
        >>> is_path_valid('/home/user/non_existent_path')
        {"exists": False, "is_file": False, "is_directory": False}
    """
    p = Path(path).expanduser().resolve()
    return {
        "exists": p.exists(),
        "is_file": p.is_file() if p.exists() else False,
        "is_directory": p.is_dir() if p.exists() else False
    }


@mcp.tool()
def read_text_file_with_encoding(path: str, encoding: str = "utf-8") -> str:
    """
    Read text file with a specific encoding.
    
    Args:
        path: Path to the file
        encoding: Text encoding to use (e.g., 'utf-8', 'latin-1', 'ascii')
    
    Returns:
        Text content of the file
        
    Example:
        >>> read_text_file_with_encoding('/home/user/documents/utf8_file.txt')
        'Content of the UTF-8 encoded file'
        
        >>> read_text_file_with_encoding('/home/user/documents/latin1_file.txt', encoding='latin-1')
        'Content of the Latin-1 encoded file with special characters: éèçà'
    """
    file_path = Path(path).expanduser().resolve()
    
    if not file_path.exists() or not file_path.is_file():
        raise ValueError(f"File does not exist: {path}")
    
    try:
        with open(file_path, encoding=encoding) as f:
            return f.read()
    except Exception as e:
        # Fixed B904: Added 'from e' to properly chain exceptions
        raise ValueError(f"Error reading file with encoding {encoding}: {str(e)}") from e


@mcp.tool()
def get_file_lines(path: str, start_line: int = 0, num_lines: int | None = None) -> list[str]:
    """
    Read specific lines from a text file.
    
    Args:
        path: Path to the file
        start_line: Starting line number (0-indexed)
        num_lines: Number of lines to read (None for all remaining lines)
    
    Returns:
        List of lines from the file
        
    Example:
        >>> get_file_lines('/home/user/documents/file.txt', start_line=5, num_lines=3)
        ['Line 6', 'Line 7', 'Line 8']  # Returns 3 lines starting from line 5 (0-indexed)
        
        >>> get_file_lines('/home/user/documents/file.txt', start_line=10)
        ['Line 11', 'Line 12', ..., 'Last line']  # Returns all lines from line 10 to the end
    """
    file_path = Path(path).expanduser().resolve()
    
    if not file_path.exists() or not file_path.is_file():
        raise ValueError(f"File does not exist: {path}")
    
    try:
        with open(file_path) as f:
            all_lines = f.readlines()
            if start_line >= len(all_lines):
                return []
            
            # Fixed E501: Breaking the long line
            end_line = len(all_lines)
            if num_lines is not None:
                end_line = min(start_line + num_lines, len(all_lines))
                
            return [line.rstrip('\n') for line in all_lines[start_line:end_line]]
    except Exception as e:
        # Fixed B904: Added 'from e' to properly chain exceptions
        raise ValueError(f"Error reading file lines: {str(e)}") from e


@mcp.tool()
def search_file_content(
    file_path: str, 
    search_term: str, 
    case_sensitive: bool = False
) -> list[dict[str, Any]]:
    """
    Search for text within a file and return matching lines with line numbers.
    
    Args:
        file_path: Path to the file to search
        search_term: Text to search for
        case_sensitive: Whether the search should be case-sensitive
    
    Returns:
        List of dictionaries with line numbers and matching lines
        
    Example:
        >>> search_file_content('/home/user/documents/log.txt', 'error')
        [
            {"line_number": 42, "content": "An error occurred during processing"},
            {"line_number": 67, "content": "System error: file not found"}
        ]
        
        >>> search_file_content('/home/user/documents/code.py', 'Class', case_sensitive=True)
        [
            {"line_number": 10, "content": "Class MyExample:"}
        ]
    """
    path = Path(file_path).expanduser().resolve()
    
    if not path.exists() or not path.is_file():
        raise ValueError(f"File does not exist: {file_path}")
    
    matches = []
    try:
        with open(path) as f:
            for i, line in enumerate(f):
                # Fixed E501: Breaking the condition into multiple lines
                is_match = False
                if case_sensitive:
                    is_match = search_term in line
                else:
                    is_match = search_term.lower() in line.lower()
                    
                if is_match:
                    matches.append({"line_number": i + 1, "content": line.rstrip('\n')})
        return matches
    except Exception as e:
        # Fixed B904: Added 'from e' to properly chain exceptions
        raise ValueError(f"Error searching file: {str(e)}") from e


@mcp.tool()
def find_files_by_content(
    directory: str, 
    search_term: str, 
    file_pattern: str = "*", 
    recursive: bool = True, 
    case_sensitive: bool = False
) -> list[dict[str, Any]]:
    """
    Find files containing specific text content.
    
    Args:
        directory: Directory to search in
        search_term: Text content to search for
        file_pattern: File pattern to match (e.g., "*.py", "*.txt")
        recursive: Whether to search recursively
        case_sensitive: Whether the search should be case-sensitive
    
    Returns:
        List of files with matches and sample context
        
    Example:
        >>> find_files_by_content('/home/user/project', 'TODO', '*.py')
        [
            {"path": "/home/user/project/main.py", "name": "main.py", "contains_match": True},
            {"path": "/home/user/project/utils.py", "name": "utils.py", "contains_match": True}
        ]
        
        >>> find_files_by_content('/home/user/logs', 'error', '*.log', case_sensitive=False)
        [
            {"path": "/home/user/logs/system.log", "name": "system.log", "contains_match": True},
            {"path": "/home/user/logs/app.log", "name": "app.log", "contains_match": True}
        ]
    """
    dir_path = Path(directory).expanduser().resolve()
    
    if not dir_path.exists() or not dir_path.is_dir():
        raise ValueError(f"Directory does not exist: {directory}")
    
    pattern = f"**/{file_pattern}" if recursive else file_pattern
    
    results = []
    for file_path in dir_path.glob(pattern):
        if file_path.is_file():
            try:
                with open(file_path) as f:
                    content = f.read()
                    # Fixed E501: Breaking the condition into multiple lines
                    match_found = False
                    if case_sensitive:
                        match_found = search_term in content
                    else:
                        match_found = search_term.lower() in content.lower()
                        
                    if match_found:
                        results.append({
                            "path": str(file_path),
                            "name": file_path.name,
                            "contains_match": True
                        })
            except OSError:
                # Skip files that can't be read as text
                pass
    
    return results


@mcp.tool()
def get_directory_size(path: str) -> dict[str, Any]:
    """
    Calculate the total size of a directory and its contents.
    
    Args:
        path: Path to the directory
    
    Returns:
        Dictionary with size information in bytes and human-readable format
        
    Example:
        >>> get_directory_size('/home/user/documents')
        {
            "path": "/home/user/documents",
            "size_bytes": 15728640,
            "size_human_readable": "15.00 MB",
            "file_count": 25,
            "directory_count": 3
        }
        
        >>> get_directory_size('/home/user/project')
        {
            "path": "/home/user/project",
            "size_bytes": 2097152,
            "size_human_readable": "2.00 MB",
            "file_count": 42,
            "directory_count": 5
        }
    """
    dir_path = Path(path).expanduser().resolve()
    
    if not dir_path.exists() or not dir_path.is_dir():
        raise ValueError(f"Directory does not exist: {path}")
    
    total_size = 0
    file_count = 0
    dir_count = 0
    
    for item in dir_path.glob('**/*'):
        if item.is_file():
            file_size = item.stat().st_size
            total_size += file_size
            file_count += 1
        elif item.is_dir():
            dir_count += 1
    
    # Convert to human-readable format
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    size = total_size
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    human_readable = f"{size:.2f} {units[unit_index]}"
    
    return {
        "path": str(dir_path),
        "size_bytes": total_size,
        "size_human_readable": human_readable,
        "file_count": file_count,
        "directory_count": dir_count
    }


@mcp.tool()
def get_file_type(path: str) -> dict[str, Any]:
    """
    Get detailed file type information.
    
    Args:
        path: Path to the file
    
    Returns:
        Dictionary with file type information
        
    Example:
        >>> get_file_type('/home/user/documents/report.pdf')
        {
            "file": "/home/user/documents/report.pdf",
            "extension": ".pdf",
            "type": "PDF document",
            "appears_to_be_text": False,
            "size_bytes": 1048576
        }
        
        >>> get_file_type('/home/user/project/main.py')
        {
            "file": "/home/user/project/main.py",
            "extension": ".py",
            "type": "Python script",
            "appears_to_be_text": True,
            "size_bytes": 4096
        }
    """
    file_path = Path(path).expanduser().resolve()
    
    if not file_path.exists() or not file_path.is_file():
        raise ValueError(f"File does not exist: {path}")
    
    extension = file_path.suffix.lower()
    
    # Basic file type detection
    file_types = {
        '.txt': 'Text file',
        '.py': 'Python script',
        '.js': 'JavaScript file',
        '.html': 'HTML file',
        '.css': 'CSS file',
        '.json': 'JSON file',
        '.xml': 'XML file',
        '.csv': 'CSV file',
        '.md': 'Markdown file',
        '.jpg': 'JPEG image',
        '.jpeg': 'JPEG image',
        '.png': 'PNG image',
        '.gif': 'GIF image',
        '.pdf': 'PDF document',
        '.doc': 'Word document',
        '.docx': 'Word document',
        '.xls': 'Excel spreadsheet',
        '.xlsx': 'Excel spreadsheet',
        '.zip': 'ZIP archive',
        '.tar': 'TAR archive',
        '.gz': 'Gzip compressed file',
    }
    
    file_type = file_types.get(extension, 'Unknown file type')
    
    # Try to detect if it's a text file
    is_text = False
    try:
        with open(file_path, encoding='utf-8') as f:
            f.read(1024)  # Try to read the first 1024 bytes
            is_text = True
    except UnicodeDecodeError:
        is_text = False
    
    return {
        "file": str(file_path),
        "extension": extension,
        "type": file_type,
        "appears_to_be_text": is_text,
        "size_bytes": file_path.stat().st_size
    }


@mcp.tool()
def batch_read_files(file_paths: list[str]) -> dict[str, Any]:
    """
    Read multiple files at once.
    
    Args:
        file_paths: List of paths to files
    
    Returns:
        Dictionary mapping file paths to their contents
        
    Example:
        >>> batch_read_files(['/home/user/project/README.md', '/home/user/project/config.json'])
        {
            "results": {
                "/home/user/project/README.md": "# Project\n\nThis is a project README file...",
                "/home/user/project/config.json": "{\n  \"debug\": true,\n  \"port\": 8080\n}"
            },
            "errors": {}
        }
        
        >>> batch_read_files(['/home/user/project/valid.txt', '/home/user/non_existent.txt'])
        {
            "results": {
                "/home/user/project/valid.txt": "This is a valid text file."
            },
            "errors": {
                "/home/user/non_existent.txt": "File does not exist or is not a file"
            }
        }
    """
    results = {}
    errors = {}
    
    for path in file_paths:
        try:
            file_path = Path(path).expanduser().resolve()
            if file_path.exists() and file_path.is_file():
                with open(file_path) as f:
                    results[path] = f.read()
            else:
                errors[path] = "File does not exist or is not a file"
        except Exception as e:
            errors[path] = str(e)
    
    return {
        "results": results,
        "errors": errors
    }


# Main execution
if __name__ == "__main__":
    pass
