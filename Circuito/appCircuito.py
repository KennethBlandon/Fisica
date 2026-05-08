"""
appCircuito
───────────
Pantalla modular para resolver circuitos simples de resistores
o capacitores en serie o paralelo.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from constantes import Constantes
from pantalla_base import PantallaBase

from .calculos import formatear_si, parse_prefixed_value, resolver_circuito
from .importadores import cargar_desde_archivo


class AplicacionCircuito(PantallaBase):
    def __init__(self, root):
        super().__init__(root)
        self.root.attributes("-fullscreen", True)
        self.configurar_ventana("Circuito Serie o Paralelo", geometry="1280x720")
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        self._filas: list[dict[str, object]] = []
        self._construir_interfaz()
        

    def _construir_interfaz(self):
        self.crear_encabezado("🔌  CIRCUITO SERIE O PARALELO", "Resistores y capacitores")

        principal = self.crear_contenedor_principal()
        izquierda = self.crear_columna_izquierda(principal, width=600)
        derecha = self.crear_columna_derecha(principal)

        self._crear_panel_entrada(izquierda)
        self._crear_panel_grid(izquierda)
        self._crear_panel_salida(derecha)

    def _crear_panel_entrada(self, contenedor):
        C = Constantes
        marco = tk.Frame(
            contenedor, bg=C.CARD_BG, padx=10, pady=10,
            highlightbackground=C.BORDER, highlightthickness=1
        )
        marco.pack(fill="x", pady=(0, 8))

        tk.Label(marco, text="Tipo de componente", font=C.SMALL, fg=C.TEXT_MUTED, bg=C.CARD_BG).grid(row=0, column=0, sticky="w")
        tk.Label(marco, text="Conexión", font=C.SMALL, fg=C.TEXT_MUTED, bg=C.CARD_BG).grid(row=0, column=1, sticky="w", padx=(12, 0))
        tk.Label(marco, text="Batería (V)", font=C.SMALL, fg=C.TEXT_MUTED, bg=C.CARD_BG).grid(row=0, column=2, sticky="w", padx=(12, 0))

        self.tipo_var = tk.StringVar(value="Resistores")
        self.conexion_var = tk.StringVar(value="Serie")
        self.entrada_fuente = tk.Entry(marco, width=12, font=C.MONO, bg=C.INPUT_BG, fg=C.TEXT_PRIMARY, insertbackground=C.ACCENT, relief="flat", bd=0, highlightbackground=C.BORDER, highlightcolor=C.ACCENT, highlightthickness=1)
        self.entrada_fuente.insert(0, "12 V")

        tipo = ttk.Combobox(marco, textvariable=self.tipo_var, values=("Resistores", "Capacitores"), state="readonly", width=16)
        conexion = ttk.Combobox(marco, textvariable=self.conexion_var, values=("Serie", "Paralelo"), state="readonly", width=12)

        tipo.grid(row=1, column=0, sticky="w", pady=(4, 0))
        conexion.grid(row=1, column=1, sticky="w", padx=(12, 0), pady=(4, 0))
        self.entrada_fuente.grid(row=1, column=2, sticky="w", padx=(12, 0), pady=(4, 0))

        botones = tk.Frame(marco, bg=C.CARD_BG)
        botones.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(10, 0))

        self.crear_boton(botones, texto="Cargar TXT/CSV", comando=self._cargar_archivo_texto, bg=C.ACCENT2, fg=C.DARK_BG, fuente=C.SMALL, padx=10, pady=6).pack(side="left", padx=(0, 8))
        self.crear_boton(botones, texto="Cargar Excel", comando=self._cargar_archivo_excel, bg=C.ACCENT2, fg=C.DARK_BG, fuente=C.SMALL, padx=10, pady=6).pack(side="left", padx=(0, 8))
        self.crear_boton(botones, texto="Resolver", comando=self.resolver, bg=C.ACCENT, fg=C.DARK_BG, fuente=("Courier New", 10, "bold"), padx=16, pady=6).pack(side="left")
        self.crear_boton(botones, texto="Limpiar", comando=self.limpiar, bg=C.INPUT_BG, fg=C.TEXT_MUTED, fuente=C.SMALL, padx=10, pady=6).pack(side="left", padx=(8, 0))

    def _crear_panel_grid(self, contenedor):
        C = Constantes
        marco = tk.Frame(
            contenedor, bg=C.CARD_BG, padx=10, pady=10,
            highlightbackground=C.BORDER, highlightthickness=1
        )
        marco.pack(fill="both", expand=False, pady=(0, 8))

        cabecera = tk.Frame(marco, bg=C.CARD_BG)
        cabecera.pack(fill="x")
        self.lbl_valor = tk.Label(cabecera, text="Valor de cada elemento", font=C.SECCION, fg=C.ACCENT2, bg=C.CARD_BG)
        self.lbl_valor.pack(side="left")

        self.lbl_ayuda = tk.Label(cabecera, text="Usa prefijos: p, n, u, m, K, M, G", font=C.SMALL, fg=C.TEXT_MUTED, bg=C.CARD_BG)
        self.lbl_ayuda.pack(side="right")

        self.marco_filas = tk.Frame(marco, bg=C.CARD_BG)
        self.marco_filas.pack(fill="both", expand=True, pady=(8, 0))

        controles = tk.Frame(marco, bg=C.CARD_BG)
        controles.pack(fill="x", pady=(8, 0))
        self.crear_boton(controles, texto="＋ Agregar fila", comando=lambda: self._agregar_fila(""), bg=C.ACCENT2, fg=C.DARK_BG, fuente=C.SMALL, padx=10, pady=6).pack(side="left")
        self.crear_boton(controles, texto="Vaciar filas", comando=self._vaciar_filas, bg=C.INPUT_BG, fg=C.TEXT_MUTED, fuente=C.SMALL, padx=10, pady=6).pack(side="left", padx=(8, 0))

        self._agregar_fila("10 K")
        self._agregar_fila("22 K")

    def _crear_panel_salida(self, contenedor):
        C = Constantes
        tk.Label(contenedor, text="Resultados", font=C.SECCION, fg=C.ACCENT2, bg=C.CARD_BG).pack(anchor="w", pady=(10, 0))

        self.texto = tk.Text(
            contenedor,
            height=22,
            wrap="word",
            font=C.MONO,
            bg=C.CARD_BG,
            fg=C.TEXT_PRIMARY,
            insertbackground=C.ACCENT,
            relief="flat",
            bd=0,
            highlightbackground=C.BORDER,
            highlightcolor=C.ACCENT,
            highlightthickness=1,
        )
        self.texto.pack(fill="both", expand=True, pady=(4, 0))
        self.texto.config(state="disabled")
        self._escribir_salida("Ingresa los datos del circuito y presiona Resolver.")

    def _agregar_fila(self, valor=""):
        C = Constantes
        fila = tk.Frame(self.marco_filas, bg=C.CARD_BG)
        fila.pack(fill="x", pady=3)

        etiqueta = tk.Label(fila, text=f"{len(self._filas)+1}.", font=C.SECCION, fg=C.ACCENT, bg=C.CARD_BG, width=4, anchor="w")
        etiqueta.pack(side="left")

        entrada = tk.Entry(fila, width=18, font=C.MONO, bg=C.INPUT_BG, fg=C.TEXT_PRIMARY, insertbackground=C.ACCENT, relief="flat", bd=0, highlightbackground=C.BORDER, highlightcolor=C.ACCENT, highlightthickness=1)
        entrada.pack(side="left", padx=(0, 8))
        if valor:
            entrada.insert(0, valor)

        boton = self.crear_boton(fila, texto="✕", comando=lambda: self._borrar_fila(fila), bg=C.CARD_BG, fg=C.ACCENT_RED, fuente=C.SMALL, padx=8, pady=4)
        boton.pack(side="left")

        self._filas.append({"frame": fila, "entrada": entrada, "etiqueta": etiqueta})
        self._renumerar_filas()

    def _borrar_fila(self, fila):
        self._filas = [item for item in self._filas if item["frame"] != fila]
        fila.destroy()
        self._renumerar_filas()

    def _renumerar_filas(self):
        for indice, item in enumerate(self._filas, start=1):
            item["etiqueta"].config(text=f"{indice}.")

    def _vaciar_filas(self):
        for item in self._filas:
            item["frame"].destroy()
        self._filas.clear()

    def _leer_valores(self):
        valores = []
        for item in self._filas:
            texto = item["entrada"].get().strip()
            if not texto:
                continue
            valores.append(parse_prefixed_value(texto))
        if not valores:
            raise ValueError("Agrega al menos un resistor o capacitor con valor válido.")
        return valores

    def _tipo_normalizado(self):
        return self.tipo_var.get().strip().lower()

    def _conexion_normalizada(self):
        return self.conexion_var.get().strip().lower()

    def resolver(self):
        try:
            fuente = parse_prefixed_value(self.entrada_fuente.get())
            valores = self._leer_valores()
            resultado = resolver_circuito(self._tipo_normalizado(), self._conexion_normalizada(), fuente, valores)
            self._mostrar_resultado(resultado)
        except Exception as exc:
            messagebox.showerror("Error en circuito", str(exc))

    def _mostrar_resultado(self, resultado):
        tipo = resultado.tipo
        conexion = resultado.conexion
        lineas = []
        lineas.append(f"Tipo: {tipo.title()}")
        lineas.append(f"Conexión: {conexion.title()}")
        lineas.append(f"Batería: {formatear_si(resultado.fuente, 'V')}")
        lineas.append("")

        if tipo == "resistores" and conexion == "serie":
            lineas.append("Ecuación: Req = R1 + R2 + ...")
            lineas.append(f"Resistencia equivalente: {formatear_si(resultado.equivalente, 'Ω')}")
            lineas.append(f"Corriente de la batería: {formatear_si(resultado.corriente_total or 0, 'A')}")
            lineas.append("Voltaje en cada resistor:")
            for indice, voltaje in enumerate(resultado.voltajes or [], start=1):
                lineas.append(f"  R{indice}: {formatear_si(voltaje, 'V')}")

        elif tipo == "resistores" and conexion == "paralelo":
            lineas.append("Ecuación: 1/Req = 1/R1 + 1/R2 + ...")
            lineas.append("Entonces Req = (1/R1 + 1/R2 + ...)^-1")
            lineas.append(f"Resistencia equivalente: {formatear_si(resultado.equivalente, 'Ω')}")
            lineas.append(f"Corriente de la batería: {formatear_si(resultado.corriente_total or 0, 'A')}")
            lineas.append("Corriente en cada resistor:")
            for indice, corriente in enumerate(resultado.corrientes or [], start=1):
                lineas.append(f"  R{indice}: {formatear_si(corriente, 'A')}")

        elif tipo == "capacitores" and conexion == "serie":
            lineas.append("Ecuación: 1/Ceq = 1/C1 + 1/C2 + ...")
            lineas.append("Entonces Ceq = (1/C1 + 1/C2 + ...)^-1")
            lineas.append(f"Capacitancia equivalente: {formatear_si(resultado.equivalente, 'F')}")
            lineas.append(f"Carga en cada capacitor: {formatear_si(resultado.carga_total or 0, 'C')}")
            lineas.append("Voltaje en cada capacitor:")
            for indice, voltaje in enumerate(resultado.voltajes or [], start=1):
                lineas.append(f"  C{indice}: {formatear_si(voltaje, 'V')}")

        else:
            lineas.append("Ecuación: Ceq = C1 + C2 + ...")
            lineas.append(f"Capacitancia equivalente: {formatear_si(resultado.equivalente, 'F')}")
            lineas.append(f"Carga total: {formatear_si(resultado.carga_total or 0, 'C')}")
            lineas.append("Carga en cada capacitor:")
            for indice, carga in enumerate(resultado.cargas or [], start=1):
                lineas.append(f"  C{indice}: {formatear_si(carga, 'C')}")

        self._escribir_salida("\n".join(lineas))

 

    def _escribir_salida(self, texto):
        self.texto.config(state="normal")
        self.texto.delete("1.0", "end")
        self.texto.insert("1.0", texto)
        self.texto.config(state="disabled")

    def _cargar_archivo_texto(self):
        self._cargar_archivo(("Archivos de texto", "*.txt *.csv"))

    def _cargar_archivo_excel(self):
        self._cargar_archivo(("Excel", "*.xlsx *.xlsm"))

    def _cargar_archivo(self, filtro):
        ruta = filedialog.askopenfilename(filetypes=[filtro, ("Todos", "*.*")])
        if not ruta:
            return
        try:
            fuente, valores = cargar_desde_archivo(ruta)
            self.entrada_fuente.delete(0, "end")
            self.entrada_fuente.insert(0, formatear_si(fuente, "V"))
            self._vaciar_filas()
            for valor in valores:
                self._agregar_fila(formatear_si(valor, ""))
            self._escribir_salida(f"Archivo cargado: {ruta}\n\nPresiona Resolver para ver el resultado.")
        except Exception as exc:
            messagebox.showerror("Error al cargar archivo", str(exc))

    def limpiar(self):
        self.tipo_var.set("Resistores")
        self.conexion_var.set("Serie")
        self.entrada_fuente.delete(0, "end")
        self.entrada_fuente.insert(0, "12 V")
        self._vaciar_filas()
        self._agregar_fila("10 K")
        self._agregar_fila("22 K")
        self._escribir_salida("Ingresa los datos del circuito y presiona Resolver.")
