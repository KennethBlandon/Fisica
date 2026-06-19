import math

GRAVEDAD_TIERRA = 9.81


def calcular_angulo_de_punteria(altura_lanzador, altura_mono, posicion_x_lanzador, posicion_x_mono):
    distancia_horizontal = posicion_x_mono - posicion_x_lanzador
    diferencia_altura = altura_mono - altura_lanzador

    angulo_radianes = math.atan2(diferencia_altura, distancia_horizontal)
    angulo_grados = math.degrees(angulo_radianes)

    return angulo_grados


def calcular_datos_experimento(datos_experimento):
    posicion_x_lanzador = datos_experimento["posicion_x_lanzador"]
    altura_lanzador = datos_experimento["altura_lanzador"]
    posicion_x_mono = datos_experimento["posicion_x_mono"]
    altura_mono = datos_experimento["altura_mono"]
    velocidad_inicial = datos_experimento["velocidad_inicial"]

    distancia_horizontal = posicion_x_mono - posicion_x_lanzador
    diferencia_altura = altura_mono - altura_lanzador
    distancia_directa = math.hypot(distancia_horizontal, diferencia_altura)

    angulo_grados = calcular_angulo_de_punteria(
        altura_lanzador,
        altura_mono,
        posicion_x_lanzador,
        posicion_x_mono,
    )

    angulo_radianes = math.radians(angulo_grados)

    velocidad_horizontal = velocidad_inicial * math.cos(angulo_radianes)
    velocidad_vertical = velocidad_inicial * math.sin(angulo_radianes)

    tiempo_choque = distancia_directa / velocidad_inicial

    posicion_x_choque = posicion_x_lanzador + velocidad_horizontal * tiempo_choque
    altura_choque = altura_lanzador + velocidad_vertical * tiempo_choque - (
        0.5 * GRAVEDAD_TIERRA * tiempo_choque ** 2
    )

    tiempo_caida_mono = math.sqrt((2 * altura_mono) / GRAVEDAD_TIERRA)

    hay_choque_en_aire = altura_choque > 0 and tiempo_choque <= tiempo_caida_mono

    if hay_choque_en_aire:
        estado = "Chocan en el aire"
    else:
        estado = "No chocan en el aire"

    return {
        "angulo_grados": angulo_grados,
        "tiempo_choque": tiempo_choque,
        "posicion_x_choque": posicion_x_choque,
        "altura_choque": altura_choque,
        "tiempo_caida_mono": tiempo_caida_mono,
        "estado": estado,
        "hay_choque_en_aire": hay_choque_en_aire,
    }


def calcular_trayectoria_experimento(datos_experimento, cantidad_puntos=80):
    datos_calculados = calcular_datos_experimento(datos_experimento)

    posicion_x_lanzador = datos_experimento["posicion_x_lanzador"]
    altura_lanzador = datos_experimento["altura_lanzador"]
    posicion_x_mono = datos_experimento["posicion_x_mono"]
    altura_mono = datos_experimento["altura_mono"]
    velocidad_inicial = datos_experimento["velocidad_inicial"]

    angulo_radianes = math.radians(datos_calculados["angulo_grados"])

    velocidad_horizontal = velocidad_inicial * math.cos(angulo_radianes)
    velocidad_vertical = velocidad_inicial * math.sin(angulo_radianes)

    tiempo_final = datos_calculados["tiempo_choque"]

    puntos_proyectil = []
    puntos_mono = []

    for indice_punto in range(cantidad_puntos + 1):
        tiempo_actual = tiempo_final * indice_punto / cantidad_puntos

        posicion_x_proyectil = posicion_x_lanzador + velocidad_horizontal * tiempo_actual
        altura_proyectil = altura_lanzador + velocidad_vertical * tiempo_actual - (
            0.5 * GRAVEDAD_TIERRA * tiempo_actual ** 2
        )

        altura_mono_actual = altura_mono - (
            0.5 * GRAVEDAD_TIERRA * tiempo_actual ** 2
        )

        puntos_proyectil.append(
            {
                "tiempo": tiempo_actual,
                "x": posicion_x_proyectil,
                "y": altura_proyectil,
            }
        )

        puntos_mono.append(
            {
                "tiempo": tiempo_actual,
                "x": posicion_x_mono,
                "y": altura_mono_actual,
            }
        )

    return {
        "datos_calculados": datos_calculados,
        "puntos_proyectil": puntos_proyectil,
        "puntos_mono": puntos_mono,
    }