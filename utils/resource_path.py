"""
utils/resource_path.py
=======================
Función centralizada para resolver rutas de recursos.
Compatible con desarrollo normal y con empaquetado PyInstaller.
"""

import os
import sys


def resource_path(relative_path: str) -> str:
    """
    Retorna la ruta absoluta a un recurso.

    En modo desarrollo: usa el directorio raíz del proyecto.
    Con PyInstaller (--onefile): usa la carpeta temporal _MEIPASS.

    Args:
        relative_path: Ruta relativa desde la raíz del proyecto.

    Returns:
        Ruta absoluta al recurso.
    """
    try:
        # PyInstaller crea una carpeta temporal y almacena la ruta en _MEIPASS
        base_path: str = sys._MEIPASS  # type: ignore[attr-defined]
    except AttributeError:
        # Modo desarrollo: usa el directorio del archivo main.py (raíz del proyecto)
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    return os.path.join(base_path, relative_path)
