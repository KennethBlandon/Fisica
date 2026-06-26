"""Interfaz grafica principal del simulador de cuerpos celestes."""

from __future__ import annotations

import math
import random
import tkinter as tk
from tkinter import messagebox

from animacion import MotorAnimacion
from estilos import (
    AXIS,
    BG_APP,
    BG_CANVAS,
    BG_PANEL,
    FONT_LABEL,
    FONT_MONO,
    FONT_TITLE,
    PRIMARY,
    SUCCESS,
    TEXT,
    TEXT_MUTED,
    TRAIL,
    WARNING,
)
from logica_experimento import Cuerpo, SimuladorNBody, crear_sistema_tierra_sol_luna
from validaciones import leer_float, validar_masa


class AppSimulador(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Simulador de cuerpos celestes 2D")
        self.geometry("1200x760")
        self.minsize(980, 620)
        self.configure(bg=BG_APP)

        self.simulador = SimuladorNBody()
        self.motor = MotorAnimacion(self, self._tick, fps=60)

        self.dt_var = tk.StringVar(value="3600")
        self.subpasos_var = tk.StringVar(value="2")
        self.camara_var = tk.StringVar(value="Origen (0,0)")
        self.retardo_var = tk.BooleanVar(value=False)
        self.vel_grav_var = tk.StringVar(value="299792458")
        self.estado_var = tk.StringVar(value="Listo")
        self.tiempo_var = tk.StringVar(value="t = 0.00 dias")

        self.entries: dict[str, tk.Entry] = {}
        self.escala_actual = 1.0
        self.centro_x = 0.0
        self.centro_y = 0.0
        self.zoom_manual: float | None = None
        self.zoom_min = 1e-15
        self.zoom_max = 1.0  # 1 px = 1 m (maximo acercamiento)
        self.pan_x_m = 0.0
        self.pan_y_m = 0.0
        self._ultimo_mouse_x = 0
        self._ultimo_mouse_y = 0
        self.estrellas: list[tuple[float, float, int, str]] = []
        self._estrellas_ancho = 0
        self._estrellas_alto = 0

        self._crear_ui()
        self._cargar_ejemplo()

    def _crear_ui(self) -> None:
        panel = tk.Frame(self, bg=BG_PANEL, width=340)
        panel.pack(side=tk.LEFT, fill=tk.Y)
        panel.pack_propagate(False)

        canvas_wrap = tk.Frame(self, bg=BG_APP)
        canvas_wrap.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        titulo = tk.Label(
            panel,
            text="Simulador N-Cuerpos",
            bg=BG_PANEL,
            fg=TEXT,
            font=FONT_TITLE,
            anchor="w",
        )
        titulo.pack(fill=tk.X, padx=16, pady=(14, 8))

        subt = tk.Label(
            panel,
            text="Agrega masa, posicion y velocidad inicial",
            bg=BG_PANEL,
            fg=TEXT_MUTED,
            font=FONT_LABEL,
            anchor="w",
        )
        subt.pack(fill=tk.X, padx=16, pady=(0, 10))

        form = tk.Frame(panel, bg=BG_PANEL)
        form.pack(fill=tk.X, padx=16)

        self._crear_campo(form, "Nombre", "Cuerpo")
        self._crear_campo(form, "Masa (kg)", "5.972e24")
        self._crear_campo(form, "x (m)", "1.5e11")
        self._crear_campo(form, "y (m)", "0")
        self._crear_campo(form, "vx (m/s)", "0")
        self._crear_campo(form, "vy (m/s)", "29885")
        self._crear_campo(form, "Color", "#38bdf8")

        fila_botones = tk.Frame(panel, bg=BG_PANEL)
        fila_botones.pack(fill=tk.X, padx=16, pady=(12, 8))

        tk.Button(
            fila_botones,
            text="Agregar",
            bg=PRIMARY,
            fg="#001018",
            activebackground="#7dd3fc",
            relief=tk.FLAT,
            command=self._agregar_cuerpo,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        tk.Button(
            fila_botones,
            text="Eliminar",
            bg=WARNING,
            fg="#1f1300",
            activebackground="#fbbf24",
            relief=tk.FLAT,
            command=self._eliminar_cuerpo,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))

        self.lista = tk.Listbox(
            panel,
            bg="#0b1120",
            fg=TEXT,
            selectbackground="#1e293b",
            font=FONT_MONO,
            height=8,
            relief=tk.FLAT,
        )
        self.lista.pack(fill=tk.X, padx=16, pady=(2, 10))

        controles = tk.Frame(panel, bg=BG_PANEL)
        controles.pack(fill=tk.X, padx=16)

        self._crear_campo_control(controles, "dt (s)", self.dt_var)
        self._crear_campo_control(controles, "Subpasos", self.subpasos_var)

        tk.Checkbutton(
            controles,
            text="Gravedad con retardo (t-r/c)",
            variable=self.retardo_var,
            bg=BG_PANEL,
            fg=TEXT,
            selectcolor="#0b1120",
            activebackground=BG_PANEL,
            activeforeground=TEXT,
            anchor="w",
            relief=tk.FLAT,
        ).pack(fill=tk.X, pady=(0, 4))

        self._crear_campo_control(controles, "Velocidad gravedad (m/s)", self.vel_grav_var)

        tk.Label(
            controles,
            text="Camara",
            bg=BG_PANEL,
            fg=TEXT,
            font=FONT_LABEL,
            anchor="w",
        ).pack(fill=tk.X)
        self.selector_camara = tk.OptionMenu(controles, self.camara_var, "Origen (0,0)")
        self.selector_camara.config(
            relief=tk.FLAT,
            bg="#0b1120",
            fg=TEXT,
            activebackground="#1e293b",
            activeforeground=TEXT,
            highlightthickness=0,
            anchor="w",
        )
        self.selector_camara["menu"].config(
            bg="#0b1120",
            fg=TEXT,
            activebackground="#1e293b",
            activeforeground=TEXT,
            relief=tk.FLAT,
        )
        self.selector_camara.pack(fill=tk.X, pady=(0, 6))

        tk.Button(
            controles,
            text="Autoajustar vista",
            bg="#334155",
            fg=TEXT,
            activebackground="#475569",
            relief=tk.FLAT,
            command=self._autoajustar_vista,
        ).pack(fill=tk.X, pady=(2, 8))

        fila_sim = tk.Frame(panel, bg=BG_PANEL)
        fila_sim.pack(fill=tk.X, padx=16, pady=(12, 8))

        tk.Button(
            fila_sim,
            text="Iniciar",
            bg=SUCCESS,
            fg="#00180c",
            relief=tk.FLAT,
            command=self._iniciar,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        tk.Button(
            fila_sim,
            text="Pausar",
            bg="#334155",
            fg=TEXT,
            relief=tk.FLAT,
            command=self._pausar,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)

        tk.Button(
            fila_sim,
            text="Reiniciar",
            bg="#475569",
            fg=TEXT,
            relief=tk.FLAT,
            command=self._reiniciar,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))

        fila_aux = tk.Frame(panel, bg=BG_PANEL)
        fila_aux.pack(fill=tk.X, padx=16, pady=(2, 8))

        tk.Button(
            fila_aux,
            text="Cargar ejemplo Sol-Tierra-Luna",
            bg="#1d4ed8",
            fg="#dbeafe",
            relief=tk.FLAT,
            command=self._cargar_ejemplo,
        ).pack(fill=tk.X)

        tk.Label(
            panel,
            textvariable=self.estado_var,
            bg=BG_PANEL,
            fg=TEXT_MUTED,
            font=FONT_LABEL,
            anchor="w",
        ).pack(fill=tk.X, padx=16, pady=(4, 2))

        tk.Label(
            panel,
            textvariable=self.tiempo_var,
            bg=BG_PANEL,
            fg=TEXT,
            font=FONT_LABEL,
            anchor="w",
        ).pack(fill=tk.X, padx=16, pady=(0, 12))

        self.canvas = tk.Canvas(
            canvas_wrap,
            bg=BG_CANVAS,
            highlightthickness=0,
            relief=tk.FLAT,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.canvas.bind("<Configure>", lambda _e: self._dibujar())
        self.canvas.bind("<MouseWheel>", self._zoom_rueda)
        self.canvas.bind("<Button-4>", self._zoom_rueda)
        self.canvas.bind("<Button-5>", self._zoom_rueda)
        self.canvas.bind("<ButtonPress-1>", self._iniciar_arrastre)
        self.canvas.bind("<B1-Motion>", self._arrastrar)

    def _crear_campo(self, parent: tk.Widget, nombre: str, defecto: str) -> None:
        tk.Label(parent, text=nombre, bg=BG_PANEL, fg=TEXT, font=FONT_LABEL, anchor="w").pack(
            fill=tk.X
        )
        entry = tk.Entry(parent, relief=tk.FLAT, bg="#0b1120", fg=TEXT, insertbackground=TEXT)
        entry.insert(0, defecto)
        entry.pack(fill=tk.X, pady=(0, 6))
        self.entries[nombre] = entry

    def _crear_campo_control(self, parent: tk.Widget, nombre: str, var: tk.StringVar) -> None:
        tk.Label(parent, text=nombre, bg=BG_PANEL, fg=TEXT, font=FONT_LABEL, anchor="w").pack(
            fill=tk.X
        )
        tk.Entry(parent, textvariable=var, relief=tk.FLAT, bg="#0b1120", fg=TEXT).pack(
            fill=tk.X, pady=(0, 6)
        )

    def _agregar_cuerpo(self) -> None:
        nombre = self.entries["Nombre"].get().strip() or f"Cuerpo {len(self.simulador.cuerpos) + 1}"

        ok, msg, masa = validar_masa(self.entries["Masa (kg)"].get())
        if not ok:
            messagebox.showerror("Dato invalido", msg)
            return

        ok, msg, x = leer_float(self.entries["x (m)"].get(), "x")
        if not ok:
            messagebox.showerror("Dato invalido", msg)
            return

        ok, msg, y = leer_float(self.entries["y (m)"].get(), "y")
        if not ok:
            messagebox.showerror("Dato invalido", msg)
            return

        ok, msg, vx = leer_float(self.entries["vx (m/s)"].get(), "vx")
        if not ok:
            messagebox.showerror("Dato invalido", msg)
            return

        ok, msg, vy = leer_float(self.entries["vy (m/s)"].get(), "vy")
        if not ok:
            messagebox.showerror("Dato invalido", msg)
            return

        color = self.entries["Color"].get().strip() or "#38bdf8"
        radio = max(3, min(12, int(3 + math.log10(max(1.0, masa)) - 20)))

        cuerpo = Cuerpo(
            nombre=nombre,
            masa=masa,
            x=x,
            y=y,
            vx=vx,
            vy=vy,
            color=color,
            radio_px=radio,
        )
        self.simulador.agregar_cuerpo(cuerpo)
        self.simulador.guardar_estado_inicial()
        self._actualizar_lista()
        self._dibujar()
        self.estado_var.set(f"Agregado: {nombre}")

    def _eliminar_cuerpo(self) -> None:
        seleccion = self.lista.curselection()
        if not seleccion:
            return
        indice = seleccion[0]
        self.simulador.eliminar_cuerpo(indice)
        self.simulador.guardar_estado_inicial()
        self._actualizar_lista()
        self._dibujar()
        self.estado_var.set("Cuerpo eliminado")

    def _cargar_ejemplo(self) -> None:
        self.motor.pausar()
        self.simulador.establecer_cuerpos(crear_sistema_tierra_sol_luna(), guardar_inicial=True)
        self._autoajustar_vista()
        self._actualizar_lista()
        self._dibujar()
        self.estado_var.set("Ejemplo Sol-Tierra-Luna cargado")

    def _iniciar(self) -> None:
        if len(self.simulador.cuerpos) < 1:
            messagebox.showwarning("Sin cuerpos", "Agrega al menos un cuerpo.")
            return

        ok, msg, dt = leer_float(self.dt_var.get(), "dt")
        if not ok or dt is None or dt <= 0:
            messagebox.showerror("Dato invalido", "dt debe ser un numero positivo.")
            return

        ok, msg, subpasos = leer_float(self.subpasos_var.get(), "Subpasos")
        if not ok or subpasos is None or subpasos < 1:
            messagebox.showerror("Dato invalido", "Subpasos debe ser un entero >= 1.")
            return

        ok, msg, v_grav = leer_float(self.vel_grav_var.get(), "Velocidad gravedad")
        if not ok or v_grav is None or v_grav <= 0:
            messagebox.showerror("Dato invalido", "Velocidad gravedad debe ser un numero positivo.")
            return

        self.simulador.dt = dt
        self.simulador.usar_retardo_gravitacional = self.retardo_var.get()
        self.simulador.velocidad_gravedad = v_grav
        self.subpasos_var.set(str(int(subpasos)))
        self.motor.iniciar()
        if self.simulador.usar_retardo_gravitacional:
            self.estado_var.set("Simulacion en ejecucion (retardo activo)")
        else:
            self.estado_var.set("Simulacion en ejecucion")

    def _pausar(self) -> None:
        self.motor.pausar()
        self.estado_var.set("Simulacion pausada")

    def _reiniciar(self) -> None:
        self.motor.pausar()
        self.simulador.reiniciar()
        self._autoajustar_vista()
        self._actualizar_lista()
        self._dibujar()
        self.estado_var.set("Sistema reiniciado")

    def _tick(self) -> None:
        subpasos = int(float(self.subpasos_var.get()))
        self.simulador.paso(subpasos=subpasos)
        dias = self.simulador.tiempo_total / (24 * 3600)
        self.tiempo_var.set(f"t = {dias:.2f} dias")
        self._dibujar()

    def _actualizar_lista(self) -> None:
        self.lista.delete(0, tk.END)
        for i, c in enumerate(self.simulador.cuerpos, start=1):
            self.lista.insert(
                tk.END,
                f"{i:02d} | {c.nombre:<12} m={c.masa:.3e}kg p=({c.x:.2e},{c.y:.2e})",
            )
        self._actualizar_selector_camara()

    def _actualizar_selector_camara(self) -> None:
        opciones = ["Origen (0,0)"] + [
            f"{i:02d} - {c.nombre}" for i, c in enumerate(self.simulador.cuerpos, start=1)
        ]

        menu = self.selector_camara["menu"]
        menu.delete(0, "end")

        for opcion in opciones:
            menu.add_command(label=opcion, command=lambda v=opcion: self.camara_var.set(v))

        if self.camara_var.get() not in opciones:
            self.camara_var.set("Origen (0,0)")

    def _autoajustar_vista(self) -> None:
        self.zoom_manual = None
        self.pan_x_m = 0.0
        self.pan_y_m = 0.0

    def _iniciar_arrastre(self, event: tk.Event) -> None:
        self._ultimo_mouse_x = int(event.x)
        self._ultimo_mouse_y = int(event.y)

    def _arrastrar(self, event: tk.Event) -> None:
        if self.escala_actual <= 0:
            return

        if self.zoom_manual is None:
            self.zoom_manual = self.escala_actual

        dx_px = int(event.x) - self._ultimo_mouse_x
        dy_px = int(event.y) - self._ultimo_mouse_y
        self._ultimo_mouse_x = int(event.x)
        self._ultimo_mouse_y = int(event.y)

        # Arrastre estilo mapa: mover mouse desplaza la vista en esa direccion.
        self.pan_x_m -= dx_px / self.escala_actual
        self.pan_y_m += dy_px / self.escala_actual
        self._dibujar()

    def _zoom_rueda(self, event: tk.Event) -> None:
        if self.escala_actual <= 0:
            return

        if self.zoom_manual is None:
            self.zoom_manual = self.escala_actual

        delta = 0
        if hasattr(event, "delta") and event.delta:
            delta = 1 if event.delta > 0 else -1
        elif hasattr(event, "num"):
            if event.num == 4:
                delta = 1
            elif event.num == 5:
                delta = -1

        if delta == 0:
            return

        factor = 1.15 if delta > 0 else 1.0 / 1.15
        escala_ant = self.zoom_manual
        escala_nueva = max(self.zoom_min, min(self.zoom_max, escala_ant * factor))
        if escala_nueva == escala_ant:
            return

        base_x, base_y = self._obtener_centro_referencia()
        centro_ant_x = base_x + self.pan_x_m
        centro_ant_y = base_y + self.pan_y_m

        ancho = self.canvas.winfo_width()
        alto = self.canvas.winfo_height()
        mx = float(event.x)
        my = float(event.y)

        mundo_x = centro_ant_x + (mx - ancho / 2) / escala_ant
        mundo_y = centro_ant_y - (my - alto / 2) / escala_ant

        centro_nuevo_x = mundo_x - (mx - ancho / 2) / escala_nueva
        centro_nuevo_y = mundo_y + (my - alto / 2) / escala_nueva

        self.pan_x_m = centro_nuevo_x - base_x
        self.pan_y_m = centro_nuevo_y - base_y
        self.zoom_manual = escala_nueva
        self._dibujar()

    def _obtener_centro_referencia(self) -> tuple[float, float]:
        seleccion = self.camara_var.get().strip()
        if seleccion == "Origen (0,0)":
            return 0.0, 0.0

        if " - " not in seleccion:
            return 0.0, 0.0

        prefijo = seleccion.split(" - ", maxsplit=1)[0]
        if not prefijo.isdigit():
            return 0.0, 0.0

        indice = int(prefijo) - 1
        if 0 <= indice < len(self.simulador.cuerpos):
            ref = self.simulador.cuerpos[indice]
            return ref.x, ref.y
        return 0.0, 0.0

    def _escala_mundo(self) -> float:
        if not self.simulador.cuerpos:
            return 1.0

        base_x, base_y = self._obtener_centro_referencia()

        if self.zoom_manual is not None:
            self.centro_x = base_x + self.pan_x_m
            self.centro_y = base_y + self.pan_y_m
            return self.zoom_manual

        self.centro_x = base_x
        self.centro_y = base_y

        mayor = 1.0
        for c in self.simulador.cuerpos:
            mayor = max(mayor, math.hypot(c.x - self.centro_x, c.y - self.centro_y))
            if c.trayectoria:
                for px, py in c.trayectoria:
                    mayor = max(mayor, math.hypot(px - self.centro_x, py - self.centro_y))

        ancho = max(10, self.canvas.winfo_width())
        alto = max(10, self.canvas.winfo_height())
        margen = 40
        escala = (min(ancho, alto) / 2 - margen) / mayor
        return max(self.zoom_min, min(self.zoom_max, escala))

    def _mundo_a_canvas(self, x: float, y: float) -> tuple[float, float]:
        ancho = self.canvas.winfo_width()
        alto = self.canvas.winfo_height()
        cx = ancho / 2 + (x - self.centro_x) * self.escala_actual
        cy = alto / 2 - (y - self.centro_y) * self.escala_actual
        return cx, cy

    def _asegurar_estrellas(self) -> None:
        ancho = max(1, self.canvas.winfo_width())
        alto = max(1, self.canvas.winfo_height())

        if self.estrellas and ancho == self._estrellas_ancho and alto == self._estrellas_alto:
            return

        self._estrellas_ancho = ancho
        self._estrellas_alto = alto

        area = ancho * alto
        cantidad = max(80, min(260, area // 9000))
        paleta = ["#dbeafe", "#e2e8f0", "#cbd5e1", "#f8fafc"]

        rng = random.Random(ancho * 1_000_003 + alto)
        self.estrellas = [
            (
                rng.uniform(0, ancho),
                rng.uniform(0, alto),
                rng.choice((1, 1, 1, 2)),
                rng.choice(paleta),
            )
            for _ in range(int(cantidad))
        ]

    def _dibujar(self) -> None:
        self.canvas.delete("all")

        ancho = self.canvas.winfo_width()
        alto = self.canvas.winfo_height()

        self._asegurar_estrellas()

        for sx, sy, tam, color in self.estrellas:
            self.canvas.create_oval(sx, sy, sx + tam, sy + tam, fill=color, outline="")

        self.escala_actual = self._escala_mundo()

        self.canvas.create_line(0, alto / 2, ancho, alto / 2, fill=AXIS)
        self.canvas.create_line(ancho / 2, 0, ancho / 2, alto, fill=AXIS)

        for c in self.simulador.cuerpos:
            if len(c.trayectoria) > 1:
                puntos = []
                for px, py in c.trayectoria:
                    sx, sy = self._mundo_a_canvas(px, py)
                    puntos.extend((sx, sy))
                self.canvas.create_line(*puntos, fill=TRAIL, smooth=True)

            sx, sy = self._mundo_a_canvas(c.x, c.y)
            r = c.radio_px
            self.canvas.create_oval(sx - r, sy - r, sx + r, sy + r, fill=c.color, outline="")
            self.canvas.create_text(
                sx + r + 4,
                sy - r - 2,
                text=c.nombre,
                fill=TEXT,
                anchor="sw",
                font=FONT_LABEL,
            )


def iniciar_app() -> None:
    app = AppSimulador()
    app.mainloop()
