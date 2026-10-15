"""
ui/views/camera_view.py
========================
Vista principal de monitoreo: grilla dinámica de cámaras con detección YOLO.

• Recibe la lista de índices de cámara desde LoadingView
• Construye un QGridLayout dinámico (filas/columnas según cantidad de cámaras)
• Cada celda (CameraCell) muestra:
    - Video en tiempo real (anotado por YOLO)
    - Badge de estado: ✓ CASCO | ✗ SIN CASCO | Sin detecciones
    - El borde del card cambia de color según el estado
• Botón "Detener" libera todos los recursos limpiamente
"""

from __future__ import annotations

import logging
import math

import cv2
import numpy as np
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.camera_manager import CameraManager
from core.model_manager import Detection

logger = logging.getLogger(__name__)


# ─── Constantes de estado ────────────────────────────────────────────────────
_STATUS_SAFE = ("✓  CON CASCO", "badge-safe", "camera-cell-safe")
_STATUS_DANGER = ("✗  SIN CASCO", "badge-danger", "camera-cell-danger")
_STATUS_NEUTRAL = ("○  Sin detecciones", "badge-neutral", "camera-cell")


def _ndarray_to_pixmap(frame_bgr: np.ndarray) -> QPixmap:
    """Convierte un frame BGR de OpenCV a QPixmap (thread-safe, solo llamar en hilo UI)."""
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    h, w, ch = frame_rgb.shape
    qt_img = QImage(frame_rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
    return QPixmap.fromImage(qt_img)


def _classify_detections(detections: list[Detection]) -> tuple[str, str, str]:
    """
    Determina el estado de la cámara según las detecciones.

    Returns:
        Tupla (texto_badge, objectName_badge, objectName_card)
    """
    if not detections:
        return _STATUS_NEUTRAL

    has_violation = any(d.is_violation for d in detections)
    has_safe = any(d.has_helmet for d in detections)

    if has_violation:
        return _STATUS_DANGER
    if has_safe:
        return _STATUS_SAFE
    return _STATUS_NEUTRAL


# ─── Widget de celda individual ───────────────────────────────────────────────

class CameraCell(QFrame):
    """
    Widget que representa una cámara en la grilla.

    Muestra el video y el badge de detección.
    Se actualiza via el slot update_frame().
    """

    def __init__(self, camera_index: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._camera_index = camera_index
        self.setObjectName("camera-cell")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(320, 240)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        # Título de la cámara
        self._title_lbl = QLabel(f"  📷  Cámara {self._camera_index + 1}")
        self._title_lbl.setObjectName("camera-title")
        self._title_lbl.setFixedHeight(24)

        # Frame de video
        self._video_lbl = QLabel()
        self._video_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._video_lbl.setStyleSheet(
            "background-color: #0D1117; border-radius: 6px; color: #8B949E; font-size: 13px;"
        )
        self._video_lbl.setText("Esperando señal…")
        self._video_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Badge de estado
        self._badge_lbl = QLabel("○  Inicializando…")
        self._badge_lbl.setObjectName("badge-neutral")
        self._badge_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._badge_lbl.setFixedHeight(28)

        layout.addWidget(self._title_lbl)
        layout.addWidget(self._video_lbl, stretch=1)
        layout.addWidget(self._badge_lbl)

    @pyqtSlot(int, object, list)
    def update_frame(
        self,
        camera_index: int,
        frame: np.ndarray,
        detections: list[Detection],
    ) -> None:
        """
        Actualiza el video y el badge de detección.
        Conectar directamente a CameraWorker.frame_ready.
        """
        if camera_index != self._camera_index:
            return

        # Actualizar video
        pixmap = _ndarray_to_pixmap(frame)
        scaled = pixmap.scaled(
            self._video_lbl.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._video_lbl.setPixmap(scaled)

        # Actualizar badge y borde
        badge_text, badge_name, card_name = _classify_detections(detections)
        self._badge_lbl.setText(badge_text)
        self._badge_lbl.setObjectName(badge_name)
        self._badge_lbl.style().unpolish(self._badge_lbl)
        self._badge_lbl.style().polish(self._badge_lbl)

        self.setObjectName(card_name)
        self.style().unpolish(self)
        self.style().polish(self)

    def show_error(self, message: str) -> None:
        """Muestra un mensaje de error en la celda."""
        self._video_lbl.setText(f"⚠  Error\n{message}")
        self._badge_lbl.setText("✗  Sin señal")
        self._badge_lbl.setObjectName("badge-danger")


# ─── Vista principal de cámaras ───────────────────────────────────────────────

class CameraView(QWidget):
    """
    Vista de monitoreo en tiempo real.

    Señales:
        go_home: Usuario presionó 'Detener / Volver al menú'.
    """

    go_home: pyqtSignal = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._manager = CameraManager()
        self._cells: dict[int, CameraCell] = {}
        self._build_ui()

    # ── Construcción de UI ────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        header = QFrame()
        header.setObjectName("toolbar")
        header.setFixedHeight(52)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        title = QLabel("📡  Monitoreo en Vivo")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #F0F6FC;")

        self._cam_count_lbl = QLabel("")
        self._cam_count_lbl.setObjectName("version-label")

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self._cam_count_lbl)

        root.addWidget(header)

        # Scroll area para la grilla
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        self._grid_container = QWidget()
        self._grid_layout = QGridLayout(self._grid_container)
        self._grid_layout.setContentsMargins(16, 16, 16, 16)
        self._grid_layout.setSpacing(12)

        # Placeholder (se reemplaza al iniciar)
        self._placeholder = QLabel("Las cámaras aparecerán aquí")
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._placeholder.setStyleSheet("color: #8B949E; font-size: 16px;")
        self._grid_layout.addWidget(self._placeholder, 0, 0)

        scroll.setWidget(self._grid_container)
        root.addWidget(scroll, stretch=1)

        # Toolbar inferior
        toolbar = QFrame()
        toolbar.setObjectName("toolbar")
        toolbar.setFixedHeight(60)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(20, 0, 20, 0)

        self._status_lbl = QLabel("▶  Monitoreo activo")
        self._status_lbl.setStyleSheet("color: #22C55E; font-size: 13px; font-weight: bold;")

        stop_btn = QPushButton("⏹  Detener y volver al menú")
        stop_btn.setObjectName("btn-danger")
        stop_btn.setMinimumHeight(40)
        stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        stop_btn.clicked.connect(self._stop_and_go_home)

        toolbar_layout.addWidget(self._status_lbl)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(stop_btn)

        root.addWidget(toolbar)

    # ── Control de cámaras ───────────────────────────────────────────────────

    def start_cameras(self, camera_indices: list[int]) -> None:
        """
        Inicializa la grilla y arranca los workers.
        Llamar cuando el modelo y las cámaras están listos.
        """
        self._clear_grid()
        self._cells.clear()

        if not camera_indices:
            self._show_no_cameras()
            return

        n = len(camera_indices)
        cols = math.ceil(math.sqrt(n))
        rows = math.ceil(n / cols)

        self._cam_count_lbl.setText(
            f"{n} cámara{'s' if n != 1 else ''} activa{'s' if n != 1 else ''}"
        )

        for pos, idx in enumerate(camera_indices):
            row, col = divmod(pos, cols)
            cell = CameraCell(camera_index=idx)
            self._grid_layout.addWidget(cell, row, col)
            self._grid_layout.setRowStretch(row, 1)
            self._grid_layout.setColumnStretch(col, 1)
            self._cells[idx] = cell

        # Arrancar CameraManager con callbacks conectados a las celdas
        self._manager.start_cameras(
            indices=camera_indices,
            frame_callback=self._on_frame_ready,
            error_callback=self._on_camera_error,
        )
        self._status_lbl.setText("▶  Monitoreo activo")
        self._status_lbl.setStyleSheet("color: #22C55E; font-size: 13px; font-weight: bold;")

    @pyqtSlot(int, object, list)
    def _on_frame_ready(
        self,
        camera_index: int,
        frame: np.ndarray,
        detections: list[Detection],
    ) -> None:
        if camera_index in self._cells:
            self._cells[camera_index].update_frame(camera_index, frame, detections)

    @pyqtSlot(int, str)
    def _on_camera_error(self, camera_index: int, message: str) -> None:
        if camera_index in self._cells:
            self._cells[camera_index].show_error(message)

    def _stop_and_go_home(self) -> None:
        self._status_lbl.setText("◼  Deteniendo…")
        self._status_lbl.setStyleSheet("color: #F59E0B; font-size: 13px; font-weight: bold;")
        self.stop_cameras()
        self.go_home.emit()

    def stop_cameras(self) -> None:
        """Detiene todos los workers y libera las cámaras."""
        self._manager.stop_all()

    def _clear_grid(self) -> None:
        """Elimina todos los widgets de la grilla."""
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

    def _show_no_cameras(self) -> None:
        lbl = QLabel("⚠  No se encontraron cámaras disponibles\n\nConecta una cámara y reinicia el monitoreo.")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("color: #8B949E; font-size: 16px; line-height: 1.6;")
        self._grid_layout.addWidget(lbl, 0, 0)
        self._cam_count_lbl.setText("0 cámaras")
        self._status_lbl.setText("⚠  Sin cámaras")
        self._status_lbl.setStyleSheet("color: #F59E0B; font-size: 13px; font-weight: bold;")
