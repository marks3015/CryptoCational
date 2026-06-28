"""Geração de chaves RSA com teste de primalidade de Miller-Rabin."""

import secrets
from typing import Tuple


def _miller_rabin_test(n: int, k: int = 64) -> bool:
    """Teste de primalidade de Miller-Rabin.

    Args:
        n: número inteiro a ser testado.
        k: número de rounds (quanto maior, menor a probabilidade de falso positivo).

    Returns:
        True se n for provavelmente primo, False caso contrário.
    """
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False

    # Escreve n-1 como 2^r * d, com d ímpar.
    r = 0
    d = n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    # Testa k bases aleatórias.
    for _ in range(k):
        a = secrets.randbelow(n - 3) + 2  # a em [2, n-2]
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def _generate_random_odd(bits: int) -> int:
    """Gera um número ímpar aleatório com o número especificado de bits."""
    while True:
        candidate = secrets.randbits(bits)
        # Garante que tem exatamente 'bits' bits e é ímpar.
        candidate |= (1 << (bits - 1)) | 1
        if candidate.bit_length() == bits:
            return candidate


def generate_prime(bits: int, k: int = 64) -> int:
    """Gera um primo aleatório de 'bits' bits usando Miller-Rabin.

    Args:
        bits: tamanho em bits do primo desejado.
        k: número de rounds do teste de Miller-Rabin.

    Returns:
        Um número primo de 'bits' bits.
    """
    while True:
        candidate = _generate_random_odd(bits)
        if _miller_rabin_test(candidate, k):
            return candidate


def generate_keypair(bits: int = 1024, public_exponent: int = 65537) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """Gera um par de chaves RSA.

    Args:
        bits: tamanho em bits de cada primo p e q (chave resultante terá 2*bits bits).
        public_exponent: expoente público e.

    Returns:
        Tupla ((n, e), (n, d)) com chave pública e chave privada.
    """
    if bits < 1024:
        raise ValueError("Cada primo deve ter no mínimo 1024 bits.")
    if public_exponent < 3 or public_exponent % 2 == 0:
        raise ValueError("O expoente público deve ser ímpar e maior ou igual a 3.")

    p = generate_prime(bits)
    q = generate_prime(bits)

    # Garante que p != q.
    while p == q:
        q = generate_prime(bits)

    n = p * q
    phi = (p - 1) * (q - 1)

    if phi % public_exponent == 0:
        raise RuntimeError("O expoente público não é coprimo com φ(n). Gere novas chaves.")

    d = pow(public_exponent, -1, phi)
    return (n, public_exponent), (n, d)
