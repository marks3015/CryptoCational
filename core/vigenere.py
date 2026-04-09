"""
Vigenère cipher and decipher module.

This module contains the main functions to encrypt and decrypt
texts using the Vigenère cipher with the A-Z alphabet.
"""

import re
from typing import Tuple, List


def normalize_text(text: str) -> str:
    """
    Normalizes text for cryptographic processing.
    
    Removes accents, converts to uppercase, and keeps only A-Z.
    Useful for analysis and internal processing.
    
    Args:
        text: Input text
        
    Returns:
        Normalized text containing only uppercase A-Z letters
    """
    # Mapping from accented to non-accented characters
    accent_map = {
        'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a', 'ä': 'a',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
        'ó': 'o', 'ò': 'o', 'õ': 'o', 'ô': 'o', 'ö': 'o',
        'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
        'ç': 'c',
        'ñ': 'n',
        'Á': 'A', 'À': 'A', 'Ã': 'A', 'Â': 'A', 'Ä': 'A',
        'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E',
        'Í': 'I', 'Ì': 'I', 'Î': 'I', 'Ï': 'I',
        'Ó': 'O', 'Ò': 'O', 'Õ': 'O', 'Ô': 'O', 'Ö': 'O',
        'Ú': 'U', 'Ù': 'U', 'Û': 'U', 'Ü': 'U',
        'Ç': 'C',
        'Ñ': 'N',
    }
    
    # Remove accents
    normalized = text
    for accented, plain in accent_map.items():
        normalized = normalized.replace(accented, plain)
    
    # Keep only A-Z
    normalized = re.sub(r'[^A-Za-z]', '', normalized)
    
    return normalized.upper()


def remove_accents(text: str) -> str:
    """
    Removes accents from text while keeping other characters.
    
    Args:
        text: Input text
        
    Returns:
        Text without accents
    """
    accent_map = {
        'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a', 'ä': 'a',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
        'ó': 'o', 'ò': 'o', 'õ': 'o', 'ô': 'o', 'ö': 'o',
        'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
        'ç': 'c',
        'ñ': 'n',
        'Á': 'A', 'À': 'A', 'Ã': 'A', 'Â': 'A', 'Ä': 'A',
        'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E',
        'Í': 'I', 'Ì': 'I', 'Î': 'I', 'Ï': 'I',
        'Ó': 'O', 'Ò': 'O', 'Õ': 'O', 'Ô': 'O', 'Ö': 'O',
        'Ú': 'U', 'Ù': 'U', 'Û': 'U', 'Ü': 'U',
        'Ç': 'C',
        'Ñ': 'N',
    }
    
    result = text
    for accented, plain in accent_map.items():
        result = result.replace(accented, plain)
    
    return result


def validate_key(key: str) -> str:
    """
    Validates and normalizes the key.
    
    Args:
        key: Key provided by the user
        
    Returns:
        Normalized key (only uppercase A-Z)
        
    Raises:
        ValueError: If the key is empty or invalid
    """
    normalized_key = normalize_text(key)
    
    if not normalized_key:
        raise ValueError("Key cannot be empty")
    
    return normalized_key


