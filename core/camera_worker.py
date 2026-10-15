"""
core/camera_worker.py
======================
QThread dedicado por cámara.

Cada CameraWorker:
  1. Abre la cámara por índice (cv2.VideoCapture)
  2. FrameGrabber lee frames continuamente (sin acumular búfer)
  3. InferenceThread corre YOLO sobre el frame más reciente, a su propio ritmo
  4. El bucle principal emite `frame_ready` a la velocidad de la cámara,
     dibujando sobre el video en vivo las últimas detecciones disponibles.
     Así el video no se congela mientras el modelo procesa (en CPU tarda
     ~150–300 ms por frame).
  5. Se detiene limpiamente con stop()
"""

from __future__ import annotations

import logging
import sys
import threading
import time

import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal

from config import CONFIG
from core.model_manager import Detection, ModelManager

logger = logging.getLogger(__name__)

def open_camera(index: int) -> cv2.VideoCapture:
    """Abre una cámara por índice. En Windows usa DirectShow, que abre mucho más rápido que MSMF."""
    if sys.platform == "win32":
        return cv2.VideoCapture(index, cv2.CAP_DSHOW)
    return cv2.VideoCapture(index)


# Colores BGR de los recuadros (coinciden con la paleta de la UI)
_COLOR_DANGER = (68, 68, 239)
_COLOR_SAFE = (94, 197, 34)
_COLOR_NEUTRAL = (158, 148, 139)


def _draw_detections(frame: np.ndarray, detections: list[Detection]) -> np.ndarray:
    """Dibuja recuadros y etiquetas de las detecciones sobre el frame (in-place)."""
    for det in detections:
        if det.is_violation:
            color = _COLOR_DANGER
        elif det.has_helmet:
            color = _COLOR_SAFE
        else:
            color = _COLOR_NEUTRAL
        x1, y1, x2, y2 = det.bbox
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        label = f"{det.class_name} {det.confidence:.2f}"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        ty = max(y1, th + 6)
        cv2.rectangle(frame, (x1, ty - th - 6), (x1 + tw + 6, ty), color, -1)
        cv2.putText(
            frame, label, (x1 + 3, ty - 4),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA,
        )
    return frame


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


class InferenceThread(threading.Thread):
    """
    Hilo daemon que corre YOLO continuamente sobre el frame más reciente
    del FrameGrabber y guarda las últimas detecciones.
    """

    def __init__(self, grabber: FrameGrabber, model: ModelManager) -> None:
        super().__init__()
        self.grabber = grabber
        self.model = model
        self.detections: list[Detection] = []
        self.stopped = False
        self.lock = threading.Lock()
        self.daemon = True

    def run(self) -> None:
        skip_n = max(1, CONFIG.INFERENCE_SKIP_FRAMES)
        count = 0
        while not self.stopped:
            ret, frame = self.grabber.get_latest_frame()
            if not ret or frame is None:
                time.sleep(0.01)
                continue
            count += 1
            if count % skip_n != 0:
                time.sleep(0.03)
                continue
            detections = self.model.detect(
                frame,
                confidence=CONFIG.DETECTION_CONFIDENCE,
                imgsz=CONFIG.MODEL_IMGSZ,
            )
            with self.lock:
                self.detections = detections

    def get_detections(self) -> list[Detection]:
        with self.lock:
            return list(self.detections)

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
        self._inference = None

    @property
    def camera_index(self) -> int:
        return self._camera_index

    def run(self) -> None:
        """Bucle principal del thread: frame en vivo + últimas detecciones → emit."""
        cap = open_camera(self._camera_index)

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

        # Inferencia en paralelo: el video no espera al modelo
        self._inference = InferenceThread(self._grabber, self._model)
        self._inference.start()

        logger.info("Cámara %d iniciada con FrameGrabber + InferenceThread.", self._camera_index)

        try:
            while not self._stop_requested:
                start_time = time.monotonic()

                ret, frame = self._grabber.get_latest_frame()
                if not ret or frame is None:
                    time.sleep(0.01)
                    continue

                detections = self._inference.get_detections()
                annotated = _draw_detections(frame, detections)
                self.frame_ready.emit(self._camera_index, annotated, detections)

                # Limitar FPS: dormir el tiempo restante del intervalo
                elapsed = time.monotonic() - start_time
                sleep_time = self._frame_interval - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)

        except Exception as exc:
            logger.exception("Error inesperado en cámara %d: %s", self._camera_index, exc)
            self.camera_error.emit(self._camera_index, str(exc))
        finally:
            if self._inference is not None:
                self._inference.stop()
                self._inference.join(timeout=2.0)
            if self._grabber is not None:
                self._grabber.stop()
                self._grabber.join(timeout=1.0)
            cap.release()
            logger.info("Cámara %d liberada.", self._camera_index)

    def stop(self) -> None:
        """Solicita detención limpia del thread."""
        self._stop_requested = True
        if self._inference is not None:
            self._inference.stop()
        if self._grabber is not None:
            self._grabber.stop()
        self.wait(3000)  # espera hasta 3s para que termine limpiamente
