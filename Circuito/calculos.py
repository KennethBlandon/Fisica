"""
calculos
────────
Núcleo matemático para resolver circuitos simples de
resistores y capacitores en serie o paralelo.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import re
from typing import List


_PREFIJOS = {
    "p": 1e-12,
    "n": 1e-9,
    "u": 1e-6,
    "µ": 1e-6,
    "m": 1e-3,
    "k": 1e3,
    "K": 1e3,
    "M": 1e6,
    "G": 1e9,
}


@dataclass(slots=True)
class ResultadoCircuito:
    tipo: str
    conexion: str
    fuente: float
    valores: List[float]
    equivalente: float
    corriente_total: float | None = None
    corrientes: List[float] | None = None
    voltajes: List[float] | None = None
    cargas: List[float] | None = None
    carga_total: float | None = None


def parse_prefixed_value(texto: str) -> float:
    """Convierte valores como '53 mV', '3553 pF' o '10k' a base SI."""
    if texto is None:
        raise ValueError("El valor está vacío.")

    texto = str(texto).strip()
    if not texto:
        raise ValueError("El valor está vacío.")

    texto = texto.replace(",", ".")
    texto = re.sub(r"\s*([=:\-])\s*", r"\1", texto)

    match = re.match(
        r"^([+-]?(?:\d+(?:\.\d+)?|\.\d+)(?:[eE][+-]?\d+)?)\s*([pnumkKMGµ]?)\s*([a-zA-ZΩuµ]*)$",
        texto,
    )
    if not match:
        raise ValueError(f"No pude interpretar el valor: {texto!r}")

    magnitud = float(match.group(1))
    prefijo = match.group(2)
    factor = _PREFIJOS.get(prefijo, 1.0)
    return magnitud * factor


def _validar_valores(valores: List[float]) -> None:
    if not valores:
        raise ValueError("Se necesita al menos un resistor o capacitor.")
    if any(v <= 0 for v in valores):
        raise ValueError("Todos los valores deben ser mayores que cero.")


def resolver_circuito(tipo: str, conexion: str, fuente: float, valores: List[float]) -> ResultadoCircuito:
    """Resuelve el circuito solicitado usando las ecuaciones correctas."""
    tipo = tipo.strip().lower()
    conexion = conexion.strip().lower()
    _validar_valores(valores)

    if fuente <= 0:
        raise ValueError("La batería debe ser mayor que cero.")

    if tipo not in {"resistores", "capacitores"}:
        raise ValueError("El tipo debe ser 'Resistores' o 'Capacitores'.")
    if conexion not in {"serie", "paralelo"}:
        raise ValueError("La conexión debe ser 'Serie' o 'Paralelo'.")

    if tipo == "resistores" and conexion == "serie":
        equivalente = sum(valores)
        corriente = fuente / equivalente
        voltajes = [corriente * r for r in valores]
        return ResultadoCircuito(
            tipo=tipo,
            conexion=conexion,
            fuente=fuente,
            valores=valores,
            equivalente=equivalente,
            corriente_total=corriente,
            voltajes=voltajes,
        )

    if tipo == "resistores" and conexion == "paralelo":
        equivalente = 1.0 / sum(1.0 / r for r in valores)
        corriente_total = fuente / equivalente
        corrientes = [fuente / r for r in valores]
        return ResultadoCircuito(
            tipo=tipo,
            conexion=conexion,
            fuente=fuente,
            valores=valores,
            equivalente=equivalente,
            corriente_total=corriente_total,
            corrientes=corrientes,
        )

    if tipo == "capacitores" and conexion == "serie":
        equivalente = 1.0 / sum(1.0 / c for c in valores)
        carga = equivalente * fuente
        voltajes = [carga / c for c in valores]
        cargas = [carga for _ in valores]
        return ResultadoCircuito(
            tipo=tipo,
            conexion=conexion,
            fuente=fuente,
            valores=valores,
            equivalente=equivalente,
            voltajes=voltajes,
            cargas=cargas,
            carga_total=carga,
        )

    equivalente = sum(valores)
    carga_total = equivalente * fuente
    cargas = [c * fuente for c in valores]
    return ResultadoCircuito(
        tipo=tipo,
        conexion=conexion,
        fuente=fuente,
        valores=valores,
        equivalente=equivalente,
        cargas=cargas,
        carga_total=carga_total,
    )


def formatear_si(valor: float, unidad: str = "") -> str:
    """Da formato legible con prefijos SI."""
    if valor == 0:
        return f"0 {unidad}".strip()

    valor_abs = abs(valor)
    escalas = [
        (1e9, "G"),
        (1e6, "M"),
        (1e3, "K"),
        (1.0, ""),
        (1e-3, "m"),
        (1e-6, "u"),
        (1e-9, "n"),
        (1e-12, "p"),
    ]
    for factor, prefijo in escalas:
        if valor_abs >= factor or factor == 1e-12:
            return f"{valor / factor:.6g} {prefijo}{unidad}".strip()
    return f"{valor:.6g} {unidad}".strip()
