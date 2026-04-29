"""
widgets (paquete superposicion)
Componentes reutilizables.
"""

import tkinter as tk
from constantes import Constantes


def hacer_titulo_seccion(contenedor, titulo):
    C = Constantes
    fila = tk.Frame(contenedor, bg=C.DARK_BG)
    fila.pack(fill="x", pady=(10, 2))

    tk.Label(
        fila, text=f"▸ {titulo}",
        font=C.SECCION, fg=C.ACCENT2, bg=C.DARK_BG
    ).pack(side="left")

    tk.Frame(fila, bg=C.BORDER, height=1).pack(
        side="left", fill="x", expand=True, padx=8
    )


class CargaWidget:
    def __init__(self, contenedor, numero, callback_borrar):
        self.numero = numero
        C = Constantes

        self.frame = tk.Frame(
            contenedor, bg=C.CARD_BG, pady=4, padx=6,
            highlightbackground=C.BORDER, highlightthickness=1
        )
        self.frame.pack(fill="x", padx=8, pady=3)

        self._lbl_numero = tk.Label(
            self.frame, text=f"q{numero}",
            font=C.SECCION, fg=C.ACCENT, bg=C.CARD_BG, width=3
        )
        self._lbl_numero.grid(row=0, column=0, padx=(4, 8))

        etiquetas = ["Carga (μC)", "x (m)", "y (m)"]
        atributos = ["entrada_q", "entrada_x", "entrada_y"]

        for col, (etiqueta, atributo) in enumerate(
            zip(etiquetas, atributos), start=1
        ):
            tk.Label(
                self.frame, text=etiqueta, font=C.SMALL,
                fg=C.TEXT_MUTED, bg=C.CARD_BG
            ).grid(row=0, column=col * 2 - 1, sticky="w", padx=2)

            entrada = tk.Entry(
                self.frame, width=9, font=C.MONO,
                bg=C.INPUT_BG, fg=C.TEXT_PRIMARY,
                insertbackground=C.ACCENT,
                relief="flat", bd=0,
                highlightbackground=C.BORDER,
                highlightcolor=C.ACCENT,
                highlightthickness=1
            )
            entrada.grid(row=0, column=col * 2, padx=(0, 8))
            setattr(self, atributo, entrada)

        tk.Button(
            self.frame, text="✕", font=C.SMALL,
            fg=C.ACCENT_RED, bg=C.CARD_BG,
            activeforeground="white", activebackground=C.ACCENT_RED,
            relief="flat", bd=0, cursor="hand2",
            command=lambda: callback_borrar(self)
        ).grid(row=0, column=7, padx=4)

    def renombrar(self, nuevo_numero):
        self.numero = nuevo_numero
        self._lbl_numero.config(text=f"q{nuevo_numero}")

    def destruir(self):
        self.frame.destroy()

    def obtener_valores(self):
        try:
            q = float(self.entrada_q.get()) * 1e-6
            x = float(self.entrada_x.get())
            y = float(self.entrada_y.get())
            return q, (x, y)
        except ValueError:
            raise ValueError(
                f"Datos inválidos en la carga q{self.numero}. "
                "Usa números (ejemplo: 2.5, -1, 0)."
            )
