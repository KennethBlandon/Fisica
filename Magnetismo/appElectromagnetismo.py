"""Ejemplo de uso del módulo Magnetismo en terminal."""
import math

from fuerza import fuerza_carga, fuerza_conductor


def ejemplo() -> None:
    q = 1.6e-19
    v = (1.0, 0.0, 0.0)
    B = (0.0, 0.0, 1.0)
    print("Ejemplo: fuerza sobre carga")
    print("q =", q, "v =", v, "B =", B)
    F = fuerza_carga(q, v, B)
    print("F =", F)
    print("|F| =", math.sqrt(F[0] ** 2 + F[1] ** 2 + F[2] ** 2))

    I = 2.0
    L = (0.0, 1.0, 0.0)
    print("\nEjemplo: fuerza sobre conductor")
    print("I =", I, "L =", L, "B =", B)
    F = fuerza_conductor(I, L, B)
    print("F =", F)
    print("|F| =", math.sqrt(F[0] ** 2 + F[1] ** 2 + F[2] ** 2))


if __name__ == "__main__":
    ejemplo()
