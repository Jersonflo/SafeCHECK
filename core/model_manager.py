"""
core/model_manager.py
======================
Singleton del modelo YOLO para detección de cascos de seguridad.

El modelo se descarga automáticamente desde HuggingFace Hub la primera vez
(~6 MB, se cachea localmente para usos posteriores).

Modelo: keremberke/yolov8n-hard-hat-detection
Clases: 'Hardhat' (con casco) | 'NO-Hardhat' (sin casco) | 'Person'
"""

from __future__ import annotations

import logging
import os
import threading
from dataclasses import dataclass
from typing import Optional

import numpy as np

from config import CONFIG
from utils.resource_path import resource_path

logger = logging.getLogger(__name__)


@dataclass
class Detection:
    """Representa una detección individual del modelo."""
    class_name: str
    confidence: float
    bbox: tuple[int, int, int, int]  # x1, y1, x2, y2

    @property
    def is_violation(self) -> bool:
        """True si la detección indica que la persona NO tiene casco."""
        name = self.class_name.lower()
        # Verificar violación PRIMERO (ej. 'no-casco' contiene 'casco' pero es violación)
        return any(kw in name for kw in CONFIG.VIOLATION_KEYWORDS)

    @property
    def has_helmet(self) -> bool:
        """True si la detección indica que la persona TIENE casco (y NO es violación)."""
        if self.is_violation:
            return False
        name = self.class_name.lower()
        return any(kw in name for kw in CONFIG.SAFE_KEYWORDS)

    @property
    def is_neutral(self) -> bool:
        """True si la detección es neutral (ej. 'Person' sin info de casco)."""
        return not self.has_helmet and not self.is_violation


class ModelManager:
    """
    Singleton que gestiona el modelo YOLO.

    Uso:
        manager = ModelManager.get_instance()
        manager.load()   # llamar una sola vez (bloqueante, corre en thread)
        dets = manager.detect(frame, confidence=0.5)
    """

    _instance: Optional[ModelManager] = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> ModelManager:
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._model = None
                cls._instance._is_loaded = False
                cls._instance._device = "cpu"
                # Un mismo modelo YOLO no es seguro entre hilos: serializar inferencias
                cls._instance._predict_lock = threading.Lock()

                # Auto-detectar GPU solo si hay suficiente memoria
                # MPS en equipos con 8GB RAM puede causar problemas;
                # CUDA (NVIDIA) generalmente funciona bien.
                try:
                    import torch
                    if torch.cuda.is_available():
                        cls._instance._device = "cuda"
                    # MPS deshabilitado por defecto en equipos con poca RAM.
                    # Descomentar la siguiente línea si tienes 16GB+ de RAM:
                    # elif torch.backends.mps.is_available():
                    #     cls._instance._device = "mps"
                except Exception:
                    pass
        return cls._instance

    @classmethod
    def get_instance(cls) -> ModelManager:
        """Retorna la instancia única del ModelManager."""
        return cls()

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    def load(self, model_name: str) -> None:
        """
        Carga el modelo YOLO desde HuggingFace Hub.
        Bloqueante — llamar desde un QThread, nunca desde el hilo principal.

        Args:
            model_name: Nombre del modelo en HuggingFace Hub.
        """
        if self._is_loaded:
            return

        logger.info("Cargando modelo YOLO: %s en dispositivo: %s", model_name, self._device)
        try:
            from ultralytics import YOLO  # import diferido para no bloquear inicio
            
            # Intentar resolver la ruta usando resource_path
            resolved_path = resource_path(model_name)
            
            # Si es un archivo local existente, usarlo directamente
            if os.path.exists(resolved_path):
                model_path = resolved_path
                logger.info("Modelo local detectado y cargado desde: %s", model_path)
            elif os.path.exists(model_name):
                model_path = model_name
                logger.info("Modelo local detectado y cargado desde: %s", model_path)
            # Si no, y tiene una barra diagonal, tratar como repositorio de Hugging Face
            elif "/" in model_name:
                logger.info("Descargando/Verificando modelo desde Hugging Face Hub: %s", model_name)
                from huggingface_hub import hf_hub_download
                model_path = hf_hub_download(repo_id=model_name, filename="best.pt")
                logger.info("Modelo descargado exitosamente en: %s", model_path)
            else:
                model_path = model_name
                
            self._model = YOLO(model_path)
            # Determinar si usar media precisión
            use_half = CONFIG.USE_HALF_PRECISION and self._device != "cpu"
            # Warmup rápido con un frame negro para pre-compilar el modelo en el dispositivo
            dummy = np.zeros((240, 320, 3), dtype=np.uint8)
            self._model.predict(
                dummy, verbose=False, device=self._device,
                imgsz=CONFIG.MODEL_IMGSZ, **({"half": True} if use_half else {}),
            )
            self._is_loaded = True
            logger.info("Modelo cargado y listo (device=%s, half=%s).", self._device, use_half)
        except Exception as exc:
            logger.exception("Error al cargar el modelo: %s", exc)
            raise

    def detect(
        self,
        frame: np.ndarray,
        confidence: float = 0.50,
        imgsz: int = 320,
    ) -> list[Detection]:
        """
        Ejecuta inferencia sobre un frame de cámara.

        Args:
            frame: Frame BGR de OpenCV.
            confidence: Umbral de confianza (0.0 – 1.0).
            imgsz: Tamaño de entrada del modelo para inferencia.

        Returns:
            Lista de detecciones (vacía si el modelo no está cargado).
            El dibujo de los recuadros lo hace el CameraWorker sobre el video en vivo.
        """
        if not self._is_loaded or self._model is None:
            return []

        try:
            use_half = CONFIG.USE_HALF_PRECISION and self._device != "cpu"
            with self._predict_lock:
                results = self._model.predict(
                    frame,
                    conf=confidence,
                    verbose=False,
                    stream=False,
                    imgsz=imgsz,
                    device=self._device,
                    **({"half": True} if use_half else {}),
                )
            result = results[0]

            detections: list[Detection] = []
            if result.boxes is not None:
                for box in result.boxes:
                    cls_id = int(box.cls[0].item())
                    cls_name = result.names[cls_id]
                    conf_val = float(box.conf[0].item())
                    x1, y1, x2, y2 = (int(v) for v in box.xyxy[0].tolist())
                    detections.append(
                        Detection(
                            class_name=cls_name,
                            confidence=conf_val,
                            bbox=(x1, y1, x2, y2),
                        )
                    )

            return detections

        except Exception as exc:
            logger.exception("Error en detect: %s", exc)
            return []
