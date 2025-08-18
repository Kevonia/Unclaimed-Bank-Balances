from pathlib import Path

def get_project_root() -> Path:
    """Get the root directory of the project."""
    return Path(__file__).parent.parent.parent

def  check_if_file_exists(filepath):
    """
    Check if a file exists at the given filepath.

    parameter filepath: str - The path to the file to check.
    
    return: bool - True if the file exists, False otherwise.
    """
    file = Path(filepath)
    return file.is_file()
