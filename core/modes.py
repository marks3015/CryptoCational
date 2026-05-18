"""
AES block cipher modes of operation: ECB and CTR.

Implements ECB (Electronic Codebook) and CTR (Counter) modes
using the manual AES-128 implementation from core.aes.
"""

import os
import struct
from typing import Tuple, Optional

from core.aes import (
    key_expansion,
    encrypt_block,
    encrypt_block_visual,
    decrypt_block,
    pad_pkcs7,
    unpad_pkcs7,
    normalize_key,
)

BLOCK_SIZE = 16


# ─────────────────────────────────────────────────────────────
# ECB Mode
# ─────────────────────────────────────────────────────────────
def aes_ecb_encrypt(data: bytes, key: bytes, num_rounds: int = 10) -> bytes:
    """
    Encrypt data using AES-128 in ECB mode.
    
    Args:
        data: Plaintext bytes (any length; PKCS#7 padding applied)
        key: 16-byte key
        num_rounds: Number of AES rounds
    
    Returns:
        Ciphertext bytes
    """
    if len(key) != 16:
        raise ValueError("Key must be 16 bytes")

    round_keys = key_expansion(key, num_rounds)
    padded = pad_pkcs7(data)
    ciphertext = bytearray()

    for i in range(0, len(padded), BLOCK_SIZE):
        block = padded[i:i + BLOCK_SIZE]
        ciphertext.extend(encrypt_block(block, round_keys, num_rounds))

    return bytes(ciphertext)


def aes_ecb_decrypt(ciphertext: bytes, key: bytes, num_rounds: int = 10) -> bytes:
    """
    Decrypt data using AES-128 in ECB mode.
    
    Args:
        ciphertext: Ciphertext bytes (multiple of 16)
        key: 16-byte key
        num_rounds: Number of AES rounds
    
    Returns:
        Plaintext bytes (PKCS#7 padding removed)
    """
    if len(key) != 16:
        raise ValueError("Key must be 16 bytes")
    if len(ciphertext) % BLOCK_SIZE != 0:
        raise ValueError("Ciphertext length must be a multiple of 16")

    round_keys = key_expansion(key, num_rounds)
    plaintext = bytearray()

    for i in range(0, len(ciphertext), BLOCK_SIZE):
        block = ciphertext[i:i + BLOCK_SIZE]
        plaintext.extend(decrypt_block(block, round_keys, num_rounds))

    return unpad_pkcs7(bytes(plaintext))


# ─────────────────────────────────────────────────────────────
# CTR Mode
# ─────────────────────────────────────────────────────────────
def _inc_nonce(nonce: bytes) -> bytes:
    """Increment the counter portion of a 16-byte nonce (big-endian)."""
    # Treat last 8 bytes as big-endian counter
    val = int.from_bytes(nonce, 'big')
    val = (val + 1) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
    return val.to_bytes(16, 'big')


def aes_ctr_encrypt(data: bytes, key: bytes, num_rounds: int = 10, iv: Optional[bytes] = None) -> Tuple[bytes, bytes]:
    """
    Encrypt/Decrypt data using AES-128 in CTR mode.
    
    Since CTR mode XORs the keystream with plaintext, the same function
    works for both encryption and decryption.
    
    Args:
        data: Plaintext or ciphertext bytes (any length)
        key: 16-byte key
        num_rounds: Number of AES rounds
        iv: Optional 16-byte nonce/IV. If None, a random one is generated.
    
    Returns:
        Tuple of (output_bytes, iv_used)
    """
    if len(key) != 16:
        raise ValueError("Key must be 16 bytes")

    if iv is None:
        iv = os.urandom(16)
    elif len(iv) != 16:
        raise ValueError("IV must be 16 bytes")

    round_keys = key_expansion(key, num_rounds)
    nonce = iv
    output = bytearray()

    for i in range(0, len(data), BLOCK_SIZE):
        block = data[i:i + BLOCK_SIZE]
        keystream = encrypt_block(nonce, round_keys, num_rounds)
        output.extend(b ^ k for b, k in zip(block, keystream))
        nonce = _inc_nonce(nonce)

    return bytes(output), iv


def aes_ctr_decrypt(ciphertext: bytes, key: bytes, num_rounds: int = 10, iv: Optional[bytes] = None) -> bytes:
    """
    Decrypt data using AES-128 in CTR mode.
    
    Args:
        ciphertext: Ciphertext bytes (any length)
        key: 16-byte key
        num_rounds: Number of AES rounds
        iv: 16-byte nonce/IV (must be the same used for encryption)
    
    Returns:
        Plaintext bytes
    """
    plaintext, _ = aes_ctr_encrypt(ciphertext, key, num_rounds, iv)
    return plaintext


# ─────────────────────────────────────────────────────────────
# Visual / didactic modes (gradual MixColumns for image demos)
# ─────────────────────────────────────────────────────────────
def aes_ecb_encrypt_visual(data: bytes, key: bytes, num_rounds: int = 10, mixcol_after: int = 3) -> bytes:
    """
    Encrypt data using a didactic AES variant for visual demonstrations.

    MixColumns is only applied from round ``mixcol_after`` onward, so
    images encrypted with a small number of rounds still show structural
    remnants (colours shifted, rows displaced) instead of pure noise.
    """
    if len(key) != 16:
        raise ValueError("Key must be 16 bytes")

    round_keys = key_expansion(key, num_rounds)
    padded = pad_pkcs7(data)
    ciphertext = bytearray()

    for i in range(0, len(padded), BLOCK_SIZE):
        block = padded[i:i + BLOCK_SIZE]
        ciphertext.extend(encrypt_block_visual(block, round_keys, num_rounds, mixcol_after))

    return bytes(ciphertext)


def aes_ctr_encrypt_visual(data: bytes, key: bytes, num_rounds: int = 10, iv: Optional[bytes] = None, mixcol_after: int = 3) -> Tuple[bytes, bytes]:
    """
    Encrypt/Decrypt data using a didactic AES-CTR variant for visual demos.

    The keystream is generated with ``encrypt_block_visual`` so that the
    visual progression (gradual MixColumns) is also visible in CTR mode.
    """
    if len(key) != 16:
        raise ValueError("Key must be 16 bytes")

    if iv is None:
        iv = os.urandom(16)
    elif len(iv) != 16:
        raise ValueError("IV must be 16 bytes")

    round_keys = key_expansion(key, num_rounds)
    nonce = iv
    output = bytearray()

    for i in range(0, len(data), BLOCK_SIZE):
        block = data[i:i + BLOCK_SIZE]
        keystream = encrypt_block_visual(nonce, round_keys, num_rounds, mixcol_after)
        output.extend(b ^ k for b, k in zip(block, keystream))
        nonce = _inc_nonce(nonce)

    return bytes(output), iv


# ─────────────────────────────────────────────────────────────
# Image helper for selfie tests
# ─────────────────────────────────────────────────────────────
def ciphertext_bytes_to_displayable(cipher_bytes: bytes, original_size: int) -> bytes:
    """
    Truncate or pad ciphertext bytes to match the original file size
    so it can be reinterpreted as image data for visual inspection.
    
    Args:
        cipher_bytes: Ciphertext bytes (may include padding)
        original_size: Original file size in bytes
    
    Returns:
        Bytes of length original_size
    """
    if len(cipher_bytes) >= original_size:
        return cipher_bytes[:original_size]
    # Should not happen since padding only adds, but just in case
    return cipher_bytes + b'\x00' * (original_size - len(cipher_bytes))
