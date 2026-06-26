"""Control simple del bucle de animacion con tkinter."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable


class MotorAnimacion:
    def __init__(self, root: tk.Tk, callback: Callable[[], None], fps: int = 60) -> None:
        self.root = root
        self.callback = callback
        self.intervalo_ms = max(1, int(1000 / max(1, fps)))
        self._after_id: str | None = None
        self.en_ejecucion = False

    def iniciar(self) -> None:
        if self.en_ejecucion:
            return
        self.en_ejecucion = True
        self._bucle()

    def pausar(self) -> None:
        self.en_ejecucion = False
        if self._after_id is not None:
            self.root.after_cancel(self._after_id)
            self._after_id = None

    def _bucle(self) -> None:
        if not self.en_ejecucion:
            return
        self.callback()
        self._after_id = self.root.after(self.intervalo_ms, self._bucle)
