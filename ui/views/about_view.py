"""
ui/views/about_view.py
======================
Vista "Acerca del Proyecto".

Presenta qué es SafeCHECK, cómo funciona, su stack tecnológico y su autor,
organizado en tarjetas (sin imágenes).
"""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from config import CONFIG


class _AboutCard(QFrame):
    """Tarjeta informativa para las secciones de Acerca del Proyecto."""

    def __init__(self, icon: str, title: str, content: str, highlight: bool = False, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("menu-card")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Encabezado (Icono + Título)
        header = QHBoxLayout()
        header.setSpacing(12)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 24px; background: transparent; border: none;")

        title_lbl = QLabel(title)
        title_lbl.setObjectName("card-title")
        title_lbl.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #FF6100; background: transparent; border: none;"
            if highlight
            else "font-size: 16px; font-weight: bold; background: transparent; border: none;"
        )

        header.addWidget(icon_lbl)
        header.addWidget(title_lbl)
        header.addStretch()

        # Contenido / Texto
        desc_lbl = QLabel(content)
        desc_lbl.setObjectName("card-desc")
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("font-size: 13px; line-height: 1.5; background: transparent; border: none;")

        layout.addLayout(header)
        layout.addWidget(desc_lbl)


class AboutView(QWidget):
    """
    Vista de Acerca del Proyecto.

    Señales:
        go_home: Usuario desea regresar al menú principal.
    """

    go_home: pyqtSignal = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ────────────────────────────────────────────────────────────
        header = QFrame()
        header.setObjectName("toolbar")
        header.setFixedHeight(52)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        title = QLabel("💡  Acerca del Proyecto")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #F0F6FC;")

        header_layout.addWidget(title)
        header_layout.addStretch()

        root.addWidget(header)

        # ── Scroll Area para las tarjetas de información ──────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(40, 24, 40, 24)
        container_layout.setSpacing(16)

        # Intro destacada
        card_intro = _AboutCard(
            icon="⛑️",
            title="SafeCHECK",
            content="Sistema de visión por computador que vigila en tiempo real si las personas en una obra o planta llevan casco de seguridad. Analiza varias cámaras a la vez y marca en rojo a quien no lo tiene puesto.",
            highlight=True,
        )

        # Cómo funciona
        card_how = _AboutCard(
            icon="⚙️",
            title="Cómo Funciona",
            content="• Cada cámara tiene su propio hilo de captura, así el video se muestra en vivo sin acumular retraso.\n"
                    "• Un modelo YOLOv8 entrenado con dos clases (casco / no-casco) analiza el fotograma más reciente en un hilo aparte.\n"
                    "• Los recuadros y el estado de cada cámara se actualizan sobre el video en vivo.\n"
                    "• Usa GPU NVIDIA si está disponible y, si no, corre en CPU.",
        )

        # Tecnologías
        card_stack = _AboutCard(
            icon="🧰",
            title="Tecnologías",
            content="Python · YOLOv8 (Ultralytics) · PyTorch · OpenCV · PyQt6",
        )

        # Autor
        card_author = _AboutCard(
            icon="👤",
            title="Autor",
            content=f"Proyecto personal desarrollado por {CONFIG.AUTHOR}.\n"
                    "Código fuente: github.com/Jersonflo/SafeCHECK",
        )

        container_layout.addWidget(card_intro)
        container_layout.addWidget(card_how)
        container_layout.addWidget(card_stack)
        container_layout.addWidget(card_author)
        container_layout.addStretch()

        scroll.setWidget(container)
        root.addWidget(scroll, stretch=1)

        # ── Toolbar Inferior con botón Regresar ───────────────────────────────
        toolbar = QFrame()
        toolbar.setObjectName("toolbar")
        toolbar.setFixedHeight(60)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(20, 0, 20, 0)

        back_btn = QPushButton("⬅  Regresar al Menú")
        back_btn.setObjectName("btn-secondary")
        back_btn.setMinimumHeight(40)
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(self.go_home)

        toolbar_layout.addWidget(back_btn)
        toolbar_layout.addStretch()

        root.addWidget(toolbar)
