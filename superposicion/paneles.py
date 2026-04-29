"""
paneles (paquete superposicion)
"""
import math
import tkinter as tk

from constantes import Constantes
from .fisicaSuperposicion import MotorFisico
from .widgets import CargaWidget, hacer_titulo_seccion

try:
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MPL_DISPONIBLE = True
except ImportError:
    MPL_DISPONIBLE = False


class PanelObjetivo:
    def __init__(self, contenedor):
        C = Constantes
        hacer_titulo_seccion(contenedor, "CARGA OBJETIVO (Q)")

        tarjeta = tk.Frame(
            contenedor, bg=C.CARD_BG, pady=8, padx=10,
            highlightbackground=C.BORDER, highlightthickness=1
        )
        tarjeta.pack(fill="x", pady=4)

        fila = tk.Frame(tarjeta, bg=C.CARD_BG)
        fila.pack()

        campos = [
            ("Carga Q (μC)", "entrada_q"),
            ("x₀ (m)",       "entrada_x"),
            ("y₀ (m)",       "entrada_y"),
        ]
        for etiqueta, atributo in campos:
            col = tk.Frame(fila, bg=C.CARD_BG)
            col.pack(side="left", padx=10)
            tk.Label(col, text=etiqueta, font=C.SMALL,
                     fg=C.TEXT_MUTED, bg=C.CARD_BG).pack()
            entrada = tk.Entry(
                col, width=10, font=C.MONO,
                bg=C.INPUT_BG, fg=C.TEXT_PRIMARY,
                insertbackground=C.ACCENT,
                relief="flat", bd=0,
                highlightbackground=C.BORDER,
                highlightcolor=C.ACCENT, highlightthickness=1
            )
            entrada.pack(ipady=4, padx=2)
            setattr(self, atributo, entrada)

        self.entrada_q.insert(0, "1")
        self.entrada_x.insert(0, "0")
        self.entrada_y.insert(0, "0")

    def obtener_valores(self):
        try:
            q = float(self.entrada_q.get()) * 1e-6
            x = float(self.entrada_x.get())
            y = float(self.entrada_y.get())
            return q, x, y
        except ValueError:
            raise ValueError(
                "Los datos de la carga objetivo son inválidos. "
                "Usa números (ejemplo: 1, 0, 0)."
            )

    def limpiar(self):
        defaults = [
            (self.entrada_q, "1"),
            (self.entrada_x, "0"),
            (self.entrada_y, "0"),
        ]
        for entrada, valor in defaults:
            entrada.delete(0, "end")
            entrada.insert(0, valor)


class PanelCargas:
    def __init__(self, contenedor):
        C = Constantes
        self._widgets = []

        hacer_titulo_seccion(contenedor, "CARGAS FUENTE (n cargas)")

        barra = tk.Frame(contenedor, bg=C.DARK_BG)
        barra.pack(fill="x", pady=(0, 4))

        tk.Button(
            barra, text="＋  Agregar carga", font=C.SMALL,
            fg=C.DARK_BG, bg=C.ACCENT2, activebackground="#2ea043",
            relief="flat", bd=0, padx=10, pady=4, cursor="hand2",
            command=self.agregar
        ).pack(side="left", padx=2)

        self._lbl_contador = tk.Label(
            barra, text="0 cargas", font=C.SMALL,
            fg=C.TEXT_MUTED, bg=C.DARK_BG
        )
        self._lbl_contador.pack(side="left", padx=10)

        marco_ext = tk.Frame(contenedor, bg=C.DARK_BG, height=180)
        marco_ext.pack(fill="x")
        marco_ext.pack_propagate(False)

        canvas_scroll = tk.Canvas(
            marco_ext, bg=C.DARK_BG, bd=0, highlightthickness=0
        )
        scrollbar = tk.Scrollbar(
            marco_ext, orient="vertical", command=canvas_scroll.yview
        )
        self._lista = tk.Frame(canvas_scroll, bg=C.DARK_BG)

        self._lista.bind(
            "<Configure>",
            lambda e: canvas_scroll.configure(
                scrollregion=canvas_scroll.bbox("all")
            )
        )
        canvas_scroll.create_window((0, 0), window=self._lista, anchor="nw")
        canvas_scroll.configure(yscrollcommand=scrollbar.set)
        canvas_scroll.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.agregar()
        self.agregar()
        self._widgets[0].entrada_q.insert(0, "2");  self._widgets[0].entrada_x.insert(0, "3");  self._widgets[0].entrada_y.insert(0, "0")
        self._widgets[1].entrada_q.insert(0, "-1"); self._widgets[1].entrada_x.insert(0, "0");  self._widgets[1].entrada_y.insert(0, "4")

    def agregar(self):
        numero = len(self._widgets) + 1
        widget = CargaWidget(self._lista, numero, self._borrar)
        self._widgets.append(widget)
        self._actualizar_contador()

    def obtener_todas(self):
        return [w.obtener_valores() for w in self._widgets]

    def hay_cargas(self):
        return len(self._widgets) > 0

    def limpiar(self):
        for w in self._widgets[:]:
            w.destruir()
        self._widgets.clear()
        self._actualizar_contador()

    def _borrar(self, widget):
        widget.destruir()
        self._widgets.remove(widget)
        for i, w in enumerate(self._widgets):
            w.renombrar(i + 1)
        self._actualizar_contador()

    def _actualizar_contador(self):
        n = len(self._widgets)
        self._lbl_contador.config(
            text=f"{n} carga{'s' if n != 1 else ''}"
        )


