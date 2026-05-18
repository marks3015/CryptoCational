"""
AES-128 implementation from scratch in pure Python.

Implements the Advanced Encryption Standard (FIPS-197) with 128-bit blocks
and 128-bit keys. Supports configurable number of rounds (1-14).

This module does NOT use external cryptographic libraries.
"""

from typing import List

# ─────────────────────────────────────────────────────────────
# AES S-box (256 bytes)
# ─────────────────────────────────────────────────────────────
S_BOX = bytes([
    0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
    0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
    0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
    0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
    0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
    0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
    0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
    0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
    0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
    0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
    0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
    0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
    0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
    0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
    0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
    0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16,
])

# ─────────────────────────────────────────────────────────────
# Inverse S-box (256 bytes)
# ─────────────────────────────────────────────────────────────
INV_S_BOX = bytes([
    0x52, 0x09, 0x6A, 0xD5, 0x30, 0x36, 0xA5, 0x38, 0xBF, 0x40, 0xA3, 0x9E, 0x81, 0xF3, 0xD7, 0xFB,
    0x7C, 0xE3, 0x39, 0x82, 0x9B, 0x2F, 0xFF, 0x87, 0x34, 0x8E, 0x43, 0x44, 0xC4, 0xDE, 0xE9, 0xCB,
    0x54, 0x7B, 0x94, 0x32, 0xA6, 0xC2, 0x23, 0x3D, 0xEE, 0x4C, 0x95, 0x0B, 0x42, 0xFA, 0xC3, 0x4E,
    0x08, 0x2E, 0xA1, 0x66, 0x28, 0xD9, 0x24, 0xB2, 0x76, 0x5B, 0xA2, 0x49, 0x6D, 0x8B, 0xD1, 0x25,
    0x72, 0xF8, 0xF6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xD4, 0xA4, 0x5C, 0xCC, 0x5D, 0x65, 0xB6, 0x92,
    0x6C, 0x70, 0x48, 0x50, 0xFD, 0xED, 0xB9, 0xDA, 0x5E, 0x15, 0x46, 0x57, 0xA7, 0x8D, 0x9D, 0x84,
    0x90, 0xD8, 0xAB, 0x00, 0x8C, 0xBC, 0xD3, 0x0A, 0xF7, 0xE4, 0x58, 0x05, 0xB8, 0xB3, 0x45, 0x06,
    0xD0, 0x2C, 0x1E, 0x8F, 0xCA, 0x3F, 0x0F, 0x02, 0xC1, 0xAF, 0xBD, 0x03, 0x01, 0x13, 0x8A, 0x6B,
    0x3A, 0x91, 0x11, 0x41, 0x4F, 0x67, 0xDC, 0xEA, 0x97, 0xF2, 0xCF, 0xCE, 0xF0, 0xB4, 0xE6, 0x73,
    0x96, 0xAC, 0x74, 0x22, 0xE7, 0xAD, 0x35, 0x85, 0xE2, 0xF9, 0x37, 0xE8, 0x1C, 0x75, 0xDF, 0x6E,
    0x47, 0xF1, 0x1A, 0x71, 0x1D, 0x29, 0xC5, 0x89, 0x6F, 0xB7, 0x62, 0x0E, 0xAA, 0x18, 0xBE, 0x1B,
    0xFC, 0x56, 0x3E, 0x4B, 0xC6, 0xD2, 0x79, 0x20, 0x9A, 0xDB, 0xC0, 0xFE, 0x78, 0xCD, 0x5A, 0xF4,
    0x1F, 0xDD, 0xA8, 0x33, 0x88, 0x07, 0xC7, 0x31, 0xB1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xEC, 0x5F,
    0x60, 0x51, 0x7F, 0xA9, 0x19, 0xB5, 0x4A, 0x0D, 0x2D, 0xE5, 0x7A, 0x9F, 0x93, 0xC9, 0x9C, 0xEF,
    0xA0, 0xE0, 0x3B, 0x4D, 0xAE, 0x2A, 0xF5, 0xB0, 0xC8, 0xEB, 0xBB, 0x3C, 0x83, 0x53, 0x99, 0x61,
    0x17, 0x2B, 0x04, 0x7E, 0xBA, 0x77, 0xD6, 0x26, 0xE1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0C, 0x7D,
])

