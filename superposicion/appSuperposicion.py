"""
appSuperposicion (paquete superposicion)
"""

import tkinter as tk
from tkinter import messagebox

from constantes import Constantes
from .fisicaSuperposicion import MotorFisico
from pantalla_base import PantallaBase
from .paneles import PanelObjetivo, PanelCargas, PanelResultados, PanelGrafica


class Aplicacion(PantallaBase):
    def __init__(self, root):
        super().__init__(root)
        self.configurar_ventana("Principio de Superposición – Ley de Coulomb")
        self._construir_interfaz()

    def _construir_interfaz(self):
        C = Constantes

        self.crear_encabezado("⚡  PRINCIPIO DE SUPERPOSICIÓN", "Ley de Coulomb")

        principal = self.crear_contenedor_principal()
        izquierda = self.crear_columna_izquierda(principal)

        self._panel_objetivo   = PanelObjetivo(izquierda)
        self._panel_cargas     = PanelCargas(izquierda)
        self._construir_botones(izquierda)
        self._panel_resultados = PanelResultados(izquierda)

        derecha = self.crear_columna_derecha(principal)

        self._panel_grafica = PanelGrafica(derecha)

    def _construir_botones(self, contenedor):
        C = Constantes
        fila = self.crear_fila_botones(contenedor)

        self.crear_boton(
            fila,
            texto="⚡  CALCULAR FUERZA NETA",
            comando=self._calcular,
            bg=C.ACCENT,
            fg=C.DARK_BG,
            fuente=("Courier New", 11, "bold"),
        ).pack(side="left", padx=(0, 8))

        self.crear_boton(
            fila,
            texto="↺  Limpiar",
            comando=self._limpiar,
            bg=C.INPUT_BG,
            fg=C.TEXT_MUTED,
            fuente=C.SMALL,
            padx=10,
        ).pack(side="left")

    def _calcular(self):
        try:
            q_obj, x_obj, y_obj = self._panel_objetivo.obtener_valores()
        except ValueError as e:
            messagebox.showerror("Error – Carga objetivo", str(e))
            return

        if not self._panel_cargas.hay_cargas():
            messagebox.showwarning(
                "Sin cargas fuente",
                "Agrega al menos una carga fuente con  ＋ Agregar carga."
            )
            return

        try:
            cargas_fuente = self._panel_cargas.obtener_todas()
        except ValueError as e:
            messagebox.showerror("Error – Cargas fuente", str(e))
            return

        try:
            Fx, Fy, magnitud, angulo, detalles = MotorFisico.fuerza_neta(
                cargas_fuente, q_obj, (x_obj, y_obj)
            )
        except ValueError as e:
            messagebox.showerror("Error físico", str(e))
            return

        self._panel_resultados.mostrar(Fx, Fy, magnitud, angulo, detalles)
        self._panel_grafica.dibujar(
            cargas_fuente, q_obj, (x_obj, y_obj), Fx, Fy, detalles
        )

    def _limpiar(self):
        self._panel_objetivo.limpiar()
        self._panel_cargas.limpiar()
        self._panel_resultados.limpiar()
        self._panel_grafica.limpiar()

    def iniciar(self, geometria=None):
        if geometria:
            self._root.geometry(geometria)
        self._root.mainloop()