class PanelResultados:
    def __init__(self, contenedor):
        C = Constantes
        hacer_titulo_seccion(contenedor, "RESULTADOS")

        self._frame = tk.Frame(
            contenedor, bg=C.CARD_BG, pady=10, padx=14,
            highlightbackground=C.BORDER, highlightthickness=1
        )
        self._frame.pack(fill="x", pady=4)
        self._mostrar_placeholder()

    def mostrar(self, Fx, Fy, magnitud, angulo, detalles):
        self._limpiar_frame()
        C  = Constantes
        fm = MotorFisico.formatear

        lineas = [("─── Fuerzas individuales ───", C.TEXT_MUTED, C.MONO)]

        for n, q, pos, fx, fy in detalles:
            m = math.sqrt(fx**2 + fy**2)
            texto = (
                f"  q{n} ({q*1e6:+.3f} μC  @  {pos[0]}, {pos[1]}):  "
                f"Fx={fm(fx)} N   Fy={fm(fy)} N   |F|={fm(m)} N"
            )
            lineas.append((texto, C.TEXT_PRIMARY, C.MONO))

        lineas += [
            ("", None, None),
            ("─── Fuerza NETA ───",                      C.ACCENT2, C.SECCION),
            (f"  F⃗  =  < {fm(Fx)},  {fm(Fy)} >  N",    C.ACCENT,  C.RESULT),
            (f"  |F| =  {fm(magnitud)} N",                C.ACCENT,  C.RESULT),
            (f"  θ   =  {angulo:.4f}°",                   C.ACCENT,  C.RESULT),
        ]

        for texto, color, fuente in lineas:
            if not texto:
                tk.Label(self._frame, text="",
                         font=("Courier New", 4), bg=C.CARD_BG).pack(anchor="w")
                continue
            tk.Label(
                self._frame, text=texto,
                font=fuente, fg=color,
                bg=C.CARD_BG, justify="left"
            ).pack(anchor="w")

    def limpiar(self):
        self._limpiar_frame()
        self._mostrar_placeholder()

    def _limpiar_frame(self):
        for w in self._frame.winfo_children():
            w.destroy()

    def _mostrar_placeholder(self):
        C = Constantes
        tk.Label(
            self._frame,
            text="Ingresa los datos y presiona  ⚡ CALCULAR",
            font=C.MONO, fg=C.TEXT_MUTED, bg=C.CARD_BG, justify="left"
        ).pack(anchor="w")


