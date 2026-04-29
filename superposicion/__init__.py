"""Paquete superposicion

Exporta nombres principales para facilitar las importaciones desde
`main.py` y otros módulos externos.
"""
from .appSuperposicion import Aplicacion
from constantes import Constantes
from pantalla_base import PantallaBase

__all__ = ["Aplicacion", "Constantes", "PantallaBase"]
