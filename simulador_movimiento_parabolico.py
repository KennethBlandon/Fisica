import tkinter as tk
from tkinter import messagebox, ttk

"""Interfaz principal del simulador de movimiento parabólico."""

from physics import (
    calcular_angulo_apuntado,
    calcular_altura_para_intercepcion,
    calcular_intercepcion,
    calcular_retraso_para_intercepcion,
    calcular_trayectoria,
    construir_puntos_objeto,
    evaluar_cazador_mono,
    reajustar_posicion_mono_por_velocidad,
)


CANVAS_WIDTH = 980
CANVAS_HEIGHT = 700
PADDING = 45
ANIMATION_DELAY_MS = 40


class SimuladorMovimientoParabolico:
    """Interfaz principal del simulador y controlador de la vista."""

    def __init__(self, raiz):
        """Inicializa la ventana, los controles y el estado de simulación."""
        self.raiz = raiz
        self.raiz.title("Simulador de movimiento parabolico")
        self.raiz.geometry("1440x920")
        self.raiz.minsize(1220, 780)

        self.campos = {}
        self.simulacion_actual = None
        self.escena_actual = None
        self.animacion_activa = False
        self.animacion_job = None
        self.indice_animacion = 0
        self.zoom_mapa = 1.0
        self.desplazamiento_mapa_x = 0.0
        self.desplazamiento_mapa_y = 0.0
        self.arrastre_previo = None
        self.visor_resultados = None
        self.resumen_resultados = None
        self.tabla_resultados = None
        self.modo_cazador_mono = tk.BooleanVar(value=False)
        self.velocidad_referencia_mono = None
        self.resultado_var = tk.StringVar(
            value="Ingresa los datos y presiona 'Simular' para ver la trayectoria."
        )

        self._crear_interfaz()
        self._cargar_ejemplo()

    def _crear_interfaz(self):
        """Construye el formulario de entrada, el mapa y los controles visuales."""
        contenedor = ttk.Frame(self.raiz, padding=18)
        contenedor.pack(fill="both", expand=True)
        contenedor.columnconfigure(0, weight=0)
        contenedor.columnconfigure(1, weight=1)
        contenedor.rowconfigure(0, weight=1)

        panel_controles = ttk.LabelFrame(contenedor, text="Datos de entrada", padding=16)
        panel_controles.grid(row=0, column=0, sticky="ns", padx=(0, 16))

        definiciones = [
            ("velocidad", "Velocidad inicial v0 (m/s)", "25"),
            ("angulo", "Angulo de lanzamiento (grados)", "45"),
            ("altura", "Altura inicial H (m)", "0"),
            ("gravedad", "Gravedad g (m/s²)", "9.8"),
            ("objeto_x", "Posicion horizontal del objeto en caida (m)", "25"),
            ("objeto_altura", "Altura inicial del objeto en caida (m)", "20"),
            ("retraso", "Retraso de la caida del objeto (s)", "0"),
            ("muestras", "Cantidad de puntos a simular", "80"),
        ]

        for fila, (clave, etiqueta, valor) in enumerate(definiciones):
            ttk.Label(panel_controles, text=etiqueta).grid(row=fila * 2, column=0, sticky="w")
            entrada = ttk.Entry(panel_controles, width=24)
            entrada.grid(row=(fila * 2) + 1, column=0, sticky="ew", pady=(0, 12))
            entrada.insert(0, valor)
            self.campos[clave] = entrada

        ttk.Checkbutton(
            panel_controles,
            text="Modo cazador y mono",
            variable=self.modo_cazador_mono,
            command=self._actualizar_modo_cazador_mono,
        ).grid(row=len(definiciones) * 2, column=0, sticky="w", pady=(4, 8))

        botones_row = (len(definiciones) * 2) + 1
        ttk.Button(panel_controles, text="Simular", command=self.simular).grid(
            row=botones_row, column=0, sticky="ew", pady=(6, 8)
        )
        ttk.Button(panel_controles, text="Cargar ejemplo", command=self._cargar_ejemplo).grid(
            row=botones_row + 1, column=0, sticky="ew"
        )
        ttk.Button(panel_controles, text="Ejemplo cazador y mono", command=self._cargar_ejemplo_cazador_mono).grid(
            row=botones_row + 2, column=0, sticky="ew", pady=(8, 0)
        )

        ayuda = (
            "Formulas usadas:\n"
            "x = v0 * cos(a) * t\n"
            "y = H + v0 * sin(a) * t - 0.5 * g * t^2\n"
            "y_obj = H_obj - 0.5 * g * (t - retraso)^2\n"
            "vx = v0 * cos(a)\n"
            "vy = v0 * sin(a) - g * t\n"
            "Modo cazador y mono: a = atan((H_obj - H) / x_obj), retraso = 0"
        )
        ttk.Label(panel_controles, text=ayuda, justify="left").grid(
            row=botones_row + 3, column=0, sticky="w", pady=(18, 0)
        )

        panel_mapa = ttk.Frame(contenedor)
        panel_mapa.grid(row=0, column=1, sticky="nsew")
        panel_mapa.columnconfigure(0, weight=1)
        panel_mapa.rowconfigure(1, weight=1)

        barra_mapa = ttk.Frame(panel_mapa)
        barra_mapa.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        barra_mapa.columnconfigure(4, weight=1)

        ttk.Button(barra_mapa, text="Ver resultados", command=self.abrir_resultados).grid(
            row=0, column=0, sticky="w", padx=(0, 8)
        )
        ttk.Button(barra_mapa, text="Animar", command=self.animar).grid(row=0, column=1, sticky="w", padx=(0, 8))
        ttk.Button(barra_mapa, text="Calcular altura", command=self.calcular_altura_automatica).grid(
            row=0, column=2, sticky="w", padx=(0, 8)
        )
        ttk.Button(barra_mapa, text="Calcular retraso", command=self.calcular_retraso_automatico).grid(
            row=0, column=3, sticky="w", padx=(0, 8)
        )
        ttk.Button(barra_mapa, text="Restablecer vista", command=self.restablecer_vista_mapa).grid(
            row=0, column=4, sticky="e", padx=(8, 8)
        )
        ttk.Label(
            barra_mapa,
            text="Explora el mapa con rueda del mouse para zoom y arrastre con clic izquierdo.",
            justify="right",
        ).grid(row=0, column=5, sticky="e")

        self.canvas = tk.Canvas(
            panel_mapa,
            width=CANVAS_WIDTH,
            height=CANVAS_HEIGHT,
            bg="#fcfcfc",
            highlightthickness=1,
            highlightbackground="#bdbdbd",
        )
        self.canvas.grid(row=1, column=0, sticky="nsew")
        self.canvas.bind("<MouseWheel>", self._zoom_mapa)
        self.canvas.bind("<ButtonPress-1>", self._iniciar_arrastre)
        self.canvas.bind("<B1-Motion>", self._arrastrar_mapa)
        self.canvas.bind("<ButtonRelease-1>", self._finalizar_arrastre)

    def _cargar_ejemplo(self):
        """Carga un escenario de ejemplo general."""
        self.modo_cazador_mono.set(False)
        valores = {
            "velocidad": "28",
            "angulo": "52",
            "altura": "1.5",
            "gravedad": "9.8",
            "objeto_x": "40",
            "objeto_altura": "39.6",
            "retraso": "0",
            "muestras": "100",
        }
        for clave, valor in valores.items():
            self.campos[clave].delete(0, tk.END)
            self.campos[clave].insert(0, valor)
        self._actualizar_modo_cazador_mono()
        self.simular()

    def _cargar_ejemplo_cazador_mono(self):
        """Carga un escenario de ejemplo para el experimento cazador y mono."""
        self.modo_cazador_mono.set(True)
        valores = {
            "velocidad": "32",
            "angulo": "35",
            "altura": "1.5",
            "gravedad": "9.8",
            "objeto_x": "25",
            "objeto_altura": "18",
            "retraso": "0",
            "muestras": "100",
        }
        for clave, valor in valores.items():
            self.campos[clave].delete(0, tk.END)
            self.campos[clave].insert(0, valor)
        self._actualizar_modo_cazador_mono()
        self.velocidad_referencia_mono = float(valores["velocidad"])
        self.simular()

    def _actualizar_modo_cazador_mono(self):
        """Bloquea o ajusta entradas cuando el modo cazador y mono está activo."""
        if self.modo_cazador_mono.get():
            try:
                altura = float(self.campos["altura"].get())
                objeto_altura = float(self.campos["objeto_altura"].get())
                objeto_x = float(self.campos["objeto_x"].get())
            except ValueError:
                return

            if objeto_x > 0:
                angulo = calcular_angulo_apuntado(altura, objeto_altura, objeto_x)
                self.campos["angulo"].configure(state="normal")
                self.campos["angulo"].delete(0, tk.END)
                self.campos["angulo"].insert(0, f"{angulo:.3f}")
                self.campos["angulo"].configure(state="disabled")

            self.campos["retraso"].configure(state="normal")
            self.campos["retraso"].delete(0, tk.END)
            self.campos["retraso"].insert(0, "0")
            self.campos["retraso"].configure(state="disabled")
        else:
            self.campos["angulo"].configure(state="normal")
            self.campos["retraso"].configure(state="normal")

    def _leer_entradas(self):
        """Lee y convierte los valores numéricos ingresados por el usuario."""
        try:
            return {
                "velocidad": float(self.campos["velocidad"].get()),
                "angulo": float(self.campos["angulo"].get()),
                "altura": float(self.campos["altura"].get()),
                "gravedad": float(self.campos["gravedad"].get()),
                "objeto_x": float(self.campos["objeto_x"].get()),
                "objeto_altura": float(self.campos["objeto_altura"].get()),
                "retraso": float(self.campos["retraso"].get()),
                "muestras": int(self.campos["muestras"].get()),
            }, None
        except ValueError:
            return None, "Todos los campos deben ser numericos."

    def _validar_entradas(self, valores):
        """Verifica rangos y restricciones físicas básicas de la simulación."""
        if valores["velocidad"] <= 0:
            return "La velocidad inicial debe ser mayor que cero."
        if valores["gravedad"] < 0:
            return "La gravedad no puede ser negativa."
        if valores["altura"] < 0:
            return "La altura inicial no puede ser negativa."
        if valores["objeto_altura"] < 0:
            return "La altura del objeto en caida no puede ser negativa."
        if valores["objeto_x"] <= 0:
            return "La posicion horizontal del objeto debe ser mayor que cero."
        if valores["retraso"] < 0:
            return "El retraso de la caida no puede ser negativo."
        if not 0 < valores["angulo"] < 90:
            return "El angulo debe estar entre 0 y 90 grados."
        if valores["muestras"] < 20 or valores["muestras"] > 300:
            return "La cantidad de puntos debe estar entre 20 y 300 para una simulacion estable."
        if self.modo_cazador_mono.get() and valores["objeto_altura"] <= valores["altura"]:
            return "En el modo cazador y mono, el objeto suspendido debe estar por encima del lanzador."
        return None

    def _construir_simulacion(self, valores):
        """Genera todos los datos derivados necesarios para dibujar y reportar."""
        valores = dict(valores)
        if self.modo_cazador_mono.get():
            valores["angulo"] = calcular_angulo_apuntado(valores["altura"], valores["objeto_altura"], valores["objeto_x"])
            valores["retraso"] = 0.0

        datos = calcular_trayectoria(
            valores["velocidad"],
            valores["angulo"],
            valores["altura"],
            valores["gravedad"],
            valores["muestras"],
        )
        puntos_objeto = construir_puntos_objeto(
            datos["puntos"],
            valores["objeto_altura"],
            valores["objeto_x"],
            valores["gravedad"],
            valores["retraso"],
        )
        intercepcion = calcular_intercepcion(
            datos,
            valores["objeto_altura"],
            valores["objeto_x"],
            valores["gravedad"],
            valores["retraso"],
        )
        return {
            "entradas": valores,
            "datos": datos,
            "puntos_objeto": puntos_objeto,
            "intercepcion": intercepcion,
            "modo_cazador_mono": self.modo_cazador_mono.get(),
            "analisis_cazador_mono": evaluar_cazador_mono(
                datos,
                valores["altura"],
                valores["objeto_altura"],
                valores["objeto_x"],
                valores["gravedad"],
            ) if self.modo_cazador_mono.get() else None,
        }

    def simular(self):
        """Ejecuta la simulación completa con los valores actuales de entrada."""
        if self.modo_cazador_mono.get():
            self._actualizar_modo_cazador_mono()
        valores, error = self._leer_entradas()
        if error:
            messagebox.showerror("Entrada invalida", error)
            return

        error = self._validar_entradas(valores)
        if error:
            messagebox.showerror("Entrada invalida", error)
            return

        if self.modo_cazador_mono.get():
            self._reajustar_mono_por_velocidad(valores)

        self._detener_animacion()
        self.simulacion_actual = self._construir_simulacion(valores)
        self.velocidad_referencia_mono = valores["velocidad"]
        self._refrescar_vista()

    def _reajustar_mono_por_velocidad(self, valores):
        """Ajusta la posición del mono cuando cambia la velocidad inicial del proyectil."""
        if self.velocidad_referencia_mono is None:
            self.velocidad_referencia_mono = valores["velocidad"]
            return

        if abs(self.velocidad_referencia_mono - valores["velocidad"]) < 1e-9:
            return

        nuevo_x, nueva_altura = reajustar_posicion_mono_por_velocidad(
            valores["altura"],
            valores["objeto_x"],
            valores["objeto_altura"],
            self.velocidad_referencia_mono,
            valores["velocidad"],
        )
        valores["objeto_x"] = nuevo_x
        valores["objeto_altura"] = nueva_altura
        self.campos["objeto_x"].delete(0, tk.END)
        self.campos["objeto_x"].insert(0, f"{nuevo_x:.3f}")
        self.campos["objeto_altura"].delete(0, tk.END)
        self.campos["objeto_altura"].insert(0, f"{nueva_altura:.3f}")
        self._actualizar_modo_cazador_mono()

    def _refrescar_vista(self):
        """Redibuja mapa, resultados y tabla a partir de la simulación activa."""
        if not self.simulacion_actual:
            return
        entradas = self.simulacion_actual["entradas"]
        datos = self.simulacion_actual["datos"]
        intercepcion = self.simulacion_actual["intercepcion"]
        self._mostrar_resultados(
            datos,
            entradas["altura"],
            entradas["gravedad"],
            entradas["objeto_altura"],
            entradas["objeto_x"],
            entradas["retraso"],
            intercepcion,
            self.simulacion_actual["modo_cazador_mono"],
            self.simulacion_actual["analisis_cazador_mono"],
        )
        self._dibujar_trayectoria(
            datos,
            self.simulacion_actual["puntos_objeto"],
            entradas["objeto_altura"],
            entradas["objeto_x"],
            intercepcion,
        )
        self._actualizar_visor_resultados(datos["puntos"], self.simulacion_actual["puntos_objeto"])

    def _llenar_tabla(self, puntos_proyectil, puntos_objeto):
        """Rellena la tabla resumida con una muestra de puntos de ambos cuerpos."""
        if not self.tabla_resultados:
            return
        self.tabla_resultados.delete(*self.tabla_resultados.get_children())
        paso = max(1, len(puntos_proyectil) // 18)
        for indice in range(0, len(puntos_proyectil), paso):
            punto_p = puntos_proyectil[indice]
            punto_o = puntos_objeto[indice]
            self.tabla_resultados.insert(
                "",
                tk.END,
                values=(
                    f"{punto_p['t']:.2f}",
                    f"{punto_p['x']:.2f}",
                    f"{punto_p['y']:.2f}",
                    f"{punto_p['vy']:.2f}",
                    f"{punto_o['x']:.2f}",
                    f"{punto_o['y']:.2f}",
                    f"{punto_o['vy']:.2f}",
                ),
            )

    def _crear_visor_resultados(self):
        """Crea la ventana secundaria donde se muestran resultados y tabla."""
        visor = tk.Toplevel(self.raiz)
        visor.title("Resultados de la simulacion")
        visor.geometry("760x720")
        visor.minsize(680, 560)
        visor.withdraw()
        visor.protocol("WM_DELETE_WINDOW", visor.withdraw)

        contenedor = ttk.Frame(visor, padding=16)
        contenedor.pack(fill="both", expand=True)
        contenedor.columnconfigure(0, weight=1)
        contenedor.rowconfigure(1, weight=1)
        contenedor.rowconfigure(2, weight=1)

        ttk.Label(contenedor, text="Resultados", font=("Segoe UI", 14, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 8)
        )

        self.resumen_resultados = tk.Text(contenedor, wrap="word", height=14)
        self.resumen_resultados.grid(row=1, column=0, sticky="nsew", pady=(0, 12))
        self.resumen_resultados.configure(state="disabled")

        columnas = ("t", "x_p", "y_p", "vy_p", "x_o", "y_o", "vy_o")
        panel_tabla = ttk.LabelFrame(contenedor, text="Tabla de simulacion", padding=8)
        panel_tabla.grid(row=2, column=0, sticky="nsew")
        panel_tabla.columnconfigure(0, weight=1)
        panel_tabla.rowconfigure(0, weight=1)

        self.tabla_resultados = ttk.Treeview(panel_tabla, columns=columnas, show="headings", height=12)
        encabezados = {
            "t": "t (s)",
            "x_p": "x proyectil",
            "y_p": "y proyectil",
            "vy_p": "vy proyectil",
            "x_o": "x objeto",
            "y_o": "y objeto",
            "vy_o": "vy objeto",
        }
        for columna in columnas:
            self.tabla_resultados.heading(columna, text=encabezados[columna])
            self.tabla_resultados.column(columna, anchor="center", width=100)
        self.tabla_resultados.grid(row=0, column=0, sticky="nsew")

        scroll = ttk.Scrollbar(panel_tabla, orient="vertical", command=self.tabla_resultados.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.tabla_resultados.configure(yscrollcommand=scroll.set)

        self.visor_resultados = visor

    def abrir_resultados(self):
        """Muestra la ventana secundaria de resultados."""
        if not self.visor_resultados or not self.visor_resultados.winfo_exists():
            self._crear_visor_resultados()
        self._actualizar_visor_resultados()
        self.visor_resultados.deiconify()
        self.visor_resultados.lift()
        self.visor_resultados.focus_force()

    def _actualizar_visor_resultados(self, puntos_proyectil=None, puntos_objeto=None):
        """Sincroniza el resumen y la tabla de la ventana secundaria."""
        if not self.visor_resultados or not self.visor_resultados.winfo_exists():
            return
        if self.simulacion_actual and (puntos_proyectil is None or puntos_objeto is None):
            puntos_proyectil = self.simulacion_actual["datos"]["puntos"]
            puntos_objeto = self.simulacion_actual["puntos_objeto"]
        if self.resumen_resultados:
            self.resumen_resultados.configure(state="normal")
            self.resumen_resultados.delete("1.0", tk.END)
            self.resumen_resultados.insert("1.0", self.resultado_var.get())
            self.resumen_resultados.configure(state="disabled")
        if puntos_proyectil is not None and puntos_objeto is not None:
            self._llenar_tabla(puntos_proyectil, puntos_objeto)

    def restablecer_vista_mapa(self):
        """Devuelve el mapa a su zoom y desplazamiento iniciales."""
        self.zoom_mapa = 1.0
        self.desplazamiento_mapa_x = 0.0
        self.desplazamiento_mapa_y = 0.0
        if self.simulacion_actual:
            self._refrescar_vista()

    def _zoom_mapa(self, evento):
        """Ajusta el zoom del mapa con la rueda del mouse."""
        if not self.simulacion_actual:
            return
        factor = 1.1 if evento.delta > 0 else 0.9
        nuevo_zoom = max(0.5, min(3.5, self.zoom_mapa * factor))
        if abs(nuevo_zoom - self.zoom_mapa) < 1e-9:
            return
        self.zoom_mapa = nuevo_zoom
        self._refrescar_vista()

    def _iniciar_arrastre(self, evento):
        """Registra el punto inicial del arrastre del mapa."""
        self.arrastre_previo = (evento.x, evento.y)

    def _arrastrar_mapa(self, evento):
        """Desplaza el mapa mientras se mantiene presionado el mouse."""
        if not self.simulacion_actual or not self.arrastre_previo:
            return
        previo_x, previo_y = self.arrastre_previo
        self.desplazamiento_mapa_x += evento.x - previo_x
        self.desplazamiento_mapa_y += evento.y - previo_y
        self.arrastre_previo = (evento.x, evento.y)
        self._refrescar_vista()

    def _finalizar_arrastre(self, _evento):
        """Cierra el gesto de arrastre del mapa."""
        self.arrastre_previo = None

    def _mostrar_resultados(self, datos, altura_inicial, gravedad, objeto_altura, objeto_x, retraso, intercepcion, modo_cazador_mono, analisis_cazador_mono):
        """Construye el texto explicativo que se muestra al usuario."""
        estado_intercepcion = "Si" if intercepcion["hay_intercepcion"] else "No"
        etiqueta_tiempo = "Tiempo total de vuelo" if datos.get("impacto_suelo", True) else "Tiempo de simulacion"
        nota_gravedad = ""
        if gravedad == 0:
            nota_gravedad = "Con gravedad 0 no hay aceleracion vertical y la trayectoria es lineal en Y."
        resumen = [
            f"Componente horizontal vx: {datos['vx']:.2f} m/s",
            f"Componente vertical inicial vy0: {datos['vy0']:.2f} m/s",
            f"{etiqueta_tiempo}: {datos['tiempo_vuelo']:.2f} s",
            f"Tiempo hasta la altura maxima: {datos['tiempo_altura_maxima']:.2f} s",
            f"Altura maxima: {datos['altura_maxima']:.2f} m",
            f"Alcance horizontal: {datos['alcance_horizontal']:.2f} m",
            f"Objeto en caida: x = {objeto_x:.2f} m, altura = {objeto_altura:.2f} m, retraso = {retraso:.2f} s",
            f"Intercepcion: {estado_intercepcion}",
            f"Aceleracion horizontal ax: 0.00 m/s²",
            f"Aceleracion vertical ay: {-gravedad:.2f} m/s²",
        ]
        if nota_gravedad:
            resumen.append(nota_gravedad)

        if modo_cazador_mono and analisis_cazador_mono:
            resumen.extend(
                [
                    "",
                    "Experimento cazador y mono:",
                    "El angulo se fija apuntando a la posicion inicial del objeto suspendido y la caida comienza en t = 0 s.",
                    f"Distancia directa al mono: {analisis_cazador_mono['distancia_directa']:.2f} m",
                    f"Tiempo teorico de encuentro: {analisis_cazador_mono['tiempo_teorico']:.2f} s",
                    f"Tiempo para tocar el suelo: {analisis_cazador_mono['tiempo_caida_mono']:.2f} s",
                    (
                        "Conclusion: con estas condiciones ideales, el proyectil y el mono caen con la misma aceleracion y se interceptan."
                        if analisis_cazador_mono["exito_teorico"]
                        else "Conclusion: el principio del experimento sigue siendo valido, pero con esta velocidad el mono toca el suelo antes del encuentro."
                    ),
                    "La garantia de intercepcion no aplica si el objeto suspendido empieza a caer mas tarde.",
                ]
            )

        resumen.extend(
            [
                "",
                f"Analisis en x = {objeto_x:.2f} m:",
                f"t = {intercepcion.get('tiempo', 0.0):.2f} s",
                f"Altura del proyectil = {intercepcion.get('y_proyectil', 0.0):.2f} m",
                f"Altura del objeto = {intercepcion.get('y_objeto', 0.0):.2f} m",
                f"Resultado: {intercepcion['motivo']}",
                "",
                "Ecuaciones aplicadas:",
                f"x(t) = {datos['vx']:.2f} * t",
                f"y(t) = {altura_inicial:.2f} + {datos['vy0']:.2f} * t - 0.5 * {gravedad:.2f} * t²",
                f"y_obj(t) = {objeto_altura:.2f} - 0.5 * {gravedad:.2f} * (t - {retraso:.2f})²",
            ]
        )
        self.resultado_var.set("\n".join(resumen))

    def _dibujar_trayectoria(self, datos, puntos_objeto, objeto_altura, objeto_x, intercepcion):
        """Dibuja la trayectoria del proyectil, el objeto y las referencias visuales."""
        self.canvas.delete("all")

        puntos = datos["puntos"]
        max_x = max(max(punto["x"] for punto in puntos), objeto_x) or 1.0
        max_y = max(max(punto["y"] for punto in puntos), objeto_altura, max(punto["y"] for punto in puntos_objeto)) or 1.0
        ancho_canvas = max(CANVAS_WIDTH, self.canvas.winfo_width())
        alto_canvas = max(CANVAS_HEIGHT, self.canvas.winfo_height())
        escala_x = (ancho_canvas - (2 * PADDING)) / max_x
        escala_y = (alto_canvas - (2 * PADDING)) / max_y
        escala = min(escala_x, escala_y) * self.zoom_mapa

        origen_x = PADDING + self.desplazamiento_mapa_x
        origen_y = alto_canvas - PADDING + self.desplazamiento_mapa_y

        self.canvas.create_line(origen_x, origen_y, ancho_canvas - 12, origen_y, width=2, arrow=tk.LAST)
        self.canvas.create_line(origen_x, origen_y, origen_x, 12, width=2, arrow=tk.LAST)
        self.canvas.create_text(ancho_canvas - 20, origen_y - 14, text="X (m)", fill="#333333")
        self.canvas.create_text(origen_x + 22, 18, text="Y (m)", fill="#333333")

        self.escena_actual = {
            "escala": escala,
            "origen_x": origen_x,
            "origen_y": origen_y,
            "puntos_proyectil": puntos,
            "puntos_objeto": puntos_objeto,
            "objeto_x": objeto_x,
        }

        coordenadas = []
        for punto in puntos:
            pantalla_x = origen_x + (punto["x"] * escala)
            pantalla_y = origen_y - (punto["y"] * escala)
            coordenadas.extend((pantalla_x, pantalla_y))

        self.canvas.create_line(*coordenadas, fill="#0b6efd", width=3, smooth=True)

        coordenadas_objeto = []
        for punto in puntos_objeto:
            pantalla_x = origen_x + (punto["x"] * escala)
            pantalla_y = origen_y - (punto["y"] * escala)
            coordenadas_objeto.extend((pantalla_x, pantalla_y))

        self.canvas.create_line(*coordenadas_objeto, fill="#6f42c1", width=3, dash=(5, 3), smooth=True)

        for marca in range(6):
            valor_x = max_x * marca / 5
            pos_x = origen_x + (valor_x * escala)
            self.canvas.create_line(pos_x, origen_y - 5, pos_x, origen_y + 5, fill="#666666")
            self.canvas.create_text(pos_x, origen_y + 18, text=f"{valor_x:.1f}", fill="#333333")

            valor_y = max_y * marca / 5
            pos_y = origen_y - (valor_y * escala)
            self.canvas.create_line(origen_x - 5, pos_y, origen_x + 5, pos_y, fill="#666666")
            self.canvas.create_text(origen_x - 24, pos_y, text=f"{valor_y:.1f}", fill="#333333")

        altura_pantalla = origen_y - (puntos[0]["y"] * escala)
        self.canvas.create_oval(origen_x - 5, altura_pantalla - 5, origen_x + 5, altura_pantalla + 5, fill="#dc3545")
        self.canvas.create_text(origen_x + 70, altura_pantalla - 12, text="Inicio", fill="#dc3545")

        objeto_inicio_y = origen_y - (objeto_altura * escala)
        objeto_inicio_x = origen_x + (objeto_x * escala)
        self.canvas.create_oval(
            objeto_inicio_x - 5,
            objeto_inicio_y - 5,
            objeto_inicio_x + 5,
            objeto_inicio_y + 5,
            fill="#6f42c1",
        )
        self.canvas.create_text(objeto_inicio_x + 78, objeto_inicio_y - 12, text="Objeto en caida", fill="#6f42c1")

        if self.simulacion_actual and self.simulacion_actual.get("modo_cazador_mono"):
            self.canvas.create_line(
                origen_x,
                altura_pantalla,
                objeto_inicio_x,
                objeto_inicio_y,
                fill="#adb5bd",
                dash=(4, 3),
            )
            self.canvas.create_text(
                (origen_x + objeto_inicio_x) / 2,
                ((altura_pantalla + objeto_inicio_y) / 2) - 14,
                text="Linea de punteria",
                fill="#6c757d",
            )

        punto_maximo = max(puntos, key=lambda punto: punto["y"])
        punto_final = puntos[-1]
        for punto, color, etiqueta in [
            (punto_maximo, "#198754", "Altura maxima"),
            (punto_final, "#fd7e14", "Impacto"),
        ]:
            pos_x = origen_x + (punto["x"] * escala)
            pos_y = origen_y - (punto["y"] * escala)
            self.canvas.create_oval(pos_x - 5, pos_y - 5, pos_x + 5, pos_y + 5, fill=color)
            self.canvas.create_text(pos_x + 48, pos_y - 12, text=etiqueta, fill=color)

        if "tiempo" in intercepcion and "y_proyectil" in intercepcion and intercepcion["y_proyectil"] >= 0:
            pos_x = origen_x + (objeto_x * escala)
            pos_y = origen_y - (max(0.0, intercepcion["y_proyectil"]) * escala)
            color = "#20c997" if intercepcion["hay_intercepcion"] else "#212529"
            etiqueta = "Intercepcion" if intercepcion["hay_intercepcion"] else "Cruce en x"
            self.canvas.create_oval(pos_x - 6, pos_y - 6, pos_x + 6, pos_y + 6, outline=color, width=2)
            self.canvas.create_text(pos_x + 42, pos_y + 14, text=etiqueta, fill=color)

    def _detener_animacion(self):
        """Cancela cualquier animación en curso y reinicia el índice."""
        self.animacion_activa = False
        if self.animacion_job is not None:
            self.raiz.after_cancel(self.animacion_job)
            self.animacion_job = None
        self.indice_animacion = 0

    def animar(self):
        """Inicia la animación cuadro a cuadro de la simulación activa."""
        if not self.simulacion_actual or not self.escena_actual:
            messagebox.showinfo("Sin simulacion", "Primero ejecuta una simulacion para poder animarla.")
            return
        self._detener_animacion()
        self.animacion_activa = True
        self._paso_animacion()

    def _paso_animacion(self):
        """Avanza un paso la animación y marca la posición actual de ambos cuerpos."""
        if not self.animacion_activa or not self.escena_actual:
            return

        puntos_proyectil = self.escena_actual["puntos_proyectil"]
        puntos_objeto = self.escena_actual["puntos_objeto"]
        if self.indice_animacion >= len(puntos_proyectil):
            self.animacion_activa = False
            self.animacion_job = None
            return

        punto_p = puntos_proyectil[self.indice_animacion]
        punto_o = puntos_objeto[self.indice_animacion]
        escala = self.escena_actual["escala"]
        origen_x = self.escena_actual["origen_x"]
        origen_y = self.escena_actual["origen_y"]

        pos_px = origen_x + (punto_p["x"] * escala)
        pos_py = origen_y - (punto_p["y"] * escala)
        pos_ox = origen_x + (punto_o["x"] * escala)
        pos_oy = origen_y - (punto_o["y"] * escala)

        self.canvas.delete("animacion")
        self.canvas.create_oval(pos_px - 7, pos_py - 7, pos_px + 7, pos_py + 7, fill="#0b6efd", outline="", tags="animacion")
        self.canvas.create_oval(pos_ox - 7, pos_oy - 7, pos_ox + 7, pos_oy + 7, fill="#6f42c1", outline="", tags="animacion")
        self.canvas.create_text(
            120,
            24,
            text=f"t = {punto_p['t']:.2f} s",
            fill="#111111",
            font=("Segoe UI", 10, "bold"),
            tags="animacion",
        )
        if self.tabla_resultados:
            self.tabla_resultados.selection_remove(*self.tabla_resultados.selection())
            filas = self.tabla_resultados.get_children()
        else:
            filas = ()
        if filas:
            indice_tabla = min(len(filas) - 1, int(self.indice_animacion / max(1, len(puntos_proyectil) // 18)))
            self.tabla_resultados.selection_set(filas[indice_tabla])
            self.tabla_resultados.see(filas[indice_tabla])

        self.indice_animacion += 1
        self.animacion_job = self.raiz.after(ANIMATION_DELAY_MS, self._paso_animacion)

    def calcular_altura_automatica(self):
        """Calcula una altura inicial que haga posible la intercepción."""
        valores, error = self._leer_entradas()
        if error:
            messagebox.showerror("Entrada invalida", error)
            return
        error = self._validar_entradas(valores)
        if error:
            messagebox.showerror("Entrada invalida", error)
            return

        datos = calcular_trayectoria(
            valores["velocidad"],
            valores["angulo"],
            valores["altura"],
            valores["gravedad"],
            valores["muestras"],
        )
        altura_requerida, error = calcular_altura_para_intercepcion(
            datos,
            valores["objeto_x"],
            valores["gravedad"],
            valores["retraso"],
        )
        if error:
            messagebox.showerror("Calculo no disponible", error)
            return

        self.campos["objeto_altura"].delete(0, tk.END)
        self.campos["objeto_altura"].insert(0, f"{altura_requerida:.3f}")
        self.simular()

    def calcular_retraso_automatico(self):
        """Calcula el retraso de caída necesario para lograr la intercepción."""
        valores, error = self._leer_entradas()
        if error:
            messagebox.showerror("Entrada invalida", error)
            return
        error = self._validar_entradas(valores)
        if error:
            messagebox.showerror("Entrada invalida", error)
            return

        datos = calcular_trayectoria(
            valores["velocidad"],
            valores["angulo"],
            valores["altura"],
            valores["gravedad"],
            valores["muestras"],
        )
        retraso_requerido, error = calcular_retraso_para_intercepcion(
            datos,
            valores["objeto_altura"],
            valores["objeto_x"],
            valores["gravedad"],
        )
        if error:
            messagebox.showerror("Calculo no disponible", error)
            return

        self.campos["retraso"].delete(0, tk.END)
        self.campos["retraso"].insert(0, f"{retraso_requerido:.3f}")
        self.simular()


def main():
    raiz = tk.Tk()
    estilo = ttk.Style()
    if "clam" in estilo.theme_names():
        estilo.theme_use("clam")
    SimuladorMovimientoParabolico(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    main()