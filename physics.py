"""Fisica del movimiento parabólico y del experimento cazador y mono."""

import math


def calcular_trayectoria(velocidad_inicial, angulo_grados, altura_inicial, gravedad, muestras=80, tiempo_maximo=None):
    """Calcula la trayectoria del proyectil y devuelve puntos de muestreo."""
    angulo_radianes = math.radians(angulo_grados)
    velocidad_x = velocidad_inicial * math.cos(angulo_radianes)
    velocidad_y_inicial = velocidad_inicial * math.sin(angulo_radianes)

    impacto_suelo = True
    if gravedad > 0:
        discriminante = (velocidad_y_inicial ** 2) + (2 * gravedad * altura_inicial)
        tiempo_vuelo = (velocidad_y_inicial + math.sqrt(discriminante)) / gravedad
        altura_maxima = altura_inicial + (velocidad_y_inicial ** 2) / (2 * gravedad)
        tiempo_altura_maxima = velocidad_y_inicial / gravedad
    else:
        tiempo_altura_maxima = float("inf") if velocidad_y_inicial > 0 else 0.0
        altura_maxima = float("inf") if velocidad_y_inicial > 0 else altura_inicial
        if velocidad_y_inicial < 0 and altura_inicial >= 0:
            tiempo_vuelo = altura_inicial / (-velocidad_y_inicial) if velocidad_y_inicial != 0 else 0.0
        else:
            impacto_suelo = False
            tiempo_vuelo = tiempo_maximo if tiempo_maximo and tiempo_maximo > 0 else 10.0

    alcance_horizontal = velocidad_x * tiempo_vuelo

    puntos = []
    for indice in range(muestras + 1):
        tiempo = tiempo_vuelo * indice / muestras
        posicion_x = velocidad_x * tiempo
        posicion_y = altura_inicial + (velocidad_y_inicial * tiempo) - (0.5 * gravedad * (tiempo ** 2))
        velocidad_y = velocidad_y_inicial - (gravedad * tiempo)
        puntos.append(
            {
                "t": tiempo,
                "x": posicion_x,
                "y": max(0.0, posicion_y),
                "vx": velocidad_x,
                "vy": velocidad_y,
            }
        )

    return {
        "angulo_radianes": angulo_radianes,
        "vx": velocidad_x,
        "vy0": velocidad_y_inicial,
        "tiempo_vuelo": tiempo_vuelo,
        "altura_maxima": altura_maxima,
        "alcance_horizontal": alcance_horizontal,
        "tiempo_altura_maxima": max(0.0, tiempo_altura_maxima),
        "impacto_suelo": impacto_suelo,
        "tiempo_simulacion": tiempo_vuelo,
        "puntos": puntos,
    }


def calcular_intercepcion(datos_proyectil, altura_objeto, posicion_x_objeto, gravedad, retraso_caida):
    """Evalúa si el proyectil y el objeto en caída coinciden en la misma posición."""
    if datos_proyectil["vx"] <= 0:
        return {
            "hay_intercepcion": False,
            "motivo": "El proyectil no avanza horizontalmente hacia el objeto.",
        }

    tiempo_interseccion_x = posicion_x_objeto / datos_proyectil["vx"]
    if tiempo_interseccion_x < 0:
        return {
            "hay_intercepcion": False,
            "motivo": "La posicion horizontal del objeto debe ser positiva.",
        }
    if datos_proyectil.get("impacto_suelo", True) and tiempo_interseccion_x > datos_proyectil["tiempo_vuelo"]:
        return {
            "hay_intercepcion": False,
            "tiempo": tiempo_interseccion_x,
            "motivo": "El proyectil cae al suelo antes de llegar a la posicion horizontal del objeto.",
        }

    altura_proyectil = (
        datos_proyectil["puntos"][0]["y"]
        + (datos_proyectil["vy0"] * tiempo_interseccion_x)
        - (0.5 * gravedad * (tiempo_interseccion_x ** 2))
    )
    if tiempo_interseccion_x < retraso_caida:
        altura_objeto_t = altura_objeto
        velocidad_objeto = 0.0
    else:
        tiempo_caida = tiempo_interseccion_x - retraso_caida
        altura_objeto_t = altura_objeto - (0.5 * gravedad * (tiempo_caida ** 2))
        velocidad_objeto = -gravedad * tiempo_caida

    tolerancia = 0.35
    hay_intercepcion = altura_proyectil >= 0 and altura_objeto_t >= 0 and abs(altura_proyectil - altura_objeto_t) <= tolerancia

    return {
        "hay_intercepcion": hay_intercepcion,
        "tiempo": tiempo_interseccion_x,
        "x": posicion_x_objeto,
        "y_proyectil": altura_proyectil,
        "y_objeto": altura_objeto_t,
        "vy_objeto": velocidad_objeto,
        "motivo": "Intercepcion detectada." if hay_intercepcion else "Las trayectorias no coinciden en la misma altura.",
    }


