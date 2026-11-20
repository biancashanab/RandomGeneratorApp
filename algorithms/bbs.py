"""Blum Blum Shub bit generator with input validation."""

from math import gcd


def is_prime(number: int) -> bool:
    """Deterministic primality check suitable for ordinary classroom inputs."""
    if number < 2:
        return False
    if number in (2, 3):
        return True
    if number % 2 == 0:
        return False
    divisor = 3
    while divisor * divisor <= number:
        if number % divisor == 0:
            return False
        divisor += 2
    return True


def generate_bbs(p: int, q: int, seed: int, count: int) -> tuple[list[int], list[int]]:
    """Return (states, bits), where each bit is the parity of a new state."""
    if not is_prime(p) or not is_prime(q):
        raise ValueError("p and q must both be prime numbers.")
    if p == q:
        raise ValueError("p and q must be distinct primes.")
    if p % 4 != 3 or q % 4 != 3:
        raise ValueError("Both p and q must be congruent to 3 modulo 4.")
    modulus = p * q
    if not 1 < seed < modulus:
        raise ValueError("Seed X₀ must satisfy 1 < X₀ < p·q.")
    if gcd(seed, modulus) != 1:
        raise ValueError("Seed X₀ must be coprime with p·q.")
    if count < 1:
        raise ValueError("The number of bits must be at least 1.")

    states: list[int] = []
    bits: list[int] = []
    x = seed
    for _ in range(count):
        x = pow(x, 2, modulus)
        states.append(x)
        bits.append(x % 2)
    return states, bits
