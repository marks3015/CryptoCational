"""Assinatura e verificação de arquivos usando RSA-OAEP e SHA3-256."""

import base64
import hashlib
from pathlib import Path
from typing import Tuple

from .cipher import PrivateKey, PublicKey
from .oaep import oaep_decode, oaep_encode


# Delimitadores do arquivo assinado.
BEGIN_SIGNED_MSG = "-----BEGIN RSA SIGNED MESSAGE-----"
END_SIGNED_MSG = "-----END RSA SIGNED MESSAGE-----"
BEGIN_SIGNATURE = "-----BEGIN RSA SIGNATURE-----"


def _modulus_bytes(n: int) -> int:
    return (n.bit_length() + 7) // 8


def _hash_file(path: Path) -> bytes:
    """Calcula o hash SHA3-256 do conteúdo de um arquivo."""
    hasher = hashlib.sha3_256()
    with path.open("rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.digest()


def _sign_hash(digest: bytes, private_key: PrivateKey) -> bytes:
    """Assina o hash: cifra OAEP do hash usando a chave privada."""
    n, d = private_key
    encoded = oaep_encode(digest, n)
    signature_int = pow(int.from_bytes(encoded, byteorder="big"), d, n)
    return signature_int.to_bytes(_modulus_bytes(n), byteorder="big")


def _verify_signature(signature: bytes, public_key: PublicKey) -> bytes:
    """Decifra a assinatura usando a chave pública e retorna o hash original."""
    n, e = public_key
    signature_int = int.from_bytes(signature, byteorder="big")
    encoded_int = pow(signature_int, e, n)
    encoded = encoded_int.to_bytes(_modulus_bytes(n), byteorder="big")
    return oaep_decode(encoded, n)


def sign_file(input_path: Path, output_path: Path, private_key: PrivateKey) -> None:
    """Assina um arquivo e salva o documento assinado.

    O arquivo assinado contém a mensagem original (BASE64) e a assinatura (BASE64).
    """
    message = input_path.read_bytes()
    digest = _hash_file(input_path)
    signature = _sign_hash(digest, private_key)

    signed_doc = (
        f"{BEGIN_SIGNED_MSG}\n"
        f"{base64.b64encode(message).decode('ascii')}\n"
        f"{BEGIN_SIGNATURE}\n"
        f"{base64.b64encode(signature).decode('ascii')}\n"
        f"{END_SIGNED_MSG}\n"
    )
    output_path.write_text(signed_doc, encoding="ascii")


def verify_file(signed_path: Path, public_key: PublicKey) -> Tuple[bool, str]:
    """Verifica a assinatura de um arquivo assinado.

    Returns:
        Tupla (válido?, mensagem de status).
    """
    try:
        content = signed_path.read_text(encoding="ascii")
    except UnicodeDecodeError:
        return False, "Arquivo assinado contém caracteres não-ASCII."

    lines = content.splitlines()
    try:
        msg_start = lines.index(BEGIN_SIGNED_MSG)
        sig_start = lines.index(BEGIN_SIGNATURE)
        end_idx = lines.index(END_SIGNED_MSG)
    except ValueError:
        return False, "Formato do arquivo assinado inválido."

    message_b64 = "".join(lines[msg_start + 1 : sig_start]).strip()
    signature_b64 = "".join(lines[sig_start + 1 : end_idx]).strip()

    try:
        message = base64.b64decode(message_b64)
        signature = base64.b64decode(signature_b64)
    except Exception:
        return False, "Falha ao decodificar BASE64."

    try:
        recovered_digest = _verify_signature(signature, public_key)
    except Exception as exc:
        return False, f"Falha ao decifrar assinatura: {exc}"

    actual_digest = hashlib.sha3_256(message).digest()
    if recovered_digest == actual_digest:
        return True, "Assinatura válida."
    return False, "Assinatura inválida: hashes não conferem."
