"""
ui/app.py
=========
Ventana principal de SafeCHECK (MainWindow).

Implementa la navegación basada en QStackedWidget:
  - Index 0: HomeView (Menú principal)
  - Index 1: LoadingView (Pantalla de carga/inicialización)
  - Index 2: CameraView (Monitoreo de cámaras en grilla)
  - Index 3: SafetyView (Medidas de seguridad)
  - Index 4: AboutView (Acerca del proyecto)
"""

from __future__ import annotations

import logging
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QMessageBox, QWidget

from config import CONFIG
from ui.styles import MAIN_STYLESHEET
from ui.views import AboutView, CameraView, HomeView, LoadingView, SafetyView

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Ventana principal que gestiona las vistas mediante un QStackedWidget."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(CONFIG.APP_NAME)
        self.resize(CONFIG.WINDOW_WIDTH, CONFIG.WINDOW_HEIGHT)
        self.setMinimumSize(800, 600)

        # Aplicar tema QSS
        self.setStyleSheet(MAIN_STYLESHEET)

        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)

        # Instanciar vistas
        self.home_view = HomeView(parent=self)
        self.loading_view = LoadingView(parent=self)
        self.camera_view = CameraView(parent=self)
        self.safety_view = SafetyView(parent=self)
        self.about_view = AboutView(parent=self)

        # Añadir al stack (los índices corresponden al orden de adición)
        self.stack.addWidget(self.home_view)    # Index 0
        self.stack.addWidget(self.loading_view) # Index 1
        self.stack.addWidget(self.camera_view)  # Index 2
        self.stack.addWidget(self.safety_view)  # Index 3
        self.stack.addWidget(self.about_view)   # Index 4

        # Mostrar menú principal inicialmente
        self.stack.setCurrentIndex(0)

    def _connect_signals(self) -> None:
        # Menú principal -> Otras vistas
        self.home_view.go_to_start.connect(self._start_monitoring_flow)
        self.home_view.go_to_safety.connect(lambda: self.stack.setCurrentIndex(3))
        self.home_view.go_to_about.connect(lambda: self.stack.setCurrentIndex(4))

        # Pantalla de carga
        self.loading_view.loading_complete.connect(self._on_loading_complete)
        self.loading_view.loading_error.connect(self._on_loading_error)

        # Vistas secundarias -> Regresar al menú
        self.camera_view.go_home.connect(self._go_home)
        self.safety_view.go_home.connect(self._go_home)
        self.about_view.go_home.connect(self._go_home)

    @pyqtSlot()
    def _start_monitoring_flow(self) -> None:
        """Inicia la transición a la pantalla de carga e inicializa recursos."""
        logger.info("Iniciando flujo de monitoreo...")
        self.stack.setCurrentIndex(1)
        self.loading_view.start_loading()

    @pyqtSlot(list)
    def _on_loading_complete(self, camera_indices: list[int]) -> None:
        """Transición a la vista de cámaras una vez que todo está listo."""
        logger.info("Carga de modelo y cámaras completa. Mostrando monitoreo.")
        self.stack.setCurrentIndex(2)
        self.camera_view.start_cameras(camera_indices)

    @pyqtSlot(str)
    def _on_loading_error(self, message: str) -> None:
        """Muestra alerta en caso de error crítico de carga."""
        QMessageBox.critical(
            self,
            "Error de Inicialización",
            f"Ocurrió un error al cargar el sistema:\n\n{message}\n\nVolviendo al menú principal.",
        )
        self._go_home()

    @pyqtSlot()
    def _go_home(self) -> None:
        """Regresa de forma segura al menú principal."""
        self.stack.setCurrentIndex(0)

    def closeEvent(self, event) -> None:  # noqa: N802, ANN001
        """Asegura liberar todas las cámaras activas al cerrar la ventana."""
        logger.info("Cerrando aplicación. Deteniendo hilos de cámaras...")
        self.camera_view.stop_cameras()
        event.accept()
