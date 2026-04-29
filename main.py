"""
main.py
───────
Punto de entrada del programa.
Ejecutar:
    python main.py

Dependencias opcionales (para la gráfica):
    pip install -r requirements.txt
"""

from pathlib import Path
import sys
import tkinter as tk


def _agregar_site_packages_venv():
    """Hace visible .venv/Lib/site-packages cuando existe en el proyecto."""
    base = Path(__file__).resolve().parent
    site_packages = base / ".venv" / "Lib" / "site-packages"
    if site_packages.is_dir():
        sys.path.insert(0, str(site_packages))


_agregar_site_packages_venv()

from superposicion import Constantes
 
 
def main():
    """Muestra pantalla inicial fullscreen con dos botones.

    "Abrir aplicación" instancia `Aplicacion` dentro de la misma ventana
    manteniendo el modo fullscreen y sin posibilidad de redimensionar.
    """
    C = Constantes
    root = tk.Tk()

    # Abrir siempre fullscreen y bloquear redimensionado
    root.attributes("-fullscreen", True)
    root.resizable(False, False)
    root.configure(bg=C.DARK_BG)

    # Pantalla de inicio
    inicio = tk.Frame(root, bg=C.DARK_BG)
    inicio.pack(fill="both", expand=True)

    cont = tk.Frame(inicio, bg=C.DARK_BG)
    cont.place(relx=0.5, rely=0.5, anchor="center")

    btn_font = ("Courier New", 28, "bold")

    def _start_app():
        # Destruye la pantalla de inicio y crea la interfaz principal
        inicio.destroy()
        from superposicion import Aplicacion
        Aplicacion(root)

    tk.Button(
        cont, text="Principio de Superposición",
        font=btn_font, fg=C.DARK_BG, bg=C.ACCENT,
        activebackground="#388bfd", relief="flat", bd=0,
        padx=40, pady=20, cursor="hand2",
        command=_start_app
    ).pack(pady=(0, 18), fill="x")
    
    def _open_circuito():
        # Destruye la pantalla de inicio y abre la ampliación de circuitos
        inicio.destroy()
        from Circuito import AplicacionCircuito
        AplicacionCircuito(root)

    tk.Button(
        cont, text="Circuito Serie o Paralelo",
        font=("Courier New", 20), fg=C.DARK_BG, bg=C.ACCENT2,
        activebackground="#2ea043", relief="flat", bd=0,
        padx=20, pady=14, cursor="hand2",
        command=_open_circuito
    ).pack(pady=(0, 18), fill="x")
    

    tk.Button(
        cont, text="Salir",
        font=("Courier New", 18), fg=C.TEXT_PRIMARY, bg=C.INPUT_BG,
        activebackground=C.BORDER, relief="flat", bd=0,
        padx=30, pady=12, cursor="hand2",
        command=root.destroy
    ).pack(fill="x")

    # Tecla Escape también cierra la aplicación desde la pantalla de inicio
    root.bind('<Escape>', lambda e: root.destroy())

    root.mainloop()
 
 
if __name__ == "__main__":
    main()
 