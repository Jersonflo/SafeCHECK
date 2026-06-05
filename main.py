"""
main.py
=======
Punto de entrada principal para SafeCHECK.

Configura el sistema de registro (logging), inicializa el bucle de eventos
de PyQt6 y lanza la interfaz gráfica principal.
"""

from __future__ import annotations

import logging
import os
import sys

# Activar fallback a CPU para operaciones MPS no soportadas (ej. torchvision::nms)
# DEBE ir antes de cualquier import de torch/ultralytics
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

from PyQt6.QtWidgets import QApplication

from ui.app import MainWindow

# ─── Configuración de Logging ─────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("SafeCHECK")


def main() -> None:
    """Función de inicio de la aplicación."""
    logger.info("Iniciando SafeCHECK v2.0...")
    
    # Crear la aplicación Qt
    app = QApplication(sys.argv)
    app.setApplicationName("SafeCHECK")
    app.setOrganizationName("INGELAM")
    
    # Crear e iniciar la ventana principal
    window = MainWindow()
    window.show()
    
    # Ejecutar el bucle de eventos principal de Qt
    logger.info("Bucle de eventos iniciado.")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