def encrypt_preserve_format(plaintext: str, key: str) -> str:
    """
    Encrypts text while preserving original formatting.
    
    Encrypts only A-Z/a-z letters, keeping spaces, punctuation,
    numbers, and line breaks in their original positions.
    
    Args:
        plaintext: Text to be encrypted
        key: Cipher key
        
    Returns:
        Ciphertext with preserved formatting
        
    Raises:
        ValueError: If the key is empty
    """
    normalized_key = validate_key(key)
    
    if not plaintext:
        return ""
    
    # Remove accents but maintain structure
    text = remove_accents(plaintext)
    
    # Prepare expanded key
    key_expanded = (normalized_key * ((len(text) // len(normalized_key)) + 1))
    key_index = 0
    
    # Encrypt preserving format
    ciphertext = []
    for char in text:
        if char.isalpha():
            # Determine if uppercase or lowercase
            is_upper = char.isupper()
            base = ord('A') if is_upper else ord('a')
            
            # Convert to number (0-25)
            text_num = ord(char) - base
            key_num = ord(key_expanded[key_index]) - ord('A')
            
            # Encrypt
            encrypted_num = (text_num + key_num) % 26
            encrypted_char = chr(encrypted_num + base)
            
            ciphertext.append(encrypted_char)
            key_index += 1
        else:
            # Keeps non-alphabetic characters
            ciphertext.append(char)
    
    return ''.join(ciphertext)


def decrypt_preserve_format(ciphertext: str, key: str) -> str:
    """
    Decrypts text while preserving original formatting.
    
    Decrypts only A-Z/a-z letters, keeping spaces, punctuation,
    numbers, and line breaks in their original positions.
    
    Args:
        ciphertext: Ciphertext
        key: Cipher key
        
    Returns:
        Decrypted text with preserved formatting
        
    Raises:
        ValueError: If the key is empty
    """
    normalized_key = validate_key(key)
    
    if not ciphertext:
        return ""
    
    # Prepare expanded key
    key_expanded = (normalized_key * ((len(ciphertext) // len(normalized_key)) + 1))
    key_index = 0
    
    # Decrypt preserving format
    plaintext = []
    for char in ciphertext:
        if char.isalpha():
            # Determine if uppercase or lowercase
            is_upper = char.isupper()
            base = ord('A') if is_upper else ord('a')
            
            # Convert to number (0-25)
            cipher_num = ord(char) - base
            key_num = ord(key_expanded[key_index]) - ord('A')
            
            # Decrypt
            decrypted_num = (cipher_num - key_num) % 26
            decrypted_char = chr(decrypted_num + base)
            
            plaintext.append(decrypted_char)
            key_index += 1
        else:
            # Keeps non-alphabetic characters
            plaintext.append(char)
    
    return ''.join(plaintext)


def encrypt(plaintext: str, key: str) -> str:
    """
    Encrypts text using the Vigenère cipher (simple version, no formatting).
    
    Removes all formatting and returns only uppercase letters.
    Useful for internal processing and analysis.
    
    Args:
        plaintext: Text to be encrypted
        key: Cipher key
        
    Returns:
        Ciphertext (uppercase A-Z only, no spaces)
    """
    # Normalizes the texts
    text = normalize_text(plaintext)
    normalized_key = validate_key(key)
    
    if not text:
        return ""
    
    # Expand the key to match text length
    key_expanded = (normalized_key * ((len(text) // len(normalized_key)) + 1))[:len(text)]
    
    # Encrypt each letter
    ciphertext = []
    for i, char in enumerate(text):
        # Convert letter to number (A=0, B=1, ..., Z=25)
        text_num = ord(char) - ord('A')
        key_num = ord(key_expanded[i]) - ord('A')
        
        # Add and apply modulo 26
        encrypted_num = (text_num + key_num) % 26
        
        # Convert back to letter
        encrypted_char = chr(encrypted_num + ord('A'))
        ciphertext.append(encrypted_char)
    
    return ''.join(ciphertext)


def decrypt(ciphertext: str, key: str) -> str:
    """
    Decrypts ciphertext using the Vigenère cipher (simple version).
    
    Removes all formatting and returns only uppercase letters.
    Useful for internal processing and analysis.
    
    Args:
        ciphertext: Ciphertext
        key: Cipher key
        
    Returns:
        Decrypted text (uppercase A-Z only, no spaces)
    """
    # Normalizes the texts
    text = normalize_text(ciphertext)
    normalized_key = validate_key(key)
    
    if not text:
        return ""
    
    # Expand the key to match text length
    key_expanded = (normalized_key * ((len(text) // len(normalized_key)) + 1))[:len(text)]
    
    # Decrypt each letter
    plaintext = []
    for i, char in enumerate(text):
        # Convert letter to number (A=0, B=1, ..., Z=25)
        cipher_num = ord(char) - ord('A')
        key_num = ord(key_expanded[i]) - ord('A')
        
        # Subtract and apply modulo 26
        decrypted_num = (cipher_num - key_num) % 26
        
        # Convert back to letter
        decrypted_char = chr(decrypted_num + ord('A'))
        plaintext.append(decrypted_char)
    
    return ''.join(plaintext)