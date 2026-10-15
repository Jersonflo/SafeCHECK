"""
ui/styles.py
=============
Dark Theme profesional para SafeCHECK.
Paleta oscura con acento naranja de seguridad industrial (#FF6100).

Colores de referencia:
  BG_PRIMARY    #0D1117   Fondo principal
  BG_SECONDARY  #161B22   Fondo de cards/paneles
  BG_TERTIARY   #1F2937   Fondo de elementos internos
  ACCENT        #FF6100   Naranja de seguridad
  ACCENT_HOVER  #E55500   Naranja oscuro (hover)
  SUCCESS       #22C55E   Verde (casco detectado)
  DANGER        #EF4444   Rojo (sin casco / alerta)
  WARNING       #F59E0B   Amarillo (neutro)
  TEXT_PRIMARY  #F0F6FC   Texto principal
  TEXT_MUTED    #8B949E   Texto secundario
  BORDER        #30363D   Bordes
"""

# ─── Constantes de color (reutilizables en código Python) ─────────────────────
BG_PRIMARY = "#0D1117"
BG_SECONDARY = "#161B22"
BG_TERTIARY = "#1F2937"
ACCENT = "#FF6100"
ACCENT_HOVER = "#E55500"
SUCCESS = "#22C55E"
SUCCESS_BG = "#052E16"
DANGER = "#EF4444"
DANGER_BG = "#450A0A"
WARNING = "#F59E0B"
TEXT_PRIMARY = "#F0F6FC"
TEXT_MUTED = "#8B949E"
BORDER = "#30363D"
BORDER_ACCENT = "#FF6100"