# ─────────────────────────────────────────────────────────────
# Galois Field (GF(2^8)) multiplication
# Irreducible polynomial: x^8 + x^4 + x^3 + x + 1  => 0x11B
# ─────────────────────────────────────────────────────────────
def _gmul(a: int, b: int) -> int:
    """Multiply two bytes in GF(2^8) with AES irreducible polynomial."""
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        hi = a & 0x80
        a <<= 1
        if hi:
            a ^= 0x1B  # 0x11B without the x^8 term (handled by overflow)
        b >>= 1
    return p & 0xFF


# Pre-computed multiplication tables for MixColumns
_MUL2 = bytes(_gmul(i, 0x02) for i in range(256))
_MUL3 = bytes(_gmul(i, 0x03) for i in range(256))
_MUL9 = bytes(_gmul(i, 0x09) for i in range(256))
_MUL11 = bytes(_gmul(i, 0x0B) for i in range(256))
_MUL13 = bytes(_gmul(i, 0x0D) for i in range(256))
_MUL14 = bytes(_gmul(i, 0x0E) for i in range(256))


# ─────────────────────────────────────────────────────────────
# State helpers (4x4 matrix as list of 16 bytes, column-major)
# ─────────────────────────────────────────────────────────────
def _bytes_to_state(data: bytes) -> List[int]:
    """Convert 16 bytes to state matrix (column-major order)."""
    return list(data)


def _state_to_bytes(state: List[int]) -> bytes:
    """Convert state matrix to 16 bytes."""
    return bytes(state)


# ─────────────────────────────────────────────────────────────
# AES transformations
# ─────────────────────────────────────────────────────────────
def _sub_bytes(state: List[int]) -> None:
    """Non-linear byte substitution using S-box."""
    for i in range(16):
        state[i] = S_BOX[state[i]]


def _inv_sub_bytes(state: List[int]) -> None:
    """Inverse byte substitution using InvS-box."""
    for i in range(16):
        state[i] = INV_S_BOX[state[i]]


def _shift_rows(state: List[int]) -> None:
    """Cyclically shift rows to the left."""
    # Row 0: no shift
    # Row 1: shift left by 1
    state[1], state[5], state[9], state[13] = state[5], state[9], state[13], state[1]
    # Row 2: shift left by 2
    state[2], state[6], state[10], state[14] = state[10], state[14], state[2], state[6]
    # Row 3: shift left by 3
    state[3], state[7], state[11], state[15] = state[15], state[3], state[7], state[11]


def _inv_shift_rows(state: List[int]) -> None:
    """Cyclically shift rows to the right (inverse)."""
    # Row 1: shift right by 1
    state[1], state[5], state[9], state[13] = state[13], state[1], state[5], state[9]
    # Row 2: shift right by 2
    state[2], state[6], state[10], state[14] = state[10], state[14], state[2], state[6]
    # Row 3: shift right by 3
    state[3], state[7], state[11], state[15] = state[7], state[11], state[15], state[3]


def _mix_columns(state: List[int]) -> None:
    """Mix columns by multiplying with fixed polynomial matrix."""
    for i in range(4):
        c0 = state[i * 4]
        c1 = state[i * 4 + 1]
        c2 = state[i * 4 + 2]
        c3 = state[i * 4 + 3]

        state[i * 4]     = _MUL2[c0] ^ _MUL3[c1] ^ c2 ^ c3
        state[i * 4 + 1] = c0 ^ _MUL2[c1] ^ _MUL3[c2] ^ c3
        state[i * 4 + 2] = c0 ^ c1 ^ _MUL2[c2] ^ _MUL3[c3]
        state[i * 4 + 3] = _MUL3[c0] ^ c1 ^ c2 ^ _MUL2[c3]


