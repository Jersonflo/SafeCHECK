"""
config.py
=========
Configuración global de SafeCHECK.

⚙️  UMBRAL DE DETECCIÓN
   Modifica DETECTION_CONFIDENCE para ajustar la sensibilidad del modelo:
   - Valores bajos  (0.3–0.45) → detecta más, pero más falsos positivos
   - Valores medios (0.50)     → balance recomendado
   - Valores altos  (0.65–0.8) → más estricto, menos falsas alarmas
"""

from dataclasses import dataclass, field
from typing import Final


@dataclass(frozen=True)
class AppConfig:
    # ─── Aplicación ────────────────────────────────────────────────────────────
    APP_NAME: str = "SafeCHECK"
    APP_VERSION: str = "2.0"
    COMPANY: str = "INGELAM"
    WINDOW_WIDTH: int = 1280
    WINDOW_HEIGHT: int = 720

    # ─── Modelo YOLO ───────────────────────────────────────────────────────────
    # Modelo entrenado propio para detectar cascos de seguridad
    # Clases: 'casco' (con casco) | 'no-casco' (sin casco)
    MODEL_NAME: str = "models/best.pt"

    # ⚙️  AJUSTA AQUÍ EL UMBRAL DE CONFIANZA (0.0 → 1.0)
    DETECTION_CONFIDENCE: float = 0.55

    # ⚙️  TAMAÑO DE IMAGEN PARA INFERENCIA (ej. 320, 416, 640)
    # Tu modelo fue entrenado a 640 — usar ese valor para máxima precisión.
    # Puedes bajar a 416 si necesitas más velocidad sin perder mucha calidad.
    MODEL_IMGSZ: int = 640

    # ⚙️  MEDIA PRECISIÓN (FP16) — solo funciona bien en CUDA (NVIDIA).
    # En MPS (Apple Silicon) puede causar problemas de detección, dejarlo en False.
    USE_HALF_PRECISION: bool = False

    # ⚙️  SKIP DE FRAMES — corre inferencia cada N frames.
    # En los frames intermedios se muestra el último resultado anotado.
    # Valor 1 = inferencia en cada frame (sin skip).
    # Valor 2 = inferencia cada 2 frames (buen balance).
    # Valor 3 = inferencia cada 3 frames (máxima fluidez).
    INFERENCE_SKIP_FRAMES: int = 1

    # ─── Cámaras ───────────────────────────────────────────────────────────────
    MAX_CAMERAS: int = 5          # Número máximo de cámaras a detectar
    CAMERA_FPS_LIMIT: int = 15   # FPS máximos por cámara (reduce carga de CPU)
    CAMERA_FRAME_WIDTH: int = 640
    CAMERA_FRAME_HEIGHT: int = 480

    # ─── UI / Grilla ───────────────────────────────────────────────────────────
    CAMERA_CELL_MIN_WIDTH: int = 400
    CAMERA_CELL_MIN_HEIGHT: int = 300

    # ─── Clases del modelo (palabras clave para clasificar detecciones) ─────────
    # Palabras que indican VIOLACIÓN (sin casco)
    VIOLATION_KEYWORDS: tuple = ("no-casco", "no_casco", "no casco")
    # Palabras que indican CUMPLIMIENTO (con casco)
    SAFE_KEYWORDS: tuple = ("casco", "con-casco", "con_casco")


# Instancia única global — importar directamente en otros módulos
CONFIG: Final[AppConfig] = AppConfig()