# ─── QSS Global ───────────────────────────────────────────────────────────────
MAIN_STYLESHEET = f"""
/* ═══════════════════════════════════════════
   BASE
═══════════════════════════════════════════ */
QMainWindow, .QWidget {{
    background-color: {BG_PRIMARY};
    color: {TEXT_PRIMARY};
    font-family: "Helvetica Neue", "SF Pro Display", "Segoe UI", Arial, sans-serif;
    font-size: 14px;
}}

QLabel {{
    background-color: transparent;
}}

QScrollArea {{
    background-color: transparent;
    border: none;
}}

QScrollBar:vertical {{
    background: {BG_SECONDARY};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 4px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{
    background: {TEXT_MUTED};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

/* ═══════════════════════════════════════════
   BOTONES — PRIMARIO (naranja)
═══════════════════════════════════════════ */
QPushButton#btn-primary {{
    background-color: {ACCENT};
    color: white;
    border: none;
    border-radius: 10px;
    padding: 14px 32px;
    font-size: 15px;
    font-weight: bold;
    letter-spacing: 0.5px;
}}
QPushButton#btn-primary:hover {{
    background-color: {ACCENT_HOVER};
}}
QPushButton#btn-primary:pressed {{
    background-color: #CC4A00;
}}

/* ═══════════════════════════════════════════
   BOTONES — SECUNDARIO (gris oscuro)
═══════════════════════════════════════════ */
QPushButton#btn-secondary {{
    background-color: {BG_TERTIARY};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 14px 28px;
    font-size: 14px;
    font-weight: 600;
}}
QPushButton#btn-secondary:hover {{
    background-color: #374151;
    border-color: {TEXT_MUTED};
}}
QPushButton#btn-secondary:pressed {{
    background-color: #1F2937;
}}

/* ═══════════════════════════════════════════
   BOTONES — GHOST (transparente con borde)
═══════════════════════════════════════════ */
QPushButton#btn-ghost {{
    background-color: transparent;
    color: {TEXT_MUTED};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 8px 20px;
    font-size: 13px;
}}
QPushButton#btn-ghost:hover {{
    color: {TEXT_PRIMARY};
    border-color: {TEXT_MUTED};
    background-color: {BG_SECONDARY};
}}

/* ═══════════════════════════════════════════
   BOTONES — DANGER (rojo)
═══════════════════════════════════════════ */
QPushButton#btn-danger {{
    background-color: {DANGER_BG};
    color: {DANGER};
    border: 1px solid {DANGER};
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 14px;
    font-weight: bold;
}}
QPushButton#btn-danger:hover {{
    background-color: #7F1D1D;
}}

/* ═══════════════════════════════════════════
   CARDS DE MENÚ (HomeView)
═══════════════════════════════════════════ */
QFrame#menu-card {{
    background-color: {BG_SECONDARY};
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 8px;
}}
QFrame#menu-card:hover {{
    border-color: {ACCENT};
    background-color: {BG_TERTIARY};
}}

/* ═══════════════════════════════════════════
   LABELS
═══════════════════════════════════════════ */
QLabel#title-main {{
    color: {TEXT_PRIMARY};
    font-size: 52px;
    font-weight: 900;
    letter-spacing: -1px;
}}
QLabel#title-accent {{
    color: {ACCENT};
    font-size: 52px;
    font-weight: 900;
    letter-spacing: -1px;
}}
QLabel#subtitle {{
    color: {TEXT_MUTED};
    font-size: 16px;
    letter-spacing: 1px;
}}
QLabel#section-title {{
    color: {TEXT_PRIMARY};
    font-size: 24px;
    font-weight: bold;
}}
QLabel#card-title {{
    color: {TEXT_PRIMARY};
    font-size: 18px;
    font-weight: bold;
}}
QLabel#card-desc {{
    color: {TEXT_MUTED};
    font-size: 13px;
}}
QLabel#badge-safe {{
    color: {SUCCESS};
    background-color: {SUCCESS_BG};
    border: 1px solid {SUCCESS};
    border-radius: 6px;
    padding: 4px 12px;
    font-size: 13px;
    font-weight: bold;
}}
QLabel#badge-danger {{
    color: {DANGER};
    background-color: {DANGER_BG};
    border: 1px solid {DANGER};
    border-radius: 6px;
    padding: 4px 12px;
    font-size: 13px;
    font-weight: bold;
}}
QLabel#badge-neutral {{
    color: {WARNING};
    background-color: #2D1B00;
    border: 1px solid {WARNING};
    border-radius: 6px;
    padding: 4px 12px;
    font-size: 13px;
    font-weight: bold;
}}
QLabel#camera-title {{
    color: {TEXT_PRIMARY};
    font-size: 12px;
    font-weight: bold;
    background-color: rgba(13, 17, 23, 0.7);
    padding: 4px 8px;
    border-radius: 4px;
}}
QLabel#version-label {{
    color: {TEXT_MUTED};
    font-size: 11px;
}}
QLabel#author-label {{
    color: {ACCENT};
    font-size: 12px;
    font-weight: bold;
    letter-spacing: 2px;
}}

/* ═══════════════════════════════════════════
   CAMERA CELL
═══════════════════════════════════════════ */
QFrame#camera-cell {{
    background-color: {BG_SECONDARY};
    border: 1px solid {BORDER};
    border-radius: 10px;
}}
QFrame#camera-cell-danger {{
    background-color: {BG_SECONDARY};
    border: 2px solid {DANGER};
    border-radius: 10px;
}}
QFrame#camera-cell-safe {{
    background-color: {BG_SECONDARY};
    border: 2px solid {SUCCESS};
    border-radius: 10px;
}}

/* ═══════════════════════════════════════════
   PROGRESS BAR (Loading)
═══════════════════════════════════════════ */
QProgressBar#loading-bar {{
    background-color: {BG_TERTIARY};
    border: none;
    border-radius: 4px;
    height: 6px;
    text-align: center;
}}
QProgressBar#loading-bar::chunk {{
    background-color: {ACCENT};
    border-radius: 4px;
}}

/* ═══════════════════════════════════════════
   SEPARADORES
═══════════════════════════════════════════ */
QFrame#h-divider {{
    background-color: {BORDER};
    max-height: 1px;
    border: none;
}}

/* ═══════════════════════════════════════════
   TOOLBAR / NAVBAR INFERIOR
═══════════════════════════════════════════ */
QFrame#toolbar {{
    background-color: {BG_SECONDARY};
    border-top: 1px solid {BORDER};
}}
/* Botones de la barra inferior: menos relleno vertical para que el texto quepa */
QFrame#toolbar QPushButton#btn-secondary,
QFrame#toolbar QPushButton#btn-danger {{
    padding: 8px 22px;
}}
"""
