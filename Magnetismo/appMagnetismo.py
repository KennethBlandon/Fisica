"""Calculadora de fuerzas magnéticas para ejecutar en terminal."""
from __future__ import annotations

import math
from typing import Sequence, Tuple

from fuerza import fuerza_carga, fuerza_conductor


def _format_val(valor: float) -> str:
    try:
        return f"{float(valor):.6g}"
    except Exception:
        return str(valor)


def _format_vec(vec: Sequence[float]) -> str:
    return "(" + ", ".join(_format_val(valor) for valor in vec) + ")"


def _leer_float(mensaje: str) -> float:
    while True:
        texto = input(mensaje).strip()
        try:
            return float(texto)
        except ValueError:
            print("Valor inválido. Intenta de nuevo.")


def _leer_vector(mensaje: str) -> Tuple[float, float, float]:
    while True:
        texto = input(mensaje).replace(",", " ").strip()
        partes = [parte for parte in texto.split() if parte]
        if len(partes) != 3:
            print("Debes ingresar exactamente 3 valores separados por espacio o coma.")
            continue
        try:
            return float(partes[0]), float(partes[1]), float(partes[2])
        except ValueError:
            print("Uno o más componentes no son numéricos. Intenta de nuevo.")


def calcular_particula() -> None:
    print("\nFuerza sobre partícula: F = q (v x B)")
    q = _leer_float("Carga q (C): ")
    v = _leer_vector("Velocidad v = x y z (m/s): ")
    B = _leer_vector("Campo magnético B = x y z (T): ")
    F = fuerza_carga(q, v, B)
    magnitud = math.sqrt(F[0] ** 2 + F[1] ** 2 + F[2] ** 2)
    print(f"q = {_format_val(q)}")
    print(f"v = {_format_vec(v)}")
    print(f"B = {_format_vec(B)}")
    print(f"F = {_format_vec(F)}")
    print(f"|F| = {_format_val(magnitud)} N")


def calcular_conductor() -> None:
    print("\nFuerza sobre conductor: F = I (L x B)")
    I = _leer_float("Corriente I (A): ")
    L = _leer_vector("Longitud L = x y z (m): ")
    B = _leer_vector("Campo magnético B = x y z (T): ")
    F = fuerza_conductor(I, L, B)
    magnitud = math.sqrt(F[0] ** 2 + F[1] ** 2 + F[2] ** 2)
    print(f"I = {_format_val(I)}")
    print(f"L = {_format_vec(L)}")
    print(f"B = {_format_vec(B)}")
    print(f"F = {_format_vec(F)}")
    print(f"|F| = {_format_val(magnitud)} N")


def main() -> None:
    print("Calculadora de magnetismo")
    while True:
        print("\nElige una opción:")
        print("1. Fuerza sobre partícula")
        print("2. Fuerza sobre conductor")
        print("3. Salir")
        opcion = input("Opción: ").strip().lower()

        if opcion in {"1", "particula", "partícula"}:
            calcular_particula()
        elif opcion in {"2", "conductor"}:
            calcular_conductor()
        elif opcion in {"3", "salir", "q", "quit", "exit"}:
            print("Saliendo...")
            break
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    main()
