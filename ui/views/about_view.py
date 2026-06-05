"""
ui/views/about_view.py
======================
Vista de "Acerca de Nosotros".

Presenta información sobre INGELAM (misión, visión, servicios, valores)
de forma estética y organizada en tarjetas profesionales (sin imágenes).
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


class _AboutCard(QFrame):
    """Tarjeta informativa para las secciones de Acerca de Nosotros."""

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
    Vista de Acerca de Nosotros.

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

        title = QLabel("🏢  Acerca de INGELAM")
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
            icon="⚡",
            title="INGELAM S.A.S.",
            content="Somos desarrolladores de ingeniería especializados en la automatización de procesos industriales e integración de tecnologías inteligentes para optimizar la seguridad y productividad empresarial.",
            highlight=True,
        )

        # Quiénes Somos
        card_who = _AboutCard(
            icon="👥",
            title="Quiénes Somos",
            content="INGELAM es una empresa consolidada en el sector industrial, dedicada al diseño y ejecución de proyectos de ingeniería electrónica, eléctrica y de sistemas. A través de SafeCHECK, introducimos la Inteligencia Artificial y Visión por Computadora al control de seguridad en obras y plantas de producción.",
        )

        # Misión
        card_mission = _AboutCard(
            icon="🎯",
            title="Nuestra Misión",
            content="Proveer soluciones integrales de automatización y seguridad industrial basadas en tecnología de punta. Nos enfocamos en maximizar la eficiencia productiva de nuestros clientes mientras resguardamos la integridad física de sus colaboradores mediante sistemas activos de monitoreo.",
        )

        # Visión
        card_vision = _AboutCard(
            icon="🔭",
            title="Nuestra Visión",
            content="Consolidarnos en el mercado regional como la compañía líder en integración de sistemas inteligentes de seguridad y automatización industrial, siendo reconocidos por la innovación, calidad de servicio y compromiso ético con la prevención de riesgos.",
        )

        # Servicios
        card_services = _AboutCard(
            icon="🛠️",
            title="Servicios y Líneas de Trabajo",
            content="• Monitoreo de seguridad activa en tiempo real con Inteligencia Artificial.\n"
                    "• Diseño e integración de tableros de control y automatización industrial.\n"
                    "• Programación de PLCs, interfaces HMI y sistemas SCADA de control centralizado.\n"
                    "• Consultoría e ingeniería de detalle para modernización de plantas.",
        )

        # Valores
        card_values = _AboutCard(
            icon="🛡️",
            title="Valores Corporativos",
            content="• Innovación: Buscamos siempre soluciones a la vanguardia de la tecnología.\n"
                    "• Seguridad: Protegemos la vida e integridad del talento humano por sobre todas las cosas.\n"
                    "• Calidad: Ofrecemos excelencia técnica y confiabilidad en cada uno de nuestros desarrollos.\n"
                    "• Compromiso: Trabajamos con transparencia, responsabilidad y rigor profesional.",
        )

        container_layout.addWidget(card_intro)
        container_layout.addWidget(card_who)
        container_layout.addWidget(card_mission)
        container_layout.addWidget(card_vision)
        container_layout.addWidget(card_services)
        container_layout.addWidget(card_values)
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
