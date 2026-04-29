"""
fisicaSuperposicion (paquete superposicion)
"""
import math
from constantes import Constantes


class MotorFisico:
    @staticmethod
    def fuerza_entre_cargas(q_fuente, pos_fuente, q_objetivo, pos_objetivo):
        dx = pos_objetivo[0] - pos_fuente[0]
        dy = pos_objetivo[1] - pos_fuente[1]
        r2 = dx**2 + dy**2

        if r2 == 0:
            raise ValueError(
                "Dos cargas están en la misma posición. "
                "Verifica las coordenadas."
            )

        r = math.sqrt(r2)
        F = Constantes.K_E * q_fuente * q_objetivo / r2
        return (F * dx / r, F * dy / r)

    @staticmethod
    def fuerza_neta(cargas_fuente, q_objetivo, pos_objetivo):
        Fx_total = 0.0
        Fy_total = 0.0
        detalles = []

        for i, (q, pos) in enumerate(cargas_fuente):
            Fx_i, Fy_i = MotorFisico.fuerza_entre_cargas(
                q, pos, q_objetivo, pos_objetivo
            )
            detalles.append((i + 1, q, pos, Fx_i, Fy_i))
            Fx_total += Fx_i
            Fy_total += Fy_i

        magnitud = math.sqrt(Fx_total**2 + Fy_total**2)
        angulo   = math.degrees(math.atan2(Fy_total, Fx_total))

        return Fx_total, Fy_total, magnitud, angulo, detalles

    @staticmethod
    def formatear(valor):
        if valor != 0 and (abs(valor) >= 1e6 or abs(valor) < 1e-3):
            return f"{valor:.4e}"
        return f"{valor:.6f}"

    @staticmethod
    def escala_flechas(detalles, Fx, Fy):
        fuerzas = [math.sqrt(fx**2 + fy**2) for _, _, _, fx, fy in detalles]
        fuerzas.append(math.sqrt(Fx**2 + Fy**2))
        max_F = max((f for f in fuerzas if f > 0), default=1.0)
        return 1.0 / max_F
