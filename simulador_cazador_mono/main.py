import ctypes
import tkinter as tk

from interfaz import InterfazExperimento


def configurar_nitidez_windows():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def iniciar_aplicacion():
    configurar_nitidez_windows()

    ventana_principal = tk.Tk()
    InterfazExperimento(ventana_principal)
    ventana_principal.mainloop()


if __name__ == "__main__":
    iniciar_aplicacion()