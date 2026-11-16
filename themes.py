"""Motywy (skórki) interfejsu OmniTV oparte o Qt Style Sheets."""

from __future__ import annotations

THEMES = {
    "Ciemny": {
        "window": "#101318",
        "panel": "#181d25",
        "base": "#11161d",
        "text": "#e8edf5",
        "subtext": "#929dad",
        "accent": "#67a3ff",
        "accent_text": "#ffffff",
        "border": "#29313d",
        "hover": "#252e3a",
        "selected": "#243d60",
        "selected_text": "#ffffff",
    },
    "Jasny": {
        "window": "#f3f5f8",
        "panel": "#ffffff",
        "base": "#ffffff",
        "text": "#172033",
        "subtext": "#647084",
        "accent": "#326de6",
        "accent_text": "#ffffff",
        "border": "#dce2eb",
        "hover": "#edf2fa",
        "selected": "#dce8ff",
        "selected_text": "#0b1b33",
    },
    "Nocny błękit": {
        "window": "#0b1420",
        "panel": "#111f30",
        "base": "#0c1928",
        "text": "#e0e8f0",
        "subtext": "#91a5bd",
        "accent": "#54b8ff",
        "accent_text": "#04121f",
        "border": "#20344b",
        "hover": "#1a2c40",
        "selected": "#1d4164",
        "selected_text": "#ffffff",
    },
    "Leśny": {
        "window": "#101914",
        "panel": "#17231c",
        "base": "#111b15",
        "text": "#e3ecdf",
        "subtext": "#98aa9b",
        "accent": "#5bc98b",
        "accent_text": "#06130c",
        "border": "#2a3a2f",
        "hover": "#233329",
        "selected": "#2b5039",
        "selected_text": "#ffffff",
    },
    "Kontrast": {
        "window": "#000000",
        "panel": "#000000",
        "base": "#000000",
        "text": "#ffffff",
        "subtext": "#d0d0d0",
        "accent": "#ffd400",
        "accent_text": "#000000",
        "border": "#ffffff",
        "hover": "#333300",
        "selected": "#ffd400",
        "selected_text": "#000000",
    },
    "Fiolet": {
        "window": "#15121d",
        "panel": "#201b2b",
        "base": "#191521",
        "text": "#f0eafa",
        "subtext": "#aa9dbd",
        "accent": "#bd8cff",
        "accent_text": "#1b1028",
        "border": "#382d49",
        "hover": "#2c243a",
        "selected": "#493665",
        "selected_text": "#ffffff",
    },
}

DEFAULT_THEME = "Ciemny"


def theme_names() -> list[str]:
    return list(THEMES.keys())


def build_stylesheet(name: str) -> str:
    colors = THEMES.get(name, THEMES[DEFAULT_THEME])
    return f"""
    QMainWindow, QWidget {{
        background-color: {colors['window']};
        color: {colors['text']};
        font-size: 13px;
    }}
    QLabel#hint, QLabel#epgLabel {{ color: {colors['subtext']}; }}
    QLabel#nowPlaying {{ color: {colors['text']}; font-size: 16px; font-weight: 700; }}
    QWidget#playerWidget {{ background-color: #000000; border-radius: 12px; }}
    QLineEdit, QComboBox {{
        background-color: {colors['base']};
        color: {colors['text']};
        border: 1px solid {colors['border']};
        border-radius: 9px;
        padding: 8px 10px;
        selection-background-color: {colors['accent']};
        selection-color: {colors['accent_text']};
    }}
    QLineEdit:focus, QComboBox:focus {{ border: 1px solid {colors['accent']}; }}
    QComboBox::drop-down {{ border: 0; width: 24px; }}
    QComboBox QAbstractItemView {{
        background-color: {colors['base']};
        color: {colors['text']};
        border: 1px solid {colors['border']};
        border-radius: 8px;
        selection-background-color: {colors['accent']};
        selection-color: {colors['accent_text']};
    }}
    QPushButton {{
        background-color: {colors['panel']};
        color: {colors['text']};
        border: 1px solid {colors['border']};
        border-radius: 9px;
        padding: 8px 13px;
        font-weight: 600;
    }}
    QPushButton:hover {{
        background-color: {colors['hover']};
        border-color: {colors['accent']};
    }}
    QPushButton:pressed {{
        background-color: {colors['accent']};
        color: {colors['accent_text']};
    }}
    QPushButton:disabled {{ color: {colors['subtext']}; }}
    QPushButton#recordButton[recording="true"] {{
        background-color: #d83242;
        color: #ffffff;
        border: 1px solid #f26370;
    }}
    QPushButton#recordButton[recording="true"]:hover {{
        background-color: #b92535;
        border-color: #ff7b86;
    }}
    QPushButton#primaryButton {{
        background-color: {colors['accent']};
        color: {colors['accent_text']};
        border-color: {colors['accent']};
    }}
    QListWidget {{
        background-color: {colors['base']};
        color: {colors['text']};
        border: 1px solid {colors['border']};
        border-radius: 10px;
        outline: none;
        alternate-background-color: {colors['panel']};
    }}
    QListWidget::item {{ padding: 7px 8px; border-radius: 6px; }}
    QListWidget::item:hover {{ background-color: {colors['hover']}; }}
    QListWidget::item:selected {{
        background-color: {colors['selected']};
        color: {colors['selected_text']};
    }}
    QSlider::groove:horizontal {{
        height: 4px;
        background: {colors['border']};
        border-radius: 2px;
    }}
    QSlider::sub-page:horizontal {{
        background: {colors['accent']};
        border-radius: 2px;
    }}
    QSlider::handle:horizontal {{
        background: {colors['accent']};
        width: 14px;
        margin: -6px 0;
        border-radius: 7px;
    }}
    QSplitter::handle {{ background-color: transparent; width: 5px; }}
    QToolTip {{
        background-color: {colors['base']};
        color: {colors['text']};
        border: 1px solid {colors['border']};
    }}
    QFrame#titleBar {{
        background-color: {colors['window']};
        border-bottom: 1px solid {colors['border']};
    }}
    QLabel#titleText {{
        color: {colors['text']};
        font-weight: 600;
        padding-left: 4px;
    }}
    QPushButton#titleButton, QPushButton#closeButton {{
        background-color: transparent;
        color: {colors['text']};
        border: none;
        border-radius: 0;
        padding: 0;
        font-size: 15px;
    }}
    QPushButton#titleButton:hover {{ background-color: {colors['hover']}; }}
    QPushButton#closeButton:hover {{
        background-color: #c42b1c;
        color: #ffffff;
    }}
    QSizeGrip {{ background-color: transparent; }}
    """
