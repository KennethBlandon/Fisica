"""Funciones para calcular fuerzas magnéticas.

Fórmulas:
- Fuerza sobre una carga puntual: F = q * (v x B)
- Fuerza sobre un conductor: F = I * (L x B)

Todas las entradas son vectores de 3 componentes (secuencia) o números.
"""
from typing import Sequence, Tuple


def _to_vector(v: Sequence[float]) -> Tuple[float, float, float]:
    try:
        if len(v) != 3:
            raise ValueError("El vector debe tener 3 componentes")
        return float(v[0]), float(v[1]), float(v[2])
    except TypeError:
        raise TypeError("El vector debe ser una secuencia de 3 números")


def cross(a: Sequence[float], b: Sequence[float]) -> Tuple[float, float, float]:
    """Calcula el producto vectorial a x b para vectores de 3 componentes.

    Devuelve una tupla (x, y, z).
    """
    a1, a2, a3 = _to_vector(a)
    b1, b2, b3 = _to_vector(b)
    return (a2 * b3 - a3 * b2, a3 * b1 - a1 * b3, a1 * b2 - a2 * b1)


def fuerza_carga(q: float, v: Sequence[float], B: Sequence[float]) -> Tuple[float, float, float]:
    """Calcula la fuerza magnética sobre una carga puntual.

    Parámetros:
    - q: carga (float)
    - v: velocidad (secuencia de 3 números)
    - B: campo magnético (secuencia de 3 números)

    Devuelve la fuerza F = q * (v x B).
    """
    cx = cross(v, B)
    return (q * cx[0], q * cx[1], q * cx[2])


def fuerza_conductor(I: float, L: Sequence[float], B: Sequence[float]) -> Tuple[float, float, float]:
    """Calcula la fuerza magnética sobre un conductor rectilíneo.

    Parámetros:
    - I: corriente (float)
    - L: vector longitud (secuencia de 3 números)
    - B: campo magnético (secuencia de 3 números)

    Devuelve la fuerza F = I * (L x B).
    """
    cx = cross(L, B)
    return (I * cx[0], I * cx[1], I * cx[2])
