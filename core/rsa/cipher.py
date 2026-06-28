"""Cifração e decifração RSA com padding OAEP."""

from .oaep import oaep_decode, oaep_encode
from typing import Tuple


PublicKey = Tuple[int, int]
PrivateKey = Tuple[int, int]


def rsa_encrypt(message: bytes, public_key: PublicKey) -> bytes:
    """Cifra uma mensagem usando RSA-OAEP com a chave pública.

    Args:
        message: mensagem em claro.
        public_key: tupla (n, e).

    Returns:
        Texto cifrado como bytes (big-endian, tamanho do módulo).
    """
    n, e = public_key
    encoded = oaep_encode(message, n)
    ciphertext_int = pow(int.from_bytes(encoded, byteorder="big"), e, n)
    return ciphertext_int.to_bytes((n.bit_length() + 7) // 8, byteorder="big")


def rsa_decrypt(ciphertext: bytes, private_key: PrivateKey) -> bytes:
    """Decifra um texto cifrado usando RSA-OAEP com a chave privada.

    Args:
        ciphertext: texto cifrado.
        private_key: tupla (n, d).

    Returns:
        Mensagem original.
    """
    n, d = private_key
    ciphertext_int = int.from_bytes(ciphertext, byteorder="big")
    encoded_int = pow(ciphertext_int, d, n)
    encoded = encoded_int.to_bytes((n.bit_length() + 7) // 8, byteorder="big")
    return oaep_decode(encoded, n)
