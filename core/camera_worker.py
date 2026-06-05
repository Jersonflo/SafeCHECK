"""
core/camera_worker.py
======================
QThread dedicado por cámara.

Cada CameraWorker:
  1. Abre la cámara por índice (cv2.VideoCapture)
  2. Lee frames en un bucle controlado por FPS
  3. Ejecuta inferencia YOLO (via ModelManager)
  4. Emite la señal `frame_ready` con el frame anotado y las detecciones
  5. Se detiene limpiamente con stop()
"""

from __future__ import annotations

import logging
import threading
import time

import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal

from config import CONFIG
from core.model_manager import Detection, ModelManager

logger = logging.getLogger(__name__)


class FrameGrabber(threading.Thread):
    """
    Hilo daemon que lee continuamente fotogramas de la cámara
    para evitar la acumulación de búfer en OpenCV.
    """

    def __init__(self, cap: cv2.VideoCapture) -> None:
        super().__init__()
        self.cap = cap
        self.ret = False
        self.frame = None
        self.stopped = False
        self.lock = threading.Lock()
        self.daemon = True

    def run(self) -> None:
        while not self.stopped:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.01)
                continue
            with self.lock:
                self.ret = ret
                self.frame = frame
            time.sleep(0.005)  # Evita saturar la CPU

    def get_latest_frame(self) -> tuple[bool, np.ndarray | None]:
        with self.lock:
            if self.ret and self.frame is not None:
                return True, self.frame.copy()
            return False, None

    def stop(self) -> None:
        self.stopped = True


class CameraWorker(QThread):
    """
    Thread de captura y detección para una cámara individual.

    Señales:
        frame_ready(int, np.ndarray, list[Detection]):
            Emitida cada vez que hay un frame procesado.
            Argumentos: (camera_index, annotated_frame_BGR, detections)
        camera_error(int, str):
            Emitida si la cámara falla o no puede abrirse.
    """

    frame_ready: pyqtSignal = pyqtSignal(int, object, list)
    camera_error: pyqtSignal = pyqtSignal(int, str)

    def __init__(self, camera_index: int, parent=None) -> None:
        super().__init__(parent)
        self._camera_index = camera_index
        self._stop_requested = False
        self._model = ModelManager.get_instance()
        self._frame_interval = 1.0 / CONFIG.CAMERA_FPS_LIMIT
        self._grabber = None

    @property
    def camera_index(self) -> int:
        return self._camera_index

    def run(self) -> None:
        """Bucle principal del thread: captura → inferencia (skip) → emit."""
        cap = cv2.VideoCapture(self._camera_index)

        if not cap.isOpened():
            logger.warning("No se pudo abrir la cámara %d", self._camera_index)
            self.camera_error.emit(
                self._camera_index,
                f"No se pudo abrir la cámara {self._camera_index}",
            )
            return

        # Configurar resolución y búfer para reducir carga de CPU y lag
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, CONFIG.CAMERA_FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CONFIG.CAMERA_FRAME_HEIGHT)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        # Iniciar grabber continuo en background
        self._grabber = FrameGrabber(cap)
        self._grabber.start()

        logger.info("Cámara %d iniciada con FrameGrabber.", self._camera_index)

        skip_n = max(1, CONFIG.INFERENCE_SKIP_FRAMES)
        frame_count = 0
        last_detections: list[Detection] = []

        try:
            while not self._stop_requested:
                start_time = time.monotonic()

                ret, frame = self._grabber.get_latest_frame()
                if not ret or frame is None:
                    time.sleep(0.01)
                    continue

                frame_count += 1

                if frame_count % skip_n == 0:
                    # Frame de inferencia: correr YOLO
                    annotated, detections = self._model.predict(
                        frame,
                        confidence=CONFIG.DETECTION_CONFIDENCE,
                        imgsz=CONFIG.MODEL_IMGSZ,
                    )
                    last_detections = detections
                    self.frame_ready.emit(self._camera_index, annotated, last_detections)
                else:
                    # Frame intermedio: emitir video crudo + últimas detecciones
                    self.frame_ready.emit(self._camera_index, frame, last_detections)

                # Limitar FPS: dormir el tiempo restante del intervalo
                elapsed = time.monotonic() - start_time
                sleep_time = self._frame_interval - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)

        except Exception as exc:
            logger.exception("Error inesperado en cámara %d: %s", self._camera_index, exc)
            self.camera_error.emit(self._camera_index, str(exc))
        finally:
            if self._grabber is not None:
                self._grabber.stop()
                self._grabber.join(timeout=1.0)
            cap.release()
            logger.info("Cámara %d liberada.", self._camera_index)

    def stop(self) -> None:
        """Solicita detención limpia del thread."""
        self._stop_requested = True
        if self._grabber is not None:
            self._grabber.stop()
        self.wait(3000)  # espera hasta 3s para que termine limpiamente