def _inv_mix_columns(state: List[int]) -> None:
    """Inverse mix columns."""
    for i in range(4):
        c0 = state[i * 4]
        c1 = state[i * 4 + 1]
        c2 = state[i * 4 + 2]
        c3 = state[i * 4 + 3]

        state[i * 4]     = _MUL14[c0] ^ _MUL11[c1] ^ _MUL13[c2] ^ _MUL9[c3]
        state[i * 4 + 1] = _MUL9[c0] ^ _MUL14[c1] ^ _MUL11[c2] ^ _MUL13[c3]
        state[i * 4 + 2] = _MUL13[c0] ^ _MUL9[c1] ^ _MUL14[c2] ^ _MUL11[c3]
        state[i * 4 + 3] = _MUL11[c0] ^ _MUL13[c1] ^ _MUL9[c2] ^ _MUL14[c3]


def _add_round_key(state: List[int], round_key: bytes) -> None:
    """XOR state with round key."""
    for i in range(16):
        state[i] ^= round_key[i]


# ─────────────────────────────────────────────────────────────
# Key Expansion
# ─────────────────────────────────────────────────────────────
def _sub_word(word: bytes) -> bytes:
    """Apply S-box to each byte of a 4-byte word."""
    return bytes(S_BOX[b] for b in word)


def _rot_word(word: bytes) -> bytes:
    """Cyclic shift left of a 4-byte word."""
    return bytes([word[1], word[2], word[3], word[0]])


def _rcon(i: int) -> bytes:
    """Generate round constant for iteration i (1-based)."""
    # x^(i-1) in GF(2^8), where x = {02}
    val = 1
    for _ in range(i - 1):
        val = _gmul(val, 0x02)
    return bytes([val, 0x00, 0x00, 0x00])


