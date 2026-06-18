import tkinter as tk
from tkinter import messagebox, ttk

from estilos import Fuentes, PaletaAzul
from logica_experimento import calcular_datos_experimento
from validaciones import leer_y_validar_datos


class InterfazExperimento:
    def __init__(self, ventana_principal):
        self.ventana_principal = ventana_principal
        self.campos_entrada = {}
        self.etiquetas_resultado = {}

        self.configurar_ventana()
        self.configurar_estilos_ttk()
        self.construir_interfaz()

    def configurar_ventana(self):
        self.ventana_principal.title("Simulador de disparo y caída")
        self.ventana_principal.configure(bg=PaletaAzul.FONDO_APLICACION)
        self.ventana_principal.minsize(1150, 720)
        self.ventana_principal.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)

        try:
            self.ventana_principal.state("zoomed")
        except tk.TclError:
            ancho_pantalla = self.ventana_principal.winfo_screenwidth()
            alto_pantalla = self.ventana_principal.winfo_screenheight()
            self.ventana_principal.geometry(f"{ancho_pantalla}x{alto_pantalla}+0+0")

    def configurar_estilos_ttk(self):
        estilo_ttk = ttk.Style()

        try:
            estilo_ttk.theme_use("clam")
        except tk.TclError:
            pass

        estilo_ttk.configure(
            "BotonPrincipal.TButton",
            font=Fuentes.BOTON,
            padding=(14, 10),
            background=PaletaAzul.AZUL_PRINCIPAL,
            foreground=PaletaAzul.TEXTO_PRINCIPAL,
            borderwidth=0,
        )

        estilo_ttk.map(
            "BotonPrincipal.TButton",
            background=[
                ("active", PaletaAzul.AZUL_CLARO),
                ("pressed", PaletaAzul.AZUL_NEON),
            ],
            foreground=[
                ("active", PaletaAzul.TEXTO_OSCURO),
                ("pressed", PaletaAzul.TEXTO_OSCURO),
            ],
        )

        estilo_ttk.configure(
            "BotonSecundario.TButton",
            font=Fuentes.BOTON,
            padding=(14, 10),
            background=PaletaAzul.FONDO_PANEL_SECUNDARIO,
            foreground=PaletaAzul.TEXTO_PRINCIPAL,
            borderwidth=0,
        )

        estilo_ttk.map(
            "BotonSecundario.TButton",
            background=[
                ("active", PaletaAzul.LINEA_SUAVE),
                ("pressed", PaletaAzul.AZUL_PRINCIPAL),
            ],
        )

        estilo_ttk.configure(
            "CampoEntrada.TEntry",
            fieldbackground=PaletaAzul.FONDO_CAMPO,
            foreground=PaletaAzul.TEXTO_OSCURO,
            padding=8,
        )

    def construir_interfaz(self):
        contenedor_principal = tk.Frame(
            self.ventana_principal,
            bg=PaletaAzul.FONDO_APLICACION,
        )
        contenedor_principal.pack(fill="both", expand=True, padx=24, pady=20)

        self.crear_encabezado(contenedor_principal)

        cuerpo_interfaz = tk.Frame(
            contenedor_principal,
            bg=PaletaAzul.FONDO_APLICACION,
        )
        cuerpo_interfaz.pack(fill="both", expand=True, pady=(18, 0))

        cuerpo_interfaz.columnconfigure(0, weight=0)
        cuerpo_interfaz.columnconfigure(1, weight=1)
        cuerpo_interfaz.rowconfigure(0, weight=1)

        self.crear_panel_entradas(cuerpo_interfaz)
        self.crear_panel_visualizacion(cuerpo_interfaz)

    def crear_encabezado(self, contenedor_principal):
        panel_encabezado = tk.Frame(
            contenedor_principal,
            bg=PaletaAzul.FONDO_APLICACION,
        )
        panel_encabezado.pack(fill="x")

        etiqueta_titulo = tk.Label(
            panel_encabezado,
            text="Experimento del disparo hacia el mono",
            font=Fuentes.TITULO,
            bg=PaletaAzul.FONDO_APLICACION,
            fg=PaletaAzul.TEXTO_PRINCIPAL,
        )
        etiqueta_titulo.pack(anchor="w")

        etiqueta_subtitulo = tk.Label(
            panel_encabezado,
            text="El proyectil apunta directamente al mono suspendido y ambos comienzan su movimiento al mismo tiempo.",
            font=Fuentes.SUBTITULO,
            bg=PaletaAzul.FONDO_APLICACION,
            fg=PaletaAzul.TEXTO_SECUNDARIO,
        )
        etiqueta_subtitulo.pack(anchor="w", pady=(4, 0))

    def crear_panel_entradas(self, cuerpo_interfaz):
        panel_entradas = tk.Frame(
            cuerpo_interfaz,
            width=360,
            bg=PaletaAzul.FONDO_PANEL,
            highlightbackground=PaletaAzul.LINEA_SUAVE,
            highlightthickness=1,
        )
        panel_entradas.grid(row=0, column=0, sticky="nsew", padx=(0, 18))
        panel_entradas.grid_propagate(False)
        panel_entradas.columnconfigure(0, weight=1)

        etiqueta_seccion = tk.Label(
            panel_entradas,
            text="Datos del experimento",
            font=Fuentes.SECCION,
            bg=PaletaAzul.FONDO_PANEL,
            fg=PaletaAzul.TEXTO_PRINCIPAL,
        )
        etiqueta_seccion.grid(row=0, column=0, sticky="w", padx=18, pady=(18, 14))

        definiciones_campos = [
            ("posicion_x_lanzador", "X del lanzador (m)", ""),
            ("altura_lanzador", "Altura del lanzador (m)", ""),
            ("posicion_x_mono", "X del mono (m)", ""),
            ("altura_mono", "Altura inicial del mono (m)", ""),
            ("velocidad_inicial", "Velocidad inicial (m/s)", ""),
        ]

        fila_actual = 1

        for clave_campo, texto_etiqueta, valor_inicial in definiciones_campos:
            self.crear_campo_entrada(
                panel_entradas,
                fila_actual,
                clave_campo,
                texto_etiqueta,
                valor_inicial,
            )
            fila_actual += 2

        self.crear_bloque_angulo(panel_entradas, fila_actual)
        fila_actual += 1

        self.crear_botones_control(panel_entradas, fila_actual)

    def crear_campo_entrada(
        self,
        panel_entradas,
        fila_actual,
        clave_campo,
        texto_etiqueta,
        valor_inicial,
    ):
        etiqueta_campo = tk.Label(
            panel_entradas,
            text=texto_etiqueta,
            font=Fuentes.TEXTO_PEQUENO,
            bg=PaletaAzul.FONDO_PANEL,
            fg=PaletaAzul.TEXTO_SECUNDARIO,
        )
        etiqueta_campo.grid(row=fila_actual, column=0, sticky="w", padx=18)

        entrada_campo = ttk.Entry(
            panel_entradas,
            style="CampoEntrada.TEntry",
            font=Fuentes.TEXTO,
        )

        if valor_inicial:
            entrada_campo.insert(0, valor_inicial)

        entrada_campo.grid(
            row=fila_actual + 1,
            column=0,
            sticky="ew",
            padx=18,
            pady=(4, 10),
        )

        self.campos_entrada[clave_campo] = entrada_campo

    def crear_bloque_angulo(self, panel_entradas, fila_actual):
        panel_angulo = tk.Frame(
            panel_entradas,
            bg=PaletaAzul.FONDO_PANEL_SECUNDARIO,
            highlightbackground=PaletaAzul.LINEA_SUAVE,
            highlightthickness=1,
        )
        panel_angulo.grid(row=fila_actual, column=0, sticky="ew", padx=18, pady=(2, 12))
        panel_angulo.columnconfigure(0, weight=1)

        etiqueta_titulo = tk.Label(
            panel_angulo,
            text="Ángulo de disparo",
            font=Fuentes.TEXTO,
            bg=PaletaAzul.FONDO_PANEL_SECUNDARIO,
            fg=PaletaAzul.TEXTO_PRINCIPAL,
        )
        etiqueta_titulo.grid(row=0, column=0, sticky="w", padx=12, pady=(10, 2))

        etiqueta_descripcion = tk.Label(
            panel_angulo,
            text="Se calcula automáticamente para apuntar a la posición inicial del mono.",
            font=Fuentes.TEXTO_PEQUENO,
            bg=PaletaAzul.FONDO_PANEL_SECUNDARIO,
            fg=PaletaAzul.TEXTO_SECUNDARIO,
            wraplength=290,
            justify="left",
        )
        etiqueta_descripcion.grid(row=1, column=0, sticky="w", padx=12, pady=(0, 10))

    def crear_botones_control(self, panel_entradas, fila_actual):
        panel_botones = tk.Frame(panel_entradas, bg=PaletaAzul.FONDO_PANEL)
        panel_botones.grid(row=fila_actual, column=0, sticky="ew", padx=18, pady=(0, 18))
        panel_botones.columnconfigure(0, weight=1)

        boton_simular = ttk.Button(
            panel_botones,
            text="Simular",
            style="BotonPrincipal.TButton",
            command=self.simular,
        )
        boton_simular.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        boton_reiniciar = ttk.Button(
            panel_botones,
            text="Reiniciar",
            style="BotonSecundario.TButton",
            command=self.dibujar_escena,
        )
        boton_reiniciar.grid(row=1, column=0, sticky="ew")

    def crear_panel_visualizacion(self, cuerpo_interfaz):
        panel_visualizacion = tk.Frame(
            cuerpo_interfaz,
            bg=PaletaAzul.FONDO_PANEL,
            highlightbackground=PaletaAzul.LINEA_SUAVE,
            highlightthickness=1,
        )
        panel_visualizacion.grid(row=0, column=1, sticky="nsew")
        panel_visualizacion.columnconfigure(0, weight=1)
        panel_visualizacion.rowconfigure(1, weight=1)

        etiqueta_titulo = tk.Label(
            panel_visualizacion,
            text="Vista del experimento",
            font=Fuentes.SECCION,
            bg=PaletaAzul.FONDO_PANEL,
            fg=PaletaAzul.TEXTO_PRINCIPAL,
        )
        etiqueta_titulo.grid(row=0, column=0, sticky="w", padx=16, pady=14)

        self.canvas_escena = tk.Canvas(
            panel_visualizacion,
            bg="#D8ECFF",
            highlightthickness=0,
        )
        self.canvas_escena.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 12))
        self.canvas_escena.bind("<Configure>", self.redibujar_escena)

        self.crear_panel_resultados(panel_visualizacion)

    def crear_panel_resultados(self, panel_visualizacion):
        panel_resultados = tk.Frame(
            panel_visualizacion,
            bg=PaletaAzul.FONDO_PANEL,
        )
        panel_resultados.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 16))

        panel_resultados.columnconfigure(0, weight=1)
        panel_resultados.columnconfigure(1, weight=1)
        panel_resultados.columnconfigure(2, weight=1)
        panel_resultados.columnconfigure(3, weight=1)

        self.crear_tarjeta_resultado(panel_resultados, 0, "Ángulo", "-- °", "angulo")
        self.crear_tarjeta_resultado(panel_resultados, 1, "Tiempo", "-- s", "tiempo")
        self.crear_tarjeta_resultado(panel_resultados, 2, "Altura de choque", "-- m", "altura")
        self.crear_tarjeta_resultado(panel_resultados, 3, "Estado", "--", "estado")

    def crear_tarjeta_resultado(self, panel_resultados, columna, titulo, valor, clave_resultado):
        tarjeta = tk.Frame(
            panel_resultados,
            bg=PaletaAzul.FONDO_PANEL_SECUNDARIO,
            highlightbackground=PaletaAzul.LINEA_SUAVE,
            highlightthickness=1,
        )
        tarjeta.grid(row=0, column=columna, sticky="ew", padx=6)

        etiqueta_titulo = tk.Label(
            tarjeta,
            text=titulo,
            font=Fuentes.TEXTO_PEQUENO,
            bg=PaletaAzul.FONDO_PANEL_SECUNDARIO,
            fg=PaletaAzul.TEXTO_SECUNDARIO,
        )
        etiqueta_titulo.pack(anchor="w", padx=12, pady=(8, 2))

        etiqueta_valor = tk.Label(
            tarjeta,
            text=valor,
            font=Fuentes.SECCION,
            bg=PaletaAzul.FONDO_PANEL_SECUNDARIO,
            fg=PaletaAzul.TEXTO_PRINCIPAL,
        )
        etiqueta_valor.pack(anchor="w", padx=12, pady=(0, 10))

        self.etiquetas_resultado[clave_resultado] = etiqueta_valor

    def redibujar_escena(self, evento_redimension):
        self.dibujar_escena()

    def dibujar_escena(self):
        self.canvas_escena.delete("all")

        ancho_canvas = max(self.canvas_escena.winfo_width(), 800)
        alto_canvas = max(self.canvas_escena.winfo_height(), 460)

        self.dibujar_fondo_escena(ancho_canvas, alto_canvas)
        self.dibujar_elementos_experimento(ancho_canvas, alto_canvas)

    def dibujar_fondo_escena(self, ancho_canvas, alto_canvas):
        self.canvas_escena.create_rectangle(
            0,
            0,
            ancho_canvas,
            alto_canvas,
            fill="#D8ECFF",
            outline="",
        )

        separacion_cuadricula = 70

        for posicion_x_cuadricula in range(0, ancho_canvas, separacion_cuadricula):
            self.canvas_escena.create_line(
                posicion_x_cuadricula,
                0,
                posicion_x_cuadricula,
                alto_canvas,
                fill="#B8D8F2",
                width=1,
            )

        for posicion_y_cuadricula in range(0, alto_canvas, separacion_cuadricula):
            self.canvas_escena.create_line(
                0,
                posicion_y_cuadricula,
                ancho_canvas,
                posicion_y_cuadricula,
                fill="#B8D8F2",
                width=1,
            )

        posicion_suelo_y = alto_canvas - 78

        self.canvas_escena.create_rectangle(
            0,
            posicion_suelo_y,
            ancho_canvas,
            alto_canvas,
            fill="#0D2742",
            outline="",
        )

        self.canvas_escena.create_line(
            0,
            posicion_suelo_y,
            ancho_canvas,
            posicion_suelo_y,
            fill=PaletaAzul.AZUL_NEON,
            width=3,
        )

    def dibujar_elementos_experimento(self, ancho_canvas, alto_canvas):
        posicion_suelo_y = alto_canvas - 78
        posicion_lanzador_x = 120
        posicion_lanzador_y = posicion_suelo_y - 62
        posicion_mono_x = ancho_canvas - 190
        posicion_mono_y = max(95, alto_canvas * 0.28)
        posicion_choque_y = posicion_mono_y + 118

        self.dibujar_lanzador(posicion_lanzador_x, posicion_lanzador_y)
        self.dibujar_mono_suspendido(posicion_mono_x, posicion_mono_y)
        self.dibujar_linea_punteria(
            posicion_lanzador_x,
            posicion_lanzador_y,
            posicion_mono_x,
            posicion_mono_y,
        )
        self.dibujar_trayectoria_referencial(
            posicion_lanzador_x,
            posicion_lanzador_y,
            posicion_mono_x,
            posicion_choque_y,
        )
        self.dibujar_linea_caida_mono(
            posicion_mono_x,
            posicion_mono_y,
            posicion_suelo_y,
            posicion_choque_y,
        )
        self.dibujar_etiquetas_escena(
            posicion_lanzador_x,
            posicion_lanzador_y,
            posicion_mono_x,
            posicion_mono_y,
            posicion_choque_y,
        )

    def dibujar_lanzador(self, posicion_lanzador_x, posicion_lanzador_y):
        self.canvas_escena.create_rectangle(
            posicion_lanzador_x - 38,
            posicion_lanzador_y + 28,
            posicion_lanzador_x + 52,
            posicion_lanzador_y + 48,
            fill="#123B63",
            outline=PaletaAzul.AZUL_OSCURO,
            width=2,
        )

        self.canvas_escena.create_oval(
            posicion_lanzador_x - 28,
            posicion_lanzador_y + 40,
            posicion_lanzador_x - 8,
            posicion_lanzador_y + 60,
            fill="#071A2E",
            outline=PaletaAzul.AZUL_NEON,
            width=2,
        )

        self.canvas_escena.create_oval(
            posicion_lanzador_x + 28,
            posicion_lanzador_y + 40,
            posicion_lanzador_x + 48,
            posicion_lanzador_y + 60,
            fill="#071A2E",
            outline=PaletaAzul.AZUL_NEON,
            width=2,
        )

        self.canvas_escena.create_line(
            posicion_lanzador_x,
            posicion_lanzador_y + 28,
            posicion_lanzador_x + 70,
            posicion_lanzador_y - 4,
            fill="#0B1C2C",
            width=13,
        )

        self.canvas_escena.create_line(
            posicion_lanzador_x,
            posicion_lanzador_y + 28,
            posicion_lanzador_x + 70,
            posicion_lanzador_y - 4,
            fill=PaletaAzul.AZUL_PRINCIPAL,
            width=8,
        )

        self.canvas_escena.create_oval(
            posicion_lanzador_x + 66,
            posicion_lanzador_y - 9,
            posicion_lanzador_x + 82,
            posicion_lanzador_y + 7,
            fill=PaletaAzul.AZUL_NEON,
            outline=PaletaAzul.AZUL_OSCURO,
            width=2,
        )

    def dibujar_mono_suspendido(self, posicion_mono_x, posicion_mono_y):
        self.canvas_escena.create_line(
            posicion_mono_x,
            posicion_mono_y - 70,
            posicion_mono_x,
            posicion_mono_y - 18,
            fill="#0B1C2C",
            width=3,
        )

        self.canvas_escena.create_rectangle(
            posicion_mono_x - 58,
            posicion_mono_y - 78,
            posicion_mono_x + 58,
            posicion_mono_y - 68,
            fill="#123B63",
            outline=PaletaAzul.AZUL_OSCURO,
            width=2,
        )

        self.canvas_escena.create_oval(
            posicion_mono_x - 25,
            posicion_mono_y - 25,
            posicion_mono_x + 25,
            posicion_mono_y + 25,
            fill=PaletaAzul.ADVERTENCIA,
            outline="#7A5A00",
            width=2,
        )

        self.canvas_escena.create_oval(
            posicion_mono_x - 10,
            posicion_mono_y - 4,
            posicion_mono_x - 4,
            posicion_mono_y + 2,
            fill="#3D2A00",
            outline="",
        )

        self.canvas_escena.create_oval(
            posicion_mono_x + 4,
            posicion_mono_y - 4,
            posicion_mono_x + 10,
            posicion_mono_y + 2,
            fill="#3D2A00",
            outline="",
        )

        self.canvas_escena.create_arc(
            posicion_mono_x - 10,
            posicion_mono_y,
            posicion_mono_x + 10,
            posicion_mono_y + 14,
            start=200,
            extent=140,
            style="arc",
            outline="#3D2A00",
            width=2,
        )

    def dibujar_linea_punteria(
        self,
        posicion_lanzador_x,
        posicion_lanzador_y,
        posicion_mono_x,
        posicion_mono_y,
    ):
        self.canvas_escena.create_line(
            posicion_lanzador_x + 78,
            posicion_lanzador_y - 5,
            posicion_mono_x,
            posicion_mono_y,
            fill=PaletaAzul.AZUL_PRINCIPAL,
            width=2,
            dash=(10, 8),
        )

    def dibujar_trayectoria_referencial(
        self,
        posicion_lanzador_x,
        posicion_lanzador_y,
        posicion_mono_x,
        posicion_choque_y,
    ):
        puntos_trayectoria = []
        cantidad_puntos = 48

        for indice_punto in range(cantidad_puntos):
            progreso = indice_punto / (cantidad_puntos - 1)

            posicion_actual_x = (
                posicion_lanzador_x
                + 78
                + ((posicion_mono_x - (posicion_lanzador_x + 78)) * progreso)
            )

            posicion_lineal_y = (
                posicion_lanzador_y
                - 5
                + ((posicion_choque_y - (posicion_lanzador_y - 5)) * progreso)
            )

            caida_visual = 58 * progreso * progreso
            posicion_actual_y = posicion_lineal_y + caida_visual

            puntos_trayectoria.append(posicion_actual_x)
            puntos_trayectoria.append(posicion_actual_y)

        self.canvas_escena.create_line(
            puntos_trayectoria,
            fill=PaletaAzul.AZUL_NEON,
            width=4,
            smooth=True,
        )

        posicion_proyectil_x = puntos_trayectoria[36]
        posicion_proyectil_y = puntos_trayectoria[37]

        self.canvas_escena.create_oval(
            posicion_proyectil_x - 8,
            posicion_proyectil_y - 8,
            posicion_proyectil_x + 8,
            posicion_proyectil_y + 8,
            fill=PaletaAzul.AZUL_OSCURO,
            outline=PaletaAzul.AZUL_NEON,
            width=2,
        )

    def dibujar_linea_caida_mono(
        self,
        posicion_mono_x,
        posicion_mono_y,
        posicion_suelo_y,
        posicion_choque_y,
    ):
        self.canvas_escena.create_line(
            posicion_mono_x,
            posicion_mono_y + 24,
            posicion_mono_x,
            posicion_suelo_y,
            fill="#326A91",
            width=2,
            dash=(6, 8),
        )

        self.canvas_escena.create_oval(
            posicion_mono_x - 22,
            posicion_choque_y - 22,
            posicion_mono_x + 22,
            posicion_choque_y + 22,
            outline=PaletaAzul.ADVERTENCIA,
            width=3,
        )

        self.canvas_escena.create_oval(
            posicion_mono_x - 34,
            posicion_choque_y - 34,
            posicion_mono_x + 34,
            posicion_choque_y + 34,
            outline=PaletaAzul.AZUL_NEON,
            width=2,
            dash=(4, 5),
        )

    def dibujar_etiquetas_escena(
        self,
        posicion_lanzador_x,
        posicion_lanzador_y,
        posicion_mono_x,
        posicion_mono_y,
        posicion_choque_y,
    ):
        self.canvas_escena.create_text(
            posicion_lanzador_x,
            posicion_lanzador_y + 78,
            text="Lanzador",
            font=Fuentes.TEXTO,
            fill=PaletaAzul.TEXTO_OSCURO,
        )

        self.canvas_escena.create_text(
            posicion_mono_x,
            posicion_mono_y - 95,
            text="Mono suspendido",
            font=Fuentes.TEXTO,
            fill=PaletaAzul.TEXTO_OSCURO,
        )

        self.canvas_escena.create_text(
            posicion_mono_x + 12,
            posicion_choque_y + 52,
            text="Choque",
            font=Fuentes.TEXTO_PEQUENO,
            fill=PaletaAzul.TEXTO_OSCURO,
            justify="center",
        )

        self.canvas_escena.create_text(
            posicion_lanzador_x + 270,
            posicion_lanzador_y - 90,
            text="Línea de puntería directa",
            font=Fuentes.TEXTO_PEQUENO,
            fill=PaletaAzul.AZUL_OSCURO,
        )

    def simular(self):
        try:
            datos_experimento = leer_y_validar_datos(self.campos_entrada)
            datos_calculados = calcular_datos_experimento(datos_experimento)
        except ValueError as error:
            messagebox.showerror("Datos inválidos", str(error))
            return

        self.etiquetas_resultado["angulo"].configure(
            text=f"{datos_calculados['angulo_grados']:.2f} °"
        )
        self.etiquetas_resultado["tiempo"].configure(
            text=f"{datos_calculados['tiempo_choque']:.2f} s"
        )
        self.etiquetas_resultado["altura"].configure(
            text=f"{datos_calculados['altura_choque']:.2f} m"
        )
        self.etiquetas_resultado["estado"].configure(
            text=datos_calculados["estado"]
        )

    def cerrar_aplicacion(self):
        self.ventana_principal.destroy()