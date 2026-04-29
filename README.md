# Programa Física

Aplicación de escritorio en Tkinter para resolver un ejercicio de superposición de cargas y una ampliación de circuitos simples.

## Qué incluye

- Pantalla de inicio en modo pantalla completa.
- Botón principal para abrir la app de superposición.
- Botón adicional para "Circuito Serie o Paralelo".
- Interfaz principal para ingresar cargas, calcular fuerzas y ver una gráfica.
- Módulo modular `Circuito/` para resolver resistores y capacitores en serie o paralelo.

## Requisitos

- Python 3.
- `matplotlib` y `numpy` para mostrar la visualización.
- `openpyxl` para leer archivos Excel en la ampliación de circuitos.

Instalación recomendada:

```bash
pip install -r requirements.txt
```

## Cómo ejecutar

```bash
python main.py
```

## Estructura importante

- `main.py`: punto de entrada y pantalla inicial.
- `superposicion/appSuperposicion.py`: ventana principal de la simulación.
- `superposicion/fisicaSuperposicion.py`: cálculos físicos.
- `superposicion/paneles.py`: paneles de interfaz y gráfica.
- `superposicion/widgets.py`: widgets reutilizables.
- `constantes.py`: colores, fuentes y constante de Coulomb compartidos.
- `pantalla_base.py`: base reutilizable para pantallas Tkinter.
- `Circuito/appCircuito.py`: pantalla para la ampliación de circuitos.
- `Circuito/calculos.py`: lógica matemática de resistores y capacitores.
- `Circuito/importadores.py`: lectura desde texto, CSV o Excel.

## Nota técnica

`main.py` intenta cargar `matplotlib` y `numpy` desde `.venv/Lib/site-packages` si existe esa carpeta dentro del proyecto. Eso evita depender del Python global cuando la app se ejecuta con otro intérprete.

El paquete `Circuito/` está separado para que la lógica de esta ampliación quede aislada y sea fácil de mantener o reutilizar en otras pantallas.
