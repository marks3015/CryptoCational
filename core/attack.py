"""
Vigenère cipher attack module.

This module contains algorithms to break the Vigenère cipher
using frequency analysis and other methods.
"""

import math
from typing import List, Tuple, Optional, Dict
from collections import Counter

from .utils import split_text_into_columns, estimate_ic
from .frequency import get_language_frequencies, calculate_frequencies
from .vigenere import decrypt


def estimate_key_length(ciphertext: str, 
                       max_length: int = 10,
                       language: str = 'pt') -> List[Tuple[int, float]]:
    """
    Estimates the key length using the Index of Coincidence method.
    
    Args:
        ciphertext: Ciphertext
        max_length: Maximum length to test
        language: Expected language of the text
        
    Returns:
        List of (length, probability) tuples sorted by probability
    """
    # Typical ICs for each language
    expected_ic = {
        'pt': 0.074,
        'en': 0.067
    }
    
    target_ic = expected_ic.get(language, 0.07)
    results = []
    
    for key_length in range(1, min(max_length + 1, len(ciphertext) // 2)):
        # Divides the text into columns
        columns = split_text_into_columns(ciphertext, key_length)
        
        # Calculates average IC of the columns
        if columns:
            avg_ic = sum(estimate_ic(col) for col in columns) / len(columns)
            # Score based on proximity to the expected IC
            score = 1.0 - abs(target_ic - avg_ic) / target_ic
            results.append((key_length, max(0.0, score)))
    
    # Sort by descending score
    results.sort(key=lambda x: x[1], reverse=True)
    
    return results


def chi_squared_score(observed: Dict[str, float], 
                      expected: Dict[str, float]) -> float:
    """
    Calculates the chi-squared statistic between observed and expected frequencies.
    
    Ignores letters with very low expected frequency (< 0.3%) to prevent
    the score from being dominated by rare letters.
    
    Args:
        observed: Observed frequencies
        expected: Expected frequencies
        
    Returns:
        Chi-squared value (lower is better)
    """
    score = 0.0
    MIN_FREQ = 0.3  # Ignores letters with expected frequency < 0.3%
    
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        obs = observed.get(letter, 0)
        exp = expected.get(letter, 0)
        
        # Only considers letters with significant expected frequency
        if exp >= MIN_FREQ:
            score += ((obs - exp) ** 2) / exp
    
    return score


def find_best_shift(column: str, language: str = 'pt') -> Tuple[int, float]:
    """
    Finds the best shift for a column using frequency analysis.
    
    Args:
        column: Text of a column
        language: Expected language
        
    Returns:
        Tuple (shift, score) where shift is the number of positions to shift
    """
    expected_freq = get_language_frequencies(language)
    best_shift = 0
    best_score = float('inf')
    
    # Tests all 26 possible shifts
    for shift in range(26):
        # Decrypts the column with this shift
        decrypted = ''.join(
            chr(((ord(c) - ord('A') - shift) % 26) + ord('A'))
            for c in column
        )
        
        # Calculates frequencies
        observed_freq = calculate_frequencies(decrypted)
        
        # Calculates chi-squared
        score = chi_squared_score(observed_freq, expected_freq)
        
        if score < best_score:
            best_score = score
            best_shift = shift
    
    return best_shift, best_score


def frequency_attack(ciphertext: str, 
                    key_length: int,
                    language: str = 'pt') -> Dict:
    """
    Performs an attack by frequency analysis.
    
    Args:
        ciphertext: Ciphertext
        key_length: Key length
        language: Expected language ('pt', 'en', or 'auto')
        
    Returns:
        Dictionary with:
            - 'key': estimated key
            - 'plaintext': decrypted text
            - 'shifts': list of shifts found
            - 'confidence': result confidence (0-1)
    """
    # Detects language automatically if necessary
    if language == 'auto':
        from .frequency import detect_language
        language = detect_language(ciphertext)
    
    # Divides into columns
    columns = split_text_into_columns(ciphertext, key_length)
    
    if not columns:
        return {
            'key': '',
            'plaintext': '',
            'shifts': [],
            'confidence': 0.0
        }
    
    # Finds the best shift for each column
    shifts = []
    total_score = 0.0
    
    for column in columns:
        shift, score = find_best_shift(column, language)
        shifts.append(shift)
        total_score += score
    
    # Converts shifts to letters (A=0, B=1, ...)
    key = ''.join(chr(shift + ord('A')) for shift in shifts)
    
    # Decrypts the text
    plaintext = decrypt(ciphertext, key)
    
    # Calculates confidence based on score (lower is better)
    avg_score = total_score / len(shifts) if shifts else float('inf')
    # Normalizes to 0-1 (approximate value)
    confidence = max(0.0, min(1.0, 1.0 - (avg_score / 1000)))
    
    return {
        'key': key,
        'plaintext': plaintext,
        'shifts': shifts,
        'confidence': confidence
    }


def get_frequencies_for_plot(ciphertext: str, 
                             column: int = 0,
                             key_length: int = 1) -> Dict[str, float]:
    """
    Gets frequencies of a specific column for visualization.
    
    Args:
        ciphertext: Ciphertext
        column: Column index (0 to key_length-1)
        key_length: Key length
        
    Returns:
        Frequency dictionary of the specific column
    """
    if key_length <= 0 or column < 0 or column >= key_length:
        return calculate_frequencies(ciphertext)
    
    # Extracts only the specific column
    column_text = ciphertext[column::key_length]
    
    return calculate_frequencies(column_text)