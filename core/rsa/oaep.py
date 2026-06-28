"""Implementação do padding OAEP com SHA3-256 e MGF1."""

import hashlib
import secrets
from typing import Optional


# Fixa SHA3-256 como função de hash para OAEP.
_HASH_ALGORITHM = hashlib.sha3_256
_HASH_LEN = _HASH_ALGORITHM().digest_size  # 32 bytes


def _xor(a: bytes, b: bytes) -> bytes:
    """XOR byte a byte entre duas sequências de bytes."""
    return bytes(x ^ y for x, y in zip(a, b))


def _mgf1(seed: bytes, mask_len: int) -> bytes:
    """Mask Generation Function baseada em SHA3-256 (MGF1).

    Args:
        seed: semente de entrada.
        mask_len: tamanho desejado para a máscara em bytes.

    Returns:
        Máscara de tamanho mask_len.
    """
    if mask_len > (_HASH_LEN << 32):
        raise ValueError("mask_len muito grande para MGF1.")

    counter = 0
    output = b""
    while len(output) < mask_len:
        c = counter.to_bytes(4, byteorder="big")
        output += _HASH_ALGORITHM(seed + c).digest()
        counter += 1
    return output[:mask_len]


def _modulus_bytes(n: int) -> int:
    """Retorna o tamanho em bytes do módulo RSA n."""
    return (n.bit_length() + 7) // 8


def oaep_encode(message: bytes, n: int, label: Optional[bytes] = None) -> bytes:
    """Codifica uma mensagem usando OAEP.

    Args:
        message: mensagem em claro (bytes).
        n: módulo RSA.
        label: rótulo opcional (padrão: bytes vazios).

    Returns:
        Mensagem codificada (encoded message) pronta para cifração RSA.
    """
    label = label or b""
    k = _modulus_bytes(n)
    h_len = _HASH_LEN
    max_len = k - 2 * h_len - 2

    if len(message) > max_len:
        raise ValueError(
            f"Mensagem muito longa para OAEP com RSA-{n.bit_length()}: "
            f"máximo {max_len} bytes, recebido {len(message)} bytes."
        )

    l_hash = _HASH_ALGORITHM(label).digest()
    ps = b"\x00" * (k - len(message) - 2 * h_len - 2)
    db = l_hash + ps + b"\x01" + message
    seed = secrets.token_bytes(h_len)
    db_mask = _mgf1(seed, k - h_len - 1)
    masked_db = _xor(db, db_mask)
    seed_mask = _mgf1(masked_db, h_len)
    masked_seed = _xor(seed, seed_mask)
    encoded_message = b"\x00" + masked_seed + masked_db
    return encoded_message


def oaep_decode(encoded_message: bytes, n: int, label: Optional[bytes] = None) -> bytes:
    """Decodifica uma mensagem previamente codificada com OAEP.

    Args:
        encoded_message: mensagem codificada (bytes).
        n: módulo RSA.
        label: rótulo opcional (padrão: bytes vazios).

    Returns:
        Mensagem original (bytes).
    """
    label = label or b""
    k = _modulus_bytes(n)
    h_len = _HASH_LEN

    if len(encoded_message) != k:
        raise ValueError(f"Tamanho inválido da mensagem codificada: esperado {k}, recebido {len(encoded_message)}.")
    if encoded_message[0:1] != b"\x00":
        raise ValueError("Byte inicial inválido na mensagem OAEP.")

    masked_seed = encoded_message[1 : h_len + 1]
    masked_db = encoded_message[h_len + 1 :]
    seed_mask = _mgf1(masked_db, h_len)
    seed = _xor(masked_seed, seed_mask)
    db_mask = _mgf1(seed, k - h_len - 1)
    db = _xor(masked_db, db_mask)

    l_hash = _HASH_ALGORITHM(label).digest()
    if db[:h_len] != l_hash:
        raise ValueError("Hash do rótulo não confere na decodificação OAEP.")

    # Remove o padding de zeros e encontra o separador 0x01.
    rest = db[h_len:]
    one_index = rest.find(b"\x01")
    if one_index == -1:
        raise ValueError("Separador 0x01 não encontrado na mensagem OAEP.")

    # Tudo antes de 0x01 deve ser zeros.
    if rest[:one_index] != b"\x00" * one_index:
        raise ValueError("Padding inválido na mensagem OAEP.")

    return rest[one_index + 1 :]