class PanelGrafica:
    def __init__(self, contenedor):
        C = Constantes
        tk.Label(
            contenedor, text="VISUALIZACIÓN", font=C.SMALL,
            fg=C.TEXT_MUTED, bg=C.CARD_BG
        ).pack(pady=(10, 0))

        tk.Label(
            contenedor,
            text="Rueda: zoom  ·  Arrastrar: mover  ·  Doble clic: reiniciar",
            font=("Courier New", 8), fg=C.TEXT_MUTED, bg=C.CARD_BG
        ).pack(pady=(0, 4))

        if not MPL_DISPONIBLE:
            tk.Label(
                contenedor,
                text="Instala matplotlib para ver la gráfica:\n\npip install matplotlib numpy",
                font=C.MONO, fg=C.TEXT_MUTED, bg=C.CARD_BG, justify="center"
            ).pack(expand=True)
            self._disponible = False
            return

        self._disponible = True
        fig, self._ax = plt.subplots(figsize=(5.2, 5.2), facecolor=C.DARK_BG)
        self._ax.set_facecolor(C.CARD_BG)

        self._vista_guardada = None
        self._arrastre_activo = False
        self._arrastre_inicio = None

        self._canvas = FigureCanvasTkAgg(fig, master=contenedor)
        self._canvas_widget = self._canvas.get_tk_widget()
        self._canvas_widget.pack(fill="both", expand=True, padx=6, pady=6)

        self._canvas.mpl_connect("scroll_event", self._on_scroll)
        self._canvas.mpl_connect("button_press_event", self._on_press)
        self._canvas.mpl_connect("button_release_event", self._on_release)
        self._canvas.mpl_connect("motion_notify_event", self._on_motion)

        self.limpiar()

    def dibujar(self, cargas_fuente, q_obj, pos_obj, Fx, Fy, detalles):
        if not self._disponible:
            return

        C  = Constantes
        ax = self._ax
        ax.clear()
        self._configurar_ejes(ax)

        escala = MotorFisico.escala_flechas(detalles, Fx, Fy)

        for n, q, pos, fx, fy in detalles:
            color = self._color_carga(q)
            ax.plot(pos[0], pos[1], 'o', markersize=10, color=color, zorder=5)
            ax.annotate(
                f"q{n}\n{q*1e6:+.2f} μC",
                xy=pos, xytext=(pos[0] + 0.15, pos[1] + 0.15),
                color=color, fontsize=7, fontweight="bold"
            )
            ax.annotate(
                "",
                xy=(pos_obj[0] + fx * escala, pos_obj[1] + fy * escala),
                xytext=pos_obj,
                arrowprops=dict(arrowstyle="->", color=color, lw=1.2, alpha=0.7)
            )

        color_obj = self._color_carga(q_obj)
        ax.plot(
            pos_obj[0], pos_obj[1], '*', markersize=16,
            color=color_obj, zorder=6,
            markeredgecolor="white", markeredgewidth=0.5
        )
        ax.annotate(
            f"Q = {q_obj*1e6:+.2f} μC",
            xy=pos_obj,
            xytext=(pos_obj[0] + 0.15, pos_obj[1] - 0.3),
            color=color_obj, fontsize=7, fontweight="bold"
        )

        mag = math.sqrt(Fx**2 + Fy**2)
        if mag > 0:
            ax.annotate(
                "",
                xy=(pos_obj[0] + Fx * escala * 1.3,
                    pos_obj[1] + Fy * escala * 1.3),
                xytext=pos_obj,
                arrowprops=dict(arrowstyle="-|>", color=C.ACCENT, lw=2.5)
            )
            ax.text(
                pos_obj[0] + Fx * escala * 1.4,
                pos_obj[1] + Fy * escala * 1.4,
                f"F⃗ neta\n{mag:.3e} N",
                color=C.ACCENT, fontsize=7, fontweight="bold", ha="center"
            )

        leyenda = [
            mpatches.Patch(color=C.ACCENT2,    label="Carga positiva"),
            mpatches.Patch(color=C.ACCENT_RED, label="Carga negativa"),
            mpatches.Patch(color=C.ACCENT,     label="Fuerza neta"),
        ]
        ax.legend(
            handles=leyenda, fontsize=7, loc="upper right",
            facecolor=C.CARD_BG, edgecolor=C.BORDER,
            labelcolor=C.TEXT_PRIMARY
        )
        ax.margins(0.25)
        self._vista_guardada = (ax.get_xlim(), ax.get_ylim())
        self._canvas.draw()

    def _on_scroll(self, event):
        if not self._disponible or event.inaxes != self._ax:
            return
        if event.xdata is None or event.ydata is None:
            return

        boton = getattr(event, "button", None)
        if boton in ("up", 1):
            factor = 0.85
        elif boton in ("down", 2):
            factor = 1.15
        else:
            return

        self._zoom_en_punto(event.xdata, event.ydata, factor)

    def _on_press(self, event):
        if not self._disponible or event.inaxes != self._ax:
            return
        if getattr(event, "button", None) != 1:
            return
        if getattr(event, "dblclick", False):
            self._restablecer_vista()
            return
        if event.xdata is None or event.ydata is None:
            return

        self._arrastre_activo = True
        self._arrastre_inicio = {
            "x": event.xdata,
            "y": event.ydata,
            "xlim": self._ax.get_xlim(),
            "ylim": self._ax.get_ylim(),
        }

    def _on_motion(self, event):
        if not self._disponible or not self._arrastre_activo:
            return
        if self._arrastre_inicio is None or event.inaxes != self._ax:
            return
        if event.xdata is None or event.ydata is None:
            return

        inicio = self._arrastre_inicio
        desplazamiento_x = inicio["x"] - event.xdata
        desplazamiento_y = inicio["y"] - event.ydata

        xlim = inicio["xlim"]
        ylim = inicio["ylim"]
        self._ax.set_xlim(xlim[0] + desplazamiento_x, xlim[1] + desplazamiento_x)
        self._ax.set_ylim(ylim[0] + desplazamiento_y, ylim[1] + desplazamiento_y)
        self._canvas.draw_idle()

    def _on_release(self, event):
        self._arrastre_activo = False
        self._arrastre_inicio = None

    def _zoom_en_punto(self, x_centro, y_centro, factor):
        ax = self._ax
        x_min, x_max = ax.get_xlim()
        y_min, y_max = ax.get_ylim()

        nuevo_xmin = x_centro - (x_centro - x_min) * factor
        nuevo_xmax = x_centro + (x_max - x_centro) * factor
        nuevo_ymin = y_centro - (y_centro - y_min) * factor
        nuevo_ymax = y_centro + (y_max - y_centro) * factor

        ax.set_xlim(nuevo_xmin, nuevo_xmax)
        ax.set_ylim(nuevo_ymin, nuevo_ymax)
        self._canvas.draw_idle()

    def _restablecer_vista(self):
        if self._vista_guardada is None:
            return
        xlim, ylim = self._vista_guardada
        self._ax.set_xlim(xlim)
        self._ax.set_ylim(ylim)
        self._canvas.draw_idle()

    def limpiar(self):
        if not self._disponible:
            return
        C  = Constantes
        ax = self._ax
        ax.clear()
        self._configurar_ejes(ax)
        ax.text(
            0.5, 0.5,
            "Presiona ⚡ CALCULAR\npara visualizar",
            transform=ax.transAxes,
            ha="center", va="center",
            color=C.TEXT_MUTED, fontsize=10, style="italic"
        )
        self._vista_guardada = (ax.get_xlim(), ax.get_ylim())
        self._canvas.draw()

    def _configurar_ejes(self, ax):
        C = Constantes
        ax.set_facecolor(C.CARD_BG)
        ax.tick_params(colors=C.TEXT_MUTED, labelsize=7)
        for spine in ax.spines.values():
            spine.set_edgecolor(C.BORDER)
        ax.set_xlabel("x (m)", color=C.TEXT_MUTED, fontsize=8)
        ax.set_ylabel("y (m)", color=C.TEXT_MUTED, fontsize=8)
        ax.set_title(
            "Diagrama de fuerzas – Ley de Coulomb",
            color=C.TEXT_PRIMARY, fontsize=9
        )
        ax.grid(True, color=C.BORDER, linewidth=0.5, alpha=0.5)
        ax.axhline(0, color=C.BORDER, lw=0.8)
        ax.axvline(0, color=C.BORDER, lw=0.8)

    @staticmethod
    def _color_carga(q):
        return Constantes.ACCENT_RED if q < 0 else Constantes.ACCENT2
