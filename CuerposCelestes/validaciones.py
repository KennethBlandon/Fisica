"""Funciones de validacion de datos ingresados por el usuario."""


def leer_float(texto: str, nombre_campo: str) -> tuple[bool, str, float | None]:
    limpio = texto.strip().replace(",", ".")
    if not limpio:
        return False, f"El campo '{nombre_campo}' no puede estar vacio.", None

    try:
        valor = float(limpio)
    except ValueError:
        return False, f"El campo '{nombre_campo}' debe ser numerico.", None

    return True, "", valor


def validar_masa(texto: str) -> tuple[bool, str, float | None]:
    ok, msg, valor = leer_float(texto, "Masa")
    if not ok:
        return ok, msg, valor

    if valor is None or valor <= 0:
        return False, "La masa debe ser mayor que cero.", None

    return True, "", valor
