def convertir_a_numero(valor_texto, nombre_campo):
    valor_limpio = valor_texto.strip().replace(",", ".")

    if valor_limpio == "":
        raise ValueError(f"El campo '{nombre_campo}' no puede quedar vacío.")

    try:
        return float(valor_limpio)
    except ValueError:
        raise ValueError(f"El campo '{nombre_campo}' debe contener solo números.")


def leer_y_validar_datos(campos_entrada):
    datos_experimento = {
        "posicion_x_lanzador": convertir_a_numero(
            campos_entrada["posicion_x_lanzador"].get(),
            "X del lanzador",
        ),
        "altura_lanzador": convertir_a_numero(
            campos_entrada["altura_lanzador"].get(),
            "Altura del lanzador",
        ),
        "posicion_x_mono": convertir_a_numero(
            campos_entrada["posicion_x_mono"].get(),
            "X del mono",
        ),
        "altura_mono": convertir_a_numero(
            campos_entrada["altura_mono"].get(),
            "Altura inicial del mono",
        ),
        "velocidad_inicial": convertir_a_numero(
            campos_entrada["velocidad_inicial"].get(),
            "Velocidad inicial",
        ),
    }

    validar_rangos_datos(datos_experimento)

    return datos_experimento


def validar_rangos_datos(datos_experimento):
    if datos_experimento["altura_lanzador"] < 0:
        raise ValueError("La altura del lanzador no puede ser negativa.")

    if datos_experimento["altura_mono"] <= 0:
        raise ValueError("La altura inicial del mono debe ser mayor que cero.")

    if datos_experimento["velocidad_inicial"] <= 0:
        raise ValueError("La velocidad inicial debe ser mayor que cero.")

    if datos_experimento["posicion_x_mono"] <= datos_experimento["posicion_x_lanzador"]:
        raise ValueError("El mono debe estar adelante del lanzador.")

    if datos_experimento["altura_mono"] <= datos_experimento["altura_lanzador"]:
        raise ValueError("El mono debe estar más alto que el lanzador.")