"""Motor fisico de simulacion gravitacional 2D."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
import math


VELOCIDAD_LUZ = 299_792_458.0


@dataclass
class Cuerpo:
    nombre: str
    masa: float
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    color: str = "#38bdf8"
    radio_px: int = 6
    trayectoria: deque[tuple[float, float]] = field(
        default_factory=lambda: deque(maxlen=400), repr=False
    )
    historial: deque[tuple[float, float, float]] = field(
        default_factory=lambda: deque(maxlen=5000), repr=False
    )

    def clonar(self) -> "Cuerpo":
        copia = Cuerpo(
            nombre=self.nombre,
            masa=self.masa,
            x=self.x,
            y=self.y,
            vx=self.vx,
            vy=self.vy,
            color=self.color,
            radio_px=self.radio_px,
        )
        copia.trayectoria = deque(self.trayectoria, maxlen=400)
        copia.historial = deque(self.historial, maxlen=5000)
        return copia


class SimuladorNBody:
    def __init__(self, g: float = 6.674e-11, dt: float = 3600.0, suavizado: float = 1e6) -> None:
        self.G = g
        self.dt = dt
        self.suavizado = suavizado
        self.usar_retardo_gravitacional = False
        self.velocidad_gravedad = VELOCIDAD_LUZ
        self.tiempo_total = 0.0
        self.cuerpos: list[Cuerpo] = []
        self._estado_inicial: list[Cuerpo] = []

    def agregar_cuerpo(self, cuerpo: Cuerpo) -> None:
        if not cuerpo.trayectoria:
            cuerpo.trayectoria.append((cuerpo.x, cuerpo.y))
        if not cuerpo.historial:
            cuerpo.historial.append((self.tiempo_total, cuerpo.x, cuerpo.y))
        self.cuerpos.append(cuerpo)

    def eliminar_cuerpo(self, indice: int) -> None:
        if 0 <= indice < len(self.cuerpos):
            self.cuerpos.pop(indice)

    def guardar_estado_inicial(self) -> None:
        self._estado_inicial = [c.clonar() for c in self.cuerpos]

    def reiniciar(self) -> None:
        self.cuerpos = [c.clonar() for c in self._estado_inicial]
        self.tiempo_total = 0.0

    def establecer_cuerpos(self, cuerpos: list[Cuerpo], guardar_inicial: bool = True) -> None:
        self.cuerpos = [c.clonar() for c in cuerpos]
        for cuerpo in self.cuerpos:
            if not cuerpo.trayectoria:
                cuerpo.trayectoria.append((cuerpo.x, cuerpo.y))
            if not cuerpo.historial:
                cuerpo.historial.append((0.0, cuerpo.x, cuerpo.y))
        self.tiempo_total = 0.0
        if guardar_inicial:
            self.guardar_estado_inicial()

    def paso(self, subpasos: int = 1) -> None:
        if len(self.cuerpos) < 1:
            return
        for _ in range(max(1, subpasos)):
            if self.usar_retardo_gravitacional:
                self._integrar_con_retardo()
            else:
                self._integrar_velocity_verlet()
            self.tiempo_total += self.dt
            for cuerpo in self.cuerpos:
                cuerpo.historial.append((self.tiempo_total, cuerpo.x, cuerpo.y))

    def _calcular_aceleraciones(self) -> tuple[list[float], list[float]]:
        n = len(self.cuerpos)
        if n == 0:
            return [], []

        ax = [0.0] * n
        ay = [0.0] * n

        # Suma de contribuciones gravitacionales por pares: O(n^2).
        for i in range(n):
            ci = self.cuerpos[i]
            for j in range(i + 1, n):
                cj = self.cuerpos[j]
                dx = cj.x - ci.x
                dy = cj.y - ci.y

                dist2 = dx * dx + dy * dy + self.suavizado * self.suavizado
                dist = math.sqrt(dist2)
                inv_dist3 = 1.0 / (dist2 * dist)

                factor = self.G * inv_dist3

                ax[i] += factor * cj.masa * dx
                ay[i] += factor * cj.masa * dy

                ax[j] -= factor * ci.masa * dx
                ay[j] -= factor * ci.masa * dy

        return ax, ay

    def _posicion_retrasada(self, indice: int, tiempo_objetivo: float) -> tuple[float, float]:
        cuerpo = self.cuerpos[indice]
        if not cuerpo.historial:
            return cuerpo.x, cuerpo.y

        if tiempo_objetivo <= cuerpo.historial[0][0]:
            _, x0, y0 = cuerpo.historial[0]
            return x0, y0

        if tiempo_objetivo >= cuerpo.historial[-1][0]:
            _, xf, yf = cuerpo.historial[-1]
            return xf, yf

        for k in range(1, len(cuerpo.historial)):
            t1, x1, y1 = cuerpo.historial[k]
            t0, x0, y0 = cuerpo.historial[k - 1]
            if t0 <= tiempo_objetivo <= t1:
                if t1 == t0:
                    return x1, y1
                alpha = (tiempo_objetivo - t0) / (t1 - t0)
                xr = x0 + alpha * (x1 - x0)
                yr = y0 + alpha * (y1 - y0)
                return xr, yr

        _, xf, yf = cuerpo.historial[-1]
        return xf, yf

    def _calcular_aceleraciones_retardadas(self) -> tuple[list[float], list[float]]:
        n = len(self.cuerpos)
        if n == 0:
            return [], []

        ax = [0.0] * n
        ay = [0.0] * n
        v_grav = max(1.0, self.velocidad_gravedad)

        for i, ci in enumerate(self.cuerpos):
            for j, cj in enumerate(self.cuerpos):
                if i == j:
                    continue

                dx_actual = cj.x - ci.x
                dy_actual = cj.y - ci.y
                distancia_actual = math.sqrt(
                    dx_actual * dx_actual + dy_actual * dy_actual + self.suavizado * self.suavizado
                )
                tiempo_retardo = self.tiempo_total - distancia_actual / v_grav

                xj_ret, yj_ret = self._posicion_retrasada(j, tiempo_retardo)
                dx = xj_ret - ci.x
                dy = yj_ret - ci.y

                dist2 = dx * dx + dy * dy + self.suavizado * self.suavizado
                dist = math.sqrt(dist2)
                inv_dist3 = 1.0 / (dist2 * dist)
                factor = self.G * inv_dist3

                ax[i] += factor * cj.masa * dx
                ay[i] += factor * cj.masa * dy

        return ax, ay

    def _integrar_velocity_verlet(self) -> None:
        n = len(self.cuerpos)
        if n == 0:
            return

        ax0, ay0 = self._calcular_aceleraciones()

        for i, cuerpo in enumerate(self.cuerpos):
            cuerpo.x += cuerpo.vx * self.dt + 0.5 * ax0[i] * self.dt * self.dt
            cuerpo.y += cuerpo.vy * self.dt + 0.5 * ay0[i] * self.dt * self.dt

        ax1, ay1 = self._calcular_aceleraciones()

        for i, cuerpo in enumerate(self.cuerpos):
            cuerpo.vx += 0.5 * (ax0[i] + ax1[i]) * self.dt
            cuerpo.vy += 0.5 * (ay0[i] + ay1[i]) * self.dt
            cuerpo.trayectoria.append((cuerpo.x, cuerpo.y))

    def _integrar_con_retardo(self) -> None:
        n = len(self.cuerpos)
        if n == 0:
            return

        ax, ay = self._calcular_aceleraciones_retardadas()
        for i, cuerpo in enumerate(self.cuerpos):
            cuerpo.vx += ax[i] * self.dt
            cuerpo.vy += ay[i] * self.dt
            cuerpo.x += cuerpo.vx * self.dt
            cuerpo.y += cuerpo.vy * self.dt
            cuerpo.trayectoria.append((cuerpo.x, cuerpo.y))

    def centro_de_masa(self) -> tuple[float, float]:
        if not self.cuerpos:
            return 0.0, 0.0

        masa_total = sum(c.masa for c in self.cuerpos)
        if masa_total <= 0:
            return 0.0, 0.0

        x_cm = sum(c.masa * c.x for c in self.cuerpos) / masa_total
        y_cm = sum(c.masa * c.y for c in self.cuerpos) / masa_total
        return x_cm, y_cm


def crear_sistema_tierra_sol_luna() -> list[Cuerpo]:
    sol = Cuerpo(
        nombre="Sol",
        masa=1.989e30,
        x=0.0,
        y=0.0,
        vx=0.0,
        vy=0.0,
        color="#f59e0b",
        radio_px=11,
    )

    tierra = Cuerpo(
        nombre="Tierra",
        masa=5.972e24,
        x=1.5e11,
        y=0.0,
        vx=0.0,
        vy=29_885.0,
        color="#3b82f6",
        radio_px=7,
    )

    luna = Cuerpo(
        nombre="Luna",
        masa=7.34767309e22,
        x=1.5e11 + 3.844e8,
        y=0.0,
        vx=0.0,
        vy=29_885.0 + 1_022.0,
        color="#e5e7eb",
        radio_px=4,
    )

    # Ajuste baricentrico para conservar momento lineal total en Y.
    momento_y = tierra.masa * tierra.vy + luna.masa * luna.vy
    sol.vy = -momento_y / sol.masa

    return [sol, tierra, luna]