def calcular_altura_para_intercepcion(datos_proyectil, posicion_x_objeto, gravedad, retraso_caida):
    """Obtiene la altura inicial que debe tener el objeto para que el encuentro ocurra."""
    if datos_proyectil["vx"] <= 0:
        return None, "El proyectil no avanza horizontalmente hacia el objeto."
    if gravedad <= 0:
        return None, "El calculo automatico de altura requiere gravedad positiva."

    tiempo_objetivo = posicion_x_objeto / datos_proyectil["vx"]
    if tiempo_objetivo < 0 or tiempo_objetivo > datos_proyectil["tiempo_vuelo"]:
        return None, "El proyectil no pasa por la posicion horizontal indicada mientras esta en vuelo."

    altura_proyectil = (
        datos_proyectil["puntos"][0]["y"]
        + (datos_proyectil["vy0"] * tiempo_objetivo)
        - (0.5 * gravedad * (tiempo_objetivo ** 2))
    )
    if altura_proyectil < 0:
        return None, "La altura del proyectil en esa posicion es negativa."

    if tiempo_objetivo <= retraso_caida:
        altura_requerida = altura_proyectil
    else:
        tiempo_caida = tiempo_objetivo - retraso_caida
        altura_requerida = altura_proyectil + (0.5 * gravedad * (tiempo_caida ** 2))

    return altura_requerida, None


def calcular_retraso_para_intercepcion(datos_proyectil, altura_objeto, posicion_x_objeto, gravedad):
    """Obtiene el retraso de caída que hace posible la intercepción."""
    if datos_proyectil["vx"] <= 0:
        return None, "El proyectil no avanza horizontalmente hacia el objeto."
    if gravedad <= 0:
        return None, "El calculo automatico de retraso requiere gravedad positiva."

    tiempo_objetivo = posicion_x_objeto / datos_proyectil["vx"]
    if tiempo_objetivo < 0 or tiempo_objetivo > datos_proyectil["tiempo_vuelo"]:
        return None, "El proyectil no pasa por la posicion horizontal indicada mientras esta en vuelo."

    altura_proyectil = (
        datos_proyectil["puntos"][0]["y"]
        + (datos_proyectil["vy0"] * tiempo_objetivo)
        - (0.5 * gravedad * (tiempo_objetivo ** 2))
    )
    if altura_objeto < altura_proyectil:
        return None, "La altura inicial del objeto es insuficiente para interceptar al proyectil en esa posicion."

    diferencia = altura_objeto - altura_proyectil
    tiempo_caida = math.sqrt((2 * diferencia) / gravedad) if diferencia > 0 else 0.0
    retraso_requerido = tiempo_objetivo - tiempo_caida
    if retraso_requerido < 0:
        return None, "La intercepcion requeriria iniciar la caida antes de t = 0 s."

    return retraso_requerido, None


def construir_puntos_objeto(puntos_proyectil, objeto_altura, objeto_x, gravedad, retraso):
    """Construye la serie de puntos del objeto suspendido o en caída libre."""
    puntos_objeto = []
    for punto in puntos_proyectil:
        if punto["t"] < retraso:
            altura_t = objeto_altura
            velocidad_y = 0.0
        else:
            tiempo_caida = punto["t"] - retraso
            altura_t = objeto_altura - (0.5 * gravedad * (tiempo_caida ** 2))
            velocidad_y = -gravedad * tiempo_caida

        puntos_objeto.append(
            {
                "t": punto["t"],
                "x": objeto_x,
                "y": max(0.0, altura_t),
                "vy": velocidad_y if altura_t > 0 else 0.0,
            }
        )
    return puntos_objeto


def calcular_angulo_apuntado(altura_inicial, objeto_altura, objeto_x):
    """Calcula el ángulo hacia la posición inicial del objeto suspendido."""
    diferencia_altura = objeto_altura - altura_inicial
    return math.degrees(math.atan2(diferencia_altura, objeto_x))


def evaluar_cazador_mono(datos_proyectil, altura_inicial, objeto_altura, objeto_x, gravedad):
    """Resume la condición teórica del experimento cazador y mono."""
    rapidez_inicial = math.hypot(datos_proyectil["vx"], datos_proyectil["vy0"])
    distancia_directa = math.hypot(objeto_x, objeto_altura - altura_inicial)
    tiempo_teorico = distancia_directa / rapidez_inicial if rapidez_inicial > 0 else float("inf")
    if gravedad > 0:
        tiempo_caida_mono = math.sqrt((2 * objeto_altura) / gravedad) if objeto_altura > 0 else 0.0
    else:
        tiempo_caida_mono = float("inf")
    return {
        "distancia_directa": distancia_directa,
        "tiempo_teorico": tiempo_teorico,
        "tiempo_caida_mono": tiempo_caida_mono,
        "exito_teorico": gravedad > 0 and tiempo_teorico <= tiempo_caida_mono,
    }


def reajustar_posicion_mono_por_velocidad(altura_inicial, objeto_x, objeto_altura, velocidad_anterior, velocidad_nueva):
    """Escala la posicion del mono sobre la misma linea de punteria al cambiar la velocidad.

    La escala se hace respecto a la distancia inicial desde el lanzador al mono.
    Si la velocidad nueva es mayor, el mono se aleja; si es menor, se acerca.
    """
    distancia_actual = math.hypot(objeto_x, objeto_altura - altura_inicial)
    if distancia_actual == 0:
        return objeto_x, objeto_altura
    if velocidad_anterior <= 0:
        return objeto_x, objeto_altura

    factor_escala = velocidad_nueva / velocidad_anterior
    distancia_nueva = distancia_actual * factor_escala
    escala = distancia_nueva / distancia_actual
    nueva_x = objeto_x * escala
    nueva_altura = altura_inicial + ((objeto_altura - altura_inicial) * escala)
    return nueva_x, nueva_altura
