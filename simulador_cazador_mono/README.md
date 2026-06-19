# Simulador del experimento del cazador y el mono

Aplicación de escritorio en Python (Tkinter) que recrea el experimento clásico donde un proyectil se dispara apuntando a un mono suspendido que comienza a caer al mismo tiempo.

El programa permite:
- Ingresar parámetros físicos del experimento.
- Calcular ángulo de puntería automáticamente.
- Simular la trayectoria del proyectil y la caída del mono.
- Mostrar resultados numéricos del choque (o no choque en el aire).
- Animar el movimiento cuadro a cuadro con seguimiento vertical cuando los objetos salen por debajo del área visible.

## 1. Objetivo del proyecto

Este simulador está orientado a aprendizaje de cinemática y movimiento parabólico bajo gravedad constante. Busca mostrar visual y numéricamente por qué, en condiciones ideales, apuntar al objetivo inicial puede producir intersección con un objetivo que cae.

## 2. Modelo físico implementado

Suposiciones del modelo:
- Gravedad constante: $g = 9.81\,m/s^2$.
- Sin resistencia del aire.
- Movimiento en 2D.
- El proyectil sale con velocidad inicial constante.
- El mono inicia caída libre en $t = 0$.

Ecuaciones usadas:

- Ángulo de puntería hacia la posición inicial del mono:
  $\theta = \operatorname{atan2}(y_m - y_l,\ x_m - x_l)$

- Componentes de velocidad del proyectil:
  $v_x = v_0\cos\theta$, $v_y = v_0\sin\theta$

- Posición del proyectil en el tiempo:
  $x_p(t)=x_l+v_xt$

  $y_p(t)=y_l+v_yt-\frac{1}{2}gt^2$

- Posición del mono en el tiempo:
  $x_m(t)=x_m$

  $y_m(t)=y_{m0}-\frac{1}{2}gt^2$

- Tiempo usado por la simulación para evaluar choque:
  $t_{choque}=\frac{d}{v_0}$

  con $d=\sqrt{(x_m-x_l)^2+(y_{m0}-y_l)^2}$

Criterio de estado:
- Chocan en el aire si la altura calculada de choque es positiva y ocurre antes de que el mono llegue al suelo.

## 3. Estructura del proyecto

- main.py
  - Punto de entrada.
  - Configura nitidez DPI en Windows.
  - Crea ventana principal y arranca el bucle de Tkinter.

- interfaz.py
  - Construye toda la UI (panel de entradas, canvas de visualización y tarjetas de resultados).
  - Ejecuta simulación y animación.
  - Convierte coordenadas físicas a coordenadas de canvas.
  - Incluye seguimiento vertical de cámara durante la animación.

- logica_experimento.py
  - Cálculo físico del ángulo, tiempo, punto de choque y trayectorias discretizadas.

- validaciones.py
  - Lectura, conversión numérica y validación de rangos de entrada.

- animacion.py
  - Control de frames con after de Tkinter.

- estilos.py
  - Paleta de colores y tipografías.

## 4. Requisitos

- Python 3.10 o superior (recomendado 3.11+).
- Tkinter disponible (en Windows normalmente ya viene incluido con Python).

No requiere dependencias externas.

## 5. Ejecución

Desde la carpeta del proyecto:

1. Abrir terminal en la raíz que contiene la carpeta simulador_cazador_mono.
2. Ejecutar:

   python simulador_cazador_mono/main.py

Si estás ya dentro de simulador_cazador_mono:

   python main.py

## 6. Uso de la interfaz

1. Completa los campos:
   - X del lanzador (m)
   - Altura del lanzador (m)
   - X del mono (m)
   - Altura inicial del mono (m)
   - Velocidad inicial (m/s)
2. Pulsa Simular.
3. Observa:
   - Trayectoria del proyectil.
   - Caída del mono.
   - Punto de choque calculado.
   - Estado final.
4. Pulsa Reiniciar para limpiar el estado.

## 7. Validaciones implementadas

El programa muestra error si:
- Un campo está vacío.
- Un campo no es numérico.
- Altura del lanzador es negativa.
- Altura inicial del mono es menor o igual a cero.
- Velocidad inicial es menor o igual a cero.
- El mono no está por delante del lanzador en X.
- El mono no está por encima del lanzador.

## 8. Resultados mostrados

En la parte inferior se muestran:
- Ángulo de disparo en grados.
- Tiempo de choque estimado.
- Punto de choque $(x,y)$ en metros.
- Estado textual: Chocan en el aire o No chocan en el aire.

## 9. Detalles de visualización y animación

- La escena se dibuja en un Canvas con cuadrícula y suelo.
- La trayectoria se discretiza en puntos y se anima por frames.
- El controlador de animación usa una cadencia temporal fija (velocidad_ms).
- La transformación de coordenadas aplica escalado horizontal y vertical.
- Durante la animación, si proyectil o mono quedan por debajo de la región visible, la vista se desplaza verticalmente para seguirlos.