def key_expansion(key: bytes, num_rounds: int) -> List[bytes]:
    """
    Expand the cipher key into (num_rounds + 1) round keys.
    
    Args:
        key: 16-byte key
        num_rounds: Number of AES rounds (1 to 14)
    
    Returns:
        List of (num_rounds + 1) round keys, each 16 bytes.
    """
    if len(key) != 16:
        raise ValueError("Key must be exactly 16 bytes for AES-128")
    if not (1 <= num_rounds <= 14):
        raise ValueError("num_rounds must be between 1 and 14")

    nk = 4  # words in key (128-bit)
    nb = 4  # words in block (128-bit)
    nr = num_rounds

    w = [key[i:i+4] for i in range(0, 16, 4)]  # initial 4 words

    for i in range(nk, nb * (nr + 1)):
        temp = w[i - 1]
        if i % nk == 0:
            temp = _sub_word(_rot_word(temp))
            rcon = _rcon(i // nk)
            temp = bytes(a ^ b for a, b in zip(temp, rcon))
        w.append(bytes(a ^ b for a, b in zip(w[i - nk], temp)))

    # Pack words into 16-byte round keys
    round_keys = []
    for i in range(0, len(w), nb):
        rk = b''.join(w[i:i+nb])
        round_keys.append(rk)

    return round_keys


# ─────────────────────────────────────────────────────────────
# Single block encrypt / decrypt (configurable rounds)
# ─────────────────────────────────────────────────────────────
def encrypt_block(block: bytes, round_keys: List[bytes], num_rounds: int) -> bytes:
    """
    Encrypt a single 16-byte block.
    
    Args:
        block: 16-byte plaintext block
        round_keys: List of round keys from key_expansion()
        num_rounds: Number of rounds to execute
    
    Returns:
        16-byte ciphertext block
    """
    if len(block) != 16:
        raise ValueError("Block must be exactly 16 bytes")
    if len(round_keys) != num_rounds + 1:
        raise ValueError(f"Expected {num_rounds + 1} round keys, got {len(round_keys)}")

    state = _bytes_to_state(block)

    # Initial round
    _add_round_key(state, round_keys[0])

    # Main rounds
    for r in range(1, num_rounds):
        _sub_bytes(state)
        _shift_rows(state)
        _mix_columns(state)
        _add_round_key(state, round_keys[r])

    # Final round (no MixColumns)
    _sub_bytes(state)
    _shift_rows(state)
    _add_round_key(state, round_keys[num_rounds])

    return _state_to_bytes(state)


def encrypt_block_visual(block: bytes, round_keys: List[bytes], num_rounds: int, mixcol_after: int = 3) -> bytes:
    """
    Encrypt a single 16-byte block with gradual introduction of MixColumns.

    MixColumns is omitted in intermediate rounds < mixcol_after.
    This creates a visual progression where early rounds preserve image structure.
    """
    if len(block) != 16:
        raise ValueError("Block must be exactly 16 bytes")
    if len(round_keys) != num_rounds + 1:
        raise ValueError(f"Expected {num_rounds + 1} round keys, got {len(round_keys)}")

    state = _bytes_to_state(block)

    # Initial round
    _add_round_key(state, round_keys[0])

    # Main rounds
    for r in range(1, num_rounds):
        _sub_bytes(state)
        _shift_rows(state)
        if r >= mixcol_after:
            _mix_columns(state)
        _add_round_key(state, round_keys[r])

    # Final round (no MixColumns)
    _sub_bytes(state)
    _shift_rows(state)
    _add_round_key(state, round_keys[num_rounds])

    return _state_to_bytes(state)


def decrypt_block(block: bytes, round_keys: List[bytes], num_rounds: int) -> bytes:
    """
    Decrypt a single 16-byte block.
    
    Args:
        block: 16-byte ciphertext block
        round_keys: List of round keys from key_expansion()
        num_rounds: Number of rounds to execute
    
    Returns:
        16-byte plaintext block
    """
    if len(block) != 16:
        raise ValueError("Block must be exactly 16 bytes")
    if len(round_keys) != num_rounds + 1:
        raise ValueError(f"Expected {num_rounds + 1} round keys, got {len(round_keys)}")

    state = _bytes_to_state(block)

    # Initial round (inverse of final round)
    _add_round_key(state, round_keys[num_rounds])
    _inv_shift_rows(state)
    _inv_sub_bytes(state)

    # Main inverse rounds
    for r in range(num_rounds - 1, 0, -1):
        _add_round_key(state, round_keys[r])
        _inv_mix_columns(state)
        _inv_shift_rows(state)
        _inv_sub_bytes(state)

    # Final AddRoundKey
    _add_round_key(state, round_keys[0])

    return _state_to_bytes(state)


# ─────────────────────────────────────────────────────────────
# Convenience wrappers
# ─────────────────────────────────────────────────────────────
def aes_encrypt_block(block: bytes, key: bytes, num_rounds: int = 10) -> bytes:
    """Encrypt one 16-byte block with AES-128."""
    round_keys = key_expansion(key, num_rounds)
    return encrypt_block(block, round_keys, num_rounds)


def aes_decrypt_block(block: bytes, key: bytes, num_rounds: int = 10) -> bytes:
    """Decrypt one 16-byte block with AES-128."""
    round_keys = key_expansion(key, num_rounds)
    return decrypt_block(block, round_keys, num_rounds)


# ─────────────────────────────────────────────────────────────
# PKCS#7 Padding
# ─────────────────────────────────────────────────────────────
def pad_pkcs7(data: bytes) -> bytes:
    """Apply PKCS#7 padding to make data a multiple of 16 bytes."""
    pad_len = 16 - (len(data) % 16)
    return data + bytes([pad_len] * pad_len)


def unpad_pkcs7(data: bytes) -> bytes:
    """Remove PKCS#7 padding."""
    if not data:
        return data
    pad_len = data[-1]
    if pad_len > 16 or pad_len == 0:
        raise ValueError("Invalid PKCS#7 padding")
    if data[-pad_len:] != bytes([pad_len] * pad_len):
        raise ValueError("Invalid PKCS#7 padding")
    return data[:-pad_len]


# ─────────────────────────────────────────────────────────────
# Key normalization
# ─────────────────────────────────────────────────────────────
def normalize_key(key_text: str) -> bytes:
    """
    Convert a text key to exactly 16 bytes for AES-128.
    
    If the UTF-8 encoding is shorter than 16 bytes, pad with null bytes.
    If longer, truncate to 16 bytes.
    """
    key_bytes = key_text.encode('utf-8')
    if len(key_bytes) < 16:
        key_bytes = key_bytes + b'\x00' * (16 - len(key_bytes))
    return key_bytes[:16]
