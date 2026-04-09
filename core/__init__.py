"""
Core package for Vigenère cipher operations.
"""

from .vigenere import (
    encrypt, decrypt, normalize_text,
    encrypt_preserve_format, decrypt_preserve_format,
    remove_accents
)
from .frequency import get_language_frequencies, calculate_frequencies, load_frequencies
from .attack import frequency_attack, estimate_key_length
from .utils import chunk_text, split_text_into_columns, estimate_ic

__all__ = [
    'encrypt',
    'decrypt', 
    'normalize_text',
    'encrypt_preserve_format',
    'decrypt_preserve_format',
    'remove_accents',
    'get_language_frequencies',
    'calculate_frequencies',
    'load_frequencies',
    'frequency_attack',
    'estimate_key_length',
    'chunk_text',
    'split_text_into_columns',
    'estimate_ic',
]