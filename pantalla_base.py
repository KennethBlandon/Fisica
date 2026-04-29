"""
pantalla_base
─────────────
Base reutilizable para construir pantallas Tkinter del proyecto.
"""

import tkinter as tk

from constantes import Constantes


class PantallaBase:
    def __init__(self, root):
        self.root = root
        self.C = Constantes

    def configurar_ventana(self, titulo, fullscreen=False, geometry=None):
        self.root.title(titulo)
        self.root.configure(bg=self.C.DARK_BG)
        self.root.resizable(False, False)

        if fullscreen:
            self.root.attributes("-fullscreen", True)

        if geometry:
            # tamaño inicial
            self.root.geometry(geometry)
            # bloquear tamaño para que no cambie
            w, h = geometry.split("x")
            self.root.minsize(int(w), int(h))
            self.root.maxsize(int(w), int(h))

    def crear_encabezado(self, titulo, subtitulo):
        encabezado = tk.Frame(self.root, bg=self.C.DARK_BG)
        encabezado.pack(fill="x", padx=20, pady=(18, 4))

        tk.Label(
            encabezado,
            text=titulo,
            font=self.C.TITULO,
            fg=self.C.ACCENT,
            bg=self.C.DARK_BG,
        ).pack(side="left")

        tk.Label(
            encabezado,
            text=subtitulo,
            font=("Courier New", 10),
            fg=self.C.TEXT_MUTED,
            bg=self.C.DARK_BG,
        ).pack(side="left", padx=12, pady=4)

        tk.Frame(self.root, bg=self.C.BORDER, height=1).pack(
            fill="x", padx=20, pady=4
        )

    def crear_contenedor_principal(self):
        contenedor = tk.Frame(self.root, bg=self.C.DARK_BG)
        contenedor.pack(fill="both", expand=True, padx=20, pady=6)
        return contenedor

    def crear_columna_izquierda(self, contenedor, width=460):
        izquierda = tk.Frame(contenedor, bg=self.C.DARK_BG, width=width)
        izquierda.pack(side="left", fill="both", expand=False, padx=(0, 12))
        izquierda.pack_propagate(False)
        return izquierda

    def crear_columna_derecha(self, contenedor):
        derecha = tk.Frame(
            contenedor,
            bg=self.C.CARD_BG,
            highlightbackground=self.C.BORDER,
            highlightthickness=1,
        )
        derecha.pack(side="left", fill="both", expand=True)
        return derecha

    def crear_fila_botones(self, contenedor):
        fila = tk.Frame(contenedor, bg=self.C.DARK_BG)
        fila.pack(fill="x", pady=10)
        return fila

    def crear_boton(
        self,
        contenedor,
        *,
        texto,
        comando,
        bg,
        fg=None,
        fuente=None,
        padx=18,
        pady=8,
        ancho=None,
    ):
        boton = tk.Button(
            contenedor,
            text=texto,
            command=comando,
            font=fuente or self.C.SMALL,
            fg=fg or self.C.TEXT_PRIMARY,
            bg=bg,
            activebackground=bg,
            relief="flat",
            bd=0,
            padx=padx,
            pady=pady,
            cursor="hand2",
        )
        if ancho is not None:
            boton.configure(width=ancho)
        return boton
