"""
ui/views/safety_view.py
========================
Vista de las Medidas de Seguridad Industrial.

Presenta las directrices y normas de seguridad en un formato estructurado,
limpio y profesional utilizando texto y tarjetas estilizadas (sin imágenes).
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


class _SafetyCard(QFrame):
    """Tarjeta para mostrar una norma o directriz de seguridad."""

    def __init__(self, icon: str, title: str, content: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("menu-card")  # Reutiliza el estilo de tarjeta del menú
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
        title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; background: transparent; border: none;")

        header.addWidget(icon_lbl)
        header.addWidget(title_lbl)
        header.addStretch()

        # Contenido / Texto de la norma
        desc_lbl = QLabel(content)
        desc_lbl.setObjectName("card-desc")
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("font-size: 13px; line-height: 1.5; background: transparent; border: none;")

        layout.addLayout(header)
        layout.addWidget(desc_lbl)


class SafetyView(QWidget):
    """
    Vista de las Medidas de Seguridad de SafeCHECK.

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

        title = QLabel("🦺  Manual de Medidas de Seguridad")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #F0F6FC;")

        header_layout.addWidget(title)
        header_layout.addStretch()

        root.addWidget(header)

        # ── Scroll Area para las tarjetas de normas ───────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(40, 24, 40, 24)
        container_layout.setSpacing(16)

        # 1. Introducción
        card_intro = _SafetyCard(
            icon="📋",
            title="Introducción al Manual",
            content="El presente manual establece las directrices fundamentales para garantizar la seguridad del personal en las áreas de operación. El uso correcto y obligatorio del Equipo de Protección Personal (EPP), en especial el casco de seguridad, es indispensable para prevenir accidentes graves.",
        )

        # 2. Herramientas
        card_tools = _SafetyCard(
            icon="🛠️",
            title="Uso de Herramientas y Equipamiento",
            content="• Utilice las herramientas únicamente para el propósito con el que fueron diseñadas.\n"
                    "• Inspeccione minuciosamente el estado de los equipos antes de comenzar su jornada.\n"
                    "• Reporte cualquier herramienta desgastada, dañada o defectuosa de inmediato al supervisor.\n"
                    "• No realice reparaciones provisionales ni alteraciones no autorizadas en los equipos.",
        )

        # 3. Capacitación y simulacros
        card_train = _SafetyCard(
            icon="🎓",
            title="Capacitación y Simulacros de Evacuación",
            content="• Es requisito obligatorio asistir y participar activamente en todas las capacitaciones de seguridad de la planta.\n"
                    "• Memorice las rutas de evacuación primarias y secundarias de su zona de trabajo, así como la ubicación de los extintores.\n"
                    "• En caso de simulacro o emergencia real, proceda en orden hacia el Punto de Encuentro designado de manera calmada y firme.",
        )

        # 4. Botiquín y Primeros Auxilios
        card_first_aid = _SafetyCard(
            icon="🩹",
            title="Botiquín y Primeros Auxilios",
            content="• Identifique de antemano el botiquín de emergencias más cercano a su estación.\n"
                    "• Ante un incidente, mantenga la calma y de aviso inmediato al personal de brigada médica de la empresa.\n"
                    "• Evite suministrar medicamentos o tratamientos avanzados a un compañero lesionado a menos que cuente con certificación médica oficial.",
        )

        # 5. Nota de Cumplimiento
        card_notice = _SafetyCard(
            icon="⚠️",
            title="Nota de Cumplimiento Obligatorio",
            content="Recuerde: Su seguridad y la de sus compañeros de trabajo es nuestra máxima prioridad. El incumplimiento del uso del equipo de protección o de estas normas puede acarrear sanciones administrativas severas o la suspensión temporal o definitiva de sus actividades.",
        )

        container_layout.addWidget(card_intro)
        container_layout.addWidget(card_tools)
        container_layout.addWidget(card_train)
        container_layout.addWidget(card_first_aid)
        container_layout.addWidget(card_notice)
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
        back_btn.setFixedHeight(38)
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(self.go_home)

        toolbar_layout.addWidget(back_btn)
        toolbar_layout.addStretch()

        root.addWidget(toolbar)
