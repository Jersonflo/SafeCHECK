"""
ui/views/loading_view.py
=========================
Pantalla de carga animada que se muestra al presionar "Iniciar".

Flujo:
  1. Detecta cámaras disponibles (CameraDetectorWorker en background)
  2. Carga el modelo YOLO (ModelLoaderWorker en background)
  3. Emite loading_complete(camera_indices) cuando todo está listo
"""

from __future__ import annotations

import logging

from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from config import CONFIG
from core.camera_manager import CameraDetectorWorker
from core.model_manager import ModelManager

logger = logging.getLogger(__name__)

# Caracteres del spinner animado
_SPINNER_FRAMES = ("◐", "◓", "◑", "◒")


class _ModelLoaderWorker(QThread):
    """Carga el modelo YOLO en background."""

    load_complete: pyqtSignal = pyqtSignal()
    load_error: pyqtSignal = pyqtSignal(str)

    def run(self) -> None:
        try:
            ModelManager.get_instance().load(CONFIG.MODEL_NAME)
            self.load_complete.emit()
        except Exception as exc:
            self.load_error.emit(str(exc))


class LoadingView(QWidget):
    """
    Vista de carga con spinner y mensajes de progreso.

    Señales:
        loading_complete(list[int]):
            Emitida cuando cámaras y modelo están listos.
            Incluye la lista de índices de cámara disponibles.
        loading_error(str):
            Emitida si ocurre un error crítico durante la carga.
    """

    loading_complete: pyqtSignal = pyqtSignal(list)
    loading_error: pyqtSignal = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._camera_indices: list[int] = []
        self._spinner_index = 0
        self._detector: CameraDetectorWorker | None = None
        self._loader: _ModelLoaderWorker | None = None
        self._build_ui()
        self._spinner_timer = QTimer(self)
        self._spinner_timer.timeout.connect(self._tick_spinner)

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addStretch(2)

        center = QVBoxLayout()
        center.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        center.setSpacing(20)

        # Spinner
        self._spinner_lbl = QLabel(_SPINNER_FRAMES[0])
        self._spinner_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._spinner_lbl.setStyleSheet(
            f"font-size: 56px; color: #FF6100;"
        )

        # Mensaje de estado
        self._status_lbl = QLabel("Iniciando…")
        self._status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_lbl.setStyleSheet(
            "font-size: 18px; color: #F0F6FC; font-weight: 600;"
        )

        # Sub-mensaje
        self._sub_lbl = QLabel("Por favor espera")
        self._sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._sub_lbl.setStyleSheet("font-size: 13px; color: #8B949E;")

        # Barra de progreso (indeterminada)
        self._progress = QProgressBar()
        self._progress.setObjectName("loading-bar")
        self._progress.setRange(0, 0)          # modo indeterminado
        self._progress.setFixedWidth(320)
        self._progress.setFixedHeight(6)
        self._progress.setTextVisible(False)

        center.addWidget(self._spinner_lbl)
        center.addSpacing(8)
        center.addWidget(self._status_lbl)
        center.addWidget(self._sub_lbl)
        center.addSpacing(16)
        center.addWidget(self._progress, alignment=Qt.AlignmentFlag.AlignHCenter)

        root.addLayout(center)
        root.addStretch(3)

    # ── Lógica de carga ───────────────────────────────────────────────────────

    def start_loading(self) -> None:
        """
        Inicia el proceso de carga.
        Llamar cada vez que se muestra esta vista.
        """
        self._camera_indices = []
        self._set_status("Detectando cámaras disponibles…", "Esto puede tomar unos segundos")
        self._spinner_timer.start(120)

        # Paso 1: Detectar cámaras
        self._detector = CameraDetectorWorker(parent=self)
        self._detector.detection_complete.connect(self._on_cameras_detected)
        self._detector.start()

    def _on_cameras_detected(self, indices: list[int]) -> None:
        self._camera_indices = indices
        cam_count = len(indices)
        msg = (
            f"{cam_count} cámara{'s' if cam_count != 1 else ''} encontrada{'s' if cam_count != 1 else ''}"
            if cam_count > 0
            else "Sin cámaras — continuando en modo demo"
        )
        self._set_status("Cargando modelo de detección…", msg)

        # Paso 2: Cargar modelo YOLO
        self._loader = _ModelLoaderWorker(parent=self)
        self._loader.load_complete.connect(self._on_model_loaded)
        self._loader.load_error.connect(self._on_load_error)
        self._loader.start()

    def _on_model_loaded(self) -> None:
        self._set_status("¡Todo listo!", "Iniciando monitoreo…")
        self._progress.setRange(0, 100)
        self._progress.setValue(100)
        self._spinner_lbl.setText("✓")
        self._spinner_lbl.setStyleSheet("font-size: 56px; color: #22C55E;")
        self._spinner_timer.stop()

        # Pequeña pausa visual antes de cambiar de vista
        QTimer.singleShot(900, lambda: self.loading_complete.emit(self._camera_indices))

    def _on_load_error(self, message: str) -> None:
        logger.error("Error al cargar el modelo: %s", message)
        self._spinner_timer.stop()
        self._set_status("Error al cargar el modelo", message)
        self._spinner_lbl.setText("✗")
        self._spinner_lbl.setStyleSheet("font-size: 56px; color: #EF4444;")
        self.loading_error.emit(message)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _set_status(self, main: str, sub: str = "") -> None:
        self._status_lbl.setText(main)
        self._sub_lbl.setText(sub)

    def _tick_spinner(self) -> None:
        self._spinner_index = (self._spinner_index + 1) % len(_SPINNER_FRAMES)
        self._spinner_lbl.setText(_SPINNER_FRAMES[self._spinner_index])
