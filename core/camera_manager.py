"""
core/camera_manager.py
=======================
Detecta cámaras disponibles en background (sin bloquear la UI)
y gestiona el ciclo de vida de los CameraWorker threads.
"""

from __future__ import annotations

import logging

import cv2
from PyQt6.QtCore import QThread, pyqtSignal

from config import CONFIG
from core.camera_worker import CameraWorker

logger = logging.getLogger(__name__)


class CameraDetectorWorker(QThread):
    """
    QThread que prueba índices de cámara de 0 a MAX_CAMERAS-1
    y emite la lista de los que están disponibles.

    Señales:
        detection_complete(list[int]):
            Emitida al terminar la detección con la lista de índices disponibles.
    """

    detection_complete: pyqtSignal = pyqtSignal(list)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

    def run(self) -> None:
        available: list[int] = []
        for index in range(CONFIG.MAX_CAMERAS):
            cap = cv2.VideoCapture(index)
            if cap.isOpened():
                logger.info("Cámara disponible en índice %d", index)
                available.append(index)
                cap.release()
            else:
                logger.debug("Sin cámara en índice %d", index)

        logger.info("Detección completada. Cámaras: %s", available)
        self.detection_complete.emit(available)


class CameraManager:
    """
    Gestiona el ciclo de vida de todos los CameraWorker activos.

    Uso:
        manager = CameraManager()
        manager.start_cameras(indices)   # inicia los workers
        manager.stop_all()               # detiene y libera todo
    """

    def __init__(self) -> None:
        self._workers: dict[int, CameraWorker] = {}

    def start_cameras(
        self,
        indices: list[int],
        frame_callback,
        error_callback,
    ) -> None:
        """
        Inicia un CameraWorker por cada índice proporcionado.

        Args:
            indices: Lista de índices de cámara disponibles.
            frame_callback: Callable(camera_index, frame, detections) para frames listos.
            error_callback: Callable(camera_index, message) para errores.
        """
        self.stop_all()  # asegurarse de limpiar workers anteriores

        for idx in indices:
            worker = CameraWorker(camera_index=idx)
            worker.frame_ready.connect(frame_callback)
            worker.camera_error.connect(error_callback)
            worker.start()
            self._workers[idx] = worker
            logger.info("Worker iniciado para cámara %d", idx)

    def stop_all(self) -> None:
        """Detiene y libera todos los workers activos."""
        for idx, worker in self._workers.items():
            logger.info("Deteniendo worker cámara %d...", idx)
            worker.stop()
        self._workers.clear()
        logger.info("Todos los workers detenidos.")

    @property
    def active_count(self) -> int:
        """Número de workers actualmente activos."""
        return len(self._workers)
