"""Linear congruential generator."""


def generate_lcg(a: int, c: int, m: int, seed: int, count: int) -> list[int]:
    """Return ``count`` states, excluding the initial seed.

    The recurrence is X[n+1] = (a * X[n] + c) mod m.
    """
    if m <= 0:
        raise ValueError("Modulus m must be a positive integer.")
    if not 0 <= seed < m:
        raise ValueError("Seed X₀ must be in the range 0 ≤ X₀ < m.")
    if count < 1:
        raise ValueError("The number of values must be at least 1.")

    values: list[int] = []
    x = seed
    for _ in range(count):
        x = (a * x + c) % m
        values.append(x)
    return values
