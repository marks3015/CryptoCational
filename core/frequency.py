"""
Frequency analysis module.

This module manages the loading and processing of expected and
observed letter frequencies.
"""

import json
import os
from typing import Dict, Optional, List, Any, cast
from collections import Counter
from .utils import get_resource_path


# Cache for loaded frequencies
_frequency_cache: Optional[Dict[str, Any]] = None


def get_data_path() -> str:
    """
    Returns the absolute path to the frequency file.
    
    Returns:
        Absolute path to letter_frequencies.json
    """
    return get_resource_path('data/letter_frequencies.json')


def load_frequencies() -> Dict[str, Any]:
    """
    Loads expected frequencies from the JSON file.
    
    Uses cache to avoid repeated file reads.
    
    Returns:
        Dictionary with frequencies by language
        
    Raises:
        FileNotFoundError: If the file is not found
        json.JSONDecodeError: If the file is malformed
    """
    global _frequency_cache
    
    if _frequency_cache is not None:
        return _frequency_cache  # type: ignore
    
    filepath = get_data_path()
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            _frequency_cache = cast(Dict[str, Any], json.load(f))
        return _frequency_cache
    except FileNotFoundError:
        raise FileNotFoundError(f"Frequency file not found: {filepath}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing frequency JSON: {e}")


def get_language_frequencies(language: str) -> Dict[str, float]:
    """
    Gets expected letter frequencies for a language.
    
    Args:
        language: Language code ('pt' or 'en')
        
    Returns:
        Dictionary {letter: percentage_frequency}
        
    Raises:
        ValueError: If the language is not supported
    """
    data = load_frequencies()
    
    language = language.lower()
    
    if language not in data:
        raise ValueError(f"Language '{language}' not supported. Use 'pt' or 'en'.")
    
    return data[language]['letter_frequency']


def get_supported_languages() -> List[str]:
    """
    Returns the list of supported languages.
    
    Returns:
        List of language codes (e.g., ['pt', 'en'])
    """
    data = load_frequencies()
    return list(data.keys())


def calculate_frequencies(text: str) -> Dict[str, float]:
    """
    Calculates the observed frequency of letters in a text.
    
    Args:
        text: Text to be analyzed (A-Z only)
        
    Returns:
        Dictionary {letter: percentage_frequency}
    """
    if not text:
        return {chr(i): 0.0 for i in range(ord('A'), ord('Z') + 1)}
    
    # Count occurrences
    counter = Counter(text.upper())
    total = len(text)
    
    # Calculate percentages
    frequencies = {}
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        count = counter.get(letter, 0)
        frequencies[letter] = (count / total) * 100
    
    return frequencies


def get_sorted_frequencies(frequencies: Dict[str, float], 
                           descending: bool = True) -> List[tuple]:
    """
    Sorts frequencies by value.
    
    Args:
        frequencies: Frequency dictionary
        descending: True for descending order (most frequent first)
        
    Returns:
        Sorted list of (letter, frequency) tuples
    """
    return sorted(frequencies.items(), key=lambda x: x[1], reverse=descending)


def detect_language(text: str) -> str:
    """
    Tries to detect the text's language based on frequency analysis.
    
    This is a simple implementation that compares the text's IC
    with typical ICs for each language.
    
    Args:
        text: Text to be analyzed
        
    Returns:
        Most probable language code ('pt' or 'en')
    """
    from .utils import estimate_ic
    
    # Typical ICs (approximate)
    ic_values = {
        'pt': 0.074,
        'en': 0.067
    }
    
    text_ic = estimate_ic(text)
    
    # Finds the language with the closest IC
    closest_lang = min(ic_values.keys(), 
                      key=lambda lang: abs(ic_values[lang] - text_ic))
    
    return closest_lang