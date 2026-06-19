class ControlAnimacion:
    def __init__(self, ventana_principal, velocidad_ms=25):
        self.ventana_principal = ventana_principal
        self.velocidad_ms = velocidad_ms
        self.indice_actual = 0
        self.total_frames = 0
        self.tarea_programada = None
        self.funcion_dibujar_frame = None

    def iniciar(self, total_frames, funcion_dibujar_frame):
        self.detener()

        self.indice_actual = 0
        self.total_frames = total_frames
        self.funcion_dibujar_frame = funcion_dibujar_frame

        self.avanzar()

    def avanzar(self):
        if self.funcion_dibujar_frame is None:
            return

        self.funcion_dibujar_frame(self.indice_actual)

        if self.indice_actual < self.total_frames - 1:
            self.indice_actual += 1
            self.tarea_programada = self.ventana_principal.after(
                self.velocidad_ms,
                self.avanzar,
            )
        else:
            self.tarea_programada = None

    def detener(self):
        if self.tarea_programada is not None:
            try:
                self.ventana_principal.after_cancel(self.tarea_programada)
            except Exception:
                pass

        self.tarea_programada = None

    def reiniciar_indice(self):
        self.indice_actual = 0