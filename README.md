# Simulador de Movimiento Parabolico

Programa en Python con interfaz grafica para simular el movimiento parabolico y la caida libre de un segundo objeto a partir de datos ingresados por el usuario.

## Requisitos

- Python 3.10 o superior
- Tkinter disponible en la instalacion de Python

## Ejecucion

```powershell
python simulador_movimiento_parabolico.py
```

## Funcionalidades

- Entrada de velocidad inicial, angulo, altura inicial y gravedad
- Entrada de posicion horizontal, altura y retraso para un segundo objeto en caida libre
- Calculo de tiempo de vuelo, altura maxima y alcance horizontal
- Verificacion de si el proyectil intercepta al objeto al llegar a su posicion horizontal
- Grafica conjunta de la trayectoria del proyectil y la caida del segundo objeto
- Ventana de resultados separada, abierta con el boton `Ver resultados`, para dejar mas espacio al mapa
- Animacion cuadro a cuadro del proyectil y del objeto en caida
- Tabla con tiempo, posicion y velocidad vertical de ambos objetos
- Calculo automatico de la altura necesaria o del retraso necesario para forzar la intercepcion
- Exploracion del mapa con zoom usando la rueda del mouse y desplazamiento arrastrando con clic izquierdo
- Modo `cazador y mono`, con angulo de disparo fijado automaticamente hacia la posicion inicial del objeto suspendido
- En ese modo, la posicion del mono se reajusta automaticamente cuando cambia la velocidad inicial
- Validacion basica de entradas

## Estructura

- `simulador_movimiento_parabolico.py`: interfaz principal y control de la aplicacion
- `physics.py`: funciones de fisica, calculos derivados y teoria del experimento cazador y mono

## Uso rapido

- Presiona `Simular` para recalcular toda la escena.
- Presiona `Ver resultados` para abrir el resumen y la tabla en una ventana aparte.
- Presiona `Animar` para reproducir el movimiento sobre la grafica.
- Presiona `Calcular altura para interceptar` para ajustar automaticamente la altura inicial del objeto en caida.
- Presiona `Calcular retraso para interceptar` para ajustar automaticamente el instante en que debe empezar a caer.
- Usa la rueda del mouse para acercar o alejar y arrastra el mapa con clic izquierdo para recorrerlo.
- Activa `Modo cazador y mono` o usa `Ejemplo cazador y mono` para fijar el angulo hacia el objeto suspendido y forzar la caida simultanea.