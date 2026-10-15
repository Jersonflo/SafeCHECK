"""
ui/views/home_view.py
======================
Vista del menú principal de SafeCHECK.

Muestra:
  • Branding de SafeCHECK
  • 3 cards de navegación: Iniciar, Medidas de Seguridad, Acerca del proyecto
  • Footer con versión
"""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from config import CONFIG


class _MenuCard(QFrame):
    """Card clickeable del menú principal."""

    clicked: pyqtSignal = pyqtSignal()

    def __init__(
        self,
        icon: str,
        title: str,
        description: str,
        primary: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("menu-card")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(300, 220)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)

        # Icono
        icon_lbl = QLabel(icon)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
        icon_lbl.setStyleSheet("font-size: 32px; background: transparent; border: none;")

        # Título
        title_lbl = QLabel(title)
        title_lbl.setObjectName("card-title")
        title_lbl.setStyleSheet(
            "color: #FF6100; font-size: 17px; font-weight: bold; background: transparent; border: none;"
            if primary
            else "background: transparent; border: none;"
        )

        # Descripción
        desc_lbl = QLabel(description)
        desc_lbl.setObjectName("card-desc")
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("background: transparent; border: none;")

        layout.addWidget(icon_lbl)
        layout.addWidget(title_lbl)
        layout.addWidget(desc_lbl)
        layout.addStretch()

    def mousePressEvent(self, event) -> None:  # noqa: ANN001
        self.clicked.emit()
        super().mousePressEvent(event)

    def enterEvent(self, event) -> None:  # noqa: ANN001
        self.setStyleSheet(
            "QFrame#menu-card { border: 1px solid #FF6100; background-color: #1F2937; border-radius: 14px; }"
        )
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # noqa: ANN001
        self.setStyleSheet("")
        super().leaveEvent(event)


class HomeView(QWidget):
    """
    Vista del menú principal.

    Señales:
        go_to_start:   Usuario presionó 'Iniciar'
        go_to_safety:  Usuario presionó 'Medidas de Seguridad'
        go_to_about:   Usuario presionó 'Acerca de Nosotros'
    """

    go_to_start: pyqtSignal = pyqtSignal()
    go_to_safety: pyqtSignal = pyqtSignal()
    go_to_about: pyqtSignal = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Área de contenido central ──────────────────────────────────────────
        content = QVBoxLayout()
        content.setContentsMargins(60, 0, 60, 0)
        content.setSpacing(0)

        content.addStretch(2)

        # ── Branding ──────────────────────────────────────────────────────────
        brand_row = QHBoxLayout()
        brand_row.setSpacing(0)

        lbl_safe = QLabel("Safe")
        lbl_safe.setObjectName("title-main")

        lbl_check = QLabel("CHECK")
        lbl_check.setObjectName("title-accent")

        brand_row.addWidget(lbl_safe)
        brand_row.addWidget(lbl_check)
        brand_row.addStretch()

        subtitle = QLabel("SISTEMA DE DETECCIÓN DE EQUIPOS DE PROTECCIÓN PERSONAL")
        subtitle.setObjectName("subtitle")

        content.addLayout(brand_row)
        content.addSpacing(8)
        content.addWidget(subtitle)
        content.addSpacing(48)

        # ── Divider ───────────────────────────────────────────────────────────
        divider = QFrame()
        divider.setObjectName("h-divider")
        divider.setFrameShape(QFrame.Shape.HLine)
        content.addWidget(divider)
        content.addSpacing(48)

        # ── Cards de navegación ───────────────────────────────────────────────
        cards_row = QHBoxLayout()
        cards_row.setSpacing(24)

        self._card_start = _MenuCard(
            icon="🎬",
            title="Iniciar Monitoreo",
            description="Activa las cámaras disponibles y comienza la detección de cascos en tiempo real.",
            primary=True,
        )
        self._card_safety = _MenuCard(
            icon="🦺",
            title="Medidas de Seguridad",
            description="Consulta las normas y protocolos de seguridad industrial del área de trabajo.",
        )
        self._card_about = _MenuCard(
            icon="💡",
            title="Acerca del Proyecto",
            description="Qué hace SafeCHECK, cómo funciona por dentro y con qué tecnologías está hecho.",
        )

        cards_row.addWidget(self._card_start)
        cards_row.addWidget(self._card_safety)
        cards_row.addWidget(self._card_about)
        cards_row.addStretch()

        content.addLayout(cards_row)
        content.addStretch(3)

        root.addLayout(content)

        # ── Footer ────────────────────────────────────────────────────────────
        footer = QFrame()
        footer.setObjectName("toolbar")
        footer.setFixedHeight(44)

        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(24, 0, 24, 0)

        author_lbl = QLabel(f"Proyecto personal · {CONFIG.AUTHOR}")
        author_lbl.setObjectName("author-label")

        version_lbl = QLabel(f"v{CONFIG.APP_VERSION}")
        version_lbl.setObjectName("version-label")

        footer_layout.addWidget(author_lbl)
        footer_layout.addStretch()
        footer_layout.addWidget(version_lbl)

        root.addWidget(footer)

        # ── Conexiones ────────────────────────────────────────────────────────
        self._card_start.clicked.connect(self.go_to_start)
        self._card_safety.clicked.connect(self.go_to_safety)
        self._card_about.clicked.connect(self.go_to_about)
