# Simulador de Cuerpos Celestes 2D

Simulador interactivo en Python que aplica la Ley de Gravitacion Universal y la Segunda Ley de Newton para animar cuerpos en un plano 2D.

## Caracteristicas

- Agregar cuerpos con:
  - masa
  - posicion inicial `(x, y)`
  - velocidad inicial `(vx, vy)`
  - color
- Simulacion gravitacional N-cuerpos (interacciones mutuas)
- Animacion en tiempo real con trayectorias
- Vista centrada en el centro de masa para apreciar la reaccion entre cuerpos
- Ejemplo incluido: Sol-Tierra-Luna
- Control de paso temporal (`dt`) y subpasos por frame
- Opcion de gravedad con retardo (`t-r/c`) configurable
- Mapa interactivo con zoom y desplazamiento libre

## Estructura

- `main.py`: punto de entrada
- `interfaz.py`: interfaz grafica (Tkinter)
- `logica_experimento.py`: motor fisico de simulacion
- `animacion.py`: bucle de animacion
- `validaciones.py`: validacion de entradas
- `estilos.py`: paleta visual y fuentes

## Requisitos

- Python 3.10+
- No requiere librerias externas (solo biblioteca estandar)

## Ejecucion

Desde la carpeta del proyecto:

```bash
python main.py
```

## Base fisica implementada

Para cada par de cuerpos se calcula la fuerza gravitacional:

- `F = G * m1 * m2 / r^2`

La aceleracion se obtiene de:

- `a = F / m`

Integracion numerica usada en cada paso:

- Integrador Velocity-Verlet:
  - `r(t + dt) = r(t) + v(t)dt + 0.5a(t)dt^2`
  - `v(t + dt) = v(t) + 0.5(a(t) + a(t + dt))dt`

Se aplica un pequeno suavizado numerico para evitar inestabilidades cuando la distancia entre cuerpos es muy pequena.

## Gravedad con retardo (opcional)

En la interfaz puedes activar `Gravedad con retardo (t-r/c)` y definir `Velocidad gravedad (m/s)`.

Cuando esta opcion esta activa, cada cuerpo calcula la fuerza usando la posicion pasada de los demas segun:

- `t_retrasado = t_actual - r/c`

con interpolacion lineal del historial de posiciones.

Nota: este modelo es una aproximacion newtoniana retardada util para exploracion numerica. No reemplaza un modelo relativista completo.

## Navegacion del mapa

- Rueda del mouse: zoom centrado en el cursor.
- Arrastre con click izquierdo: mover libremente la camara por el plano.
- Boton `Autoajustar vista`: volver al encuadre automatico.

El zoom maximo esta limitado a `1 px = 1 m` para permitir acercamientos muy altos manteniendo estabilidad visual.
