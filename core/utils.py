import os
import sys
import re
from typing import List


def get_resource_path(relative_path: str) -> str:
    """
    Get the absolute path to a resource, works for dev and for PyInstaller.
    
    Args:
        relative_path: The relative path to the resource from the project root.
        
    Returns:
        The absolute path to the resource.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # If not running in PyInstaller, use the project root
        # This assumes utils.py is in core/
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return os.path.abspath(os.path.join(base_path, relative_path))


def chunk_text(text: str, chunk_size: int = 5) -> str:
    """
    Divides text into groups of a specified size for better readability.
    
    Args:
        text: Text to be divided
        chunk_size: Size of each group (default: 5)
        
    Returns:
        Text divided into groups separated by space
    """
    if not text:
        return ""
    
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    return ' '.join(chunks)


def remove_whitespace(text: str) -> str:
    """
    Removes all whitespace from the text.
    
    Args:
        text: Input text
        
    Returns:
        Text without spaces
    """
    return re.sub(r'\s+', '', text)


def format_key_for_display(key: str, group_size: int = 4) -> str:
    """
    Formats a key for display, grouping it into blocks.
    
    Args:
        key: Key to be formatted
        group_size: Group size
        
    Returns:
        Formatted key
    """
    if not key:
        return ""
    
    chunks = [key[i:i + group_size] for i in range(0, len(key), group_size)]
    return ' '.join(chunks)


def estimate_ic(text: str) -> float:
    """
    Calculates the Index of Coincidence (IC) of a text.
    
    The IC is useful for estimating the key size in attacks.
    
    Args:
        text: Normalized text (A-Z only)
        
    Returns:
        Value of the Index of Coincidence
    """
    if len(text) < 2:
        return 0.0
    
    # Counts the frequency of each letter
    frequencies = {}
    for char in text:
        frequencies[char] = frequencies.get(char, 0) + 1
    
    # Calculates IC
    n = len(text)
    ic_sum = sum(f * (f - 1) for f in frequencies.values())
    ic = ic_sum / (n * (n - 1)) if n > 1 else 0.0
    
    return ic


def split_text_into_columns(text: str, num_columns: int) -> List[str]:
    """
    Splits the text into columns for frequency analysis.
    
    Useful for analyzing each key position in the attack.
    
    Args:
        text: Ciphertext
        num_columns: Number of columns (estimated key size)
        
    Returns:
        List of strings, each representing a column
    """
    if not text or num_columns <= 0:
        return []
    
    columns = ['' for _ in range(num_columns)]
    
    for i, char in enumerate(text):
        column_index = i % num_columns
        columns[column_index] += char
    
    return columns