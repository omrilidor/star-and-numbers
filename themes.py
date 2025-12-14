# themes.py

"""
Visual theme definitions for the Star Board Game.

This module contains ONLY color / style dictionaries.
No game logic and no Tkinter widgets belong here.

The GUI imports:
    THEMES
    DEFAULT_THEME_NAME
"""

from __future__ import annotations

from typing import Dict, Any

from config import (
    BG_COLOR,
    STAR_COLOR,
    TEXT_COLOR,
    POSITIVE_COLOR,
    NEGATIVE_COLOR,
    ZERO_COLOR,
    STAR_CELL_COLOR,
    EMPTY_CELL_COLOR,
)


# Each theme is a dictionary of visual attributes.
# gui/app.py will pick a theme and read values from it.

THEMES: Dict[str, Dict[str, Any]] = {
    "Dark": {
        "bg": BG_COLOR,
        "panel_bg": BG_COLOR,
        "header_text": TEXT_COLOR,
        "text": TEXT_COLOR,
        "star": STAR_COLOR,

        "pos_text": POSITIVE_COLOR,
        "neg_text": NEGATIVE_COLOR,
        "zero_text": ZERO_COLOR,

        "star_cell": STAR_CELL_COLOR,
        "empty_cell": EMPTY_CELL_COLOR,

        "hover_bg": "#2b3350",

        "log_bg": "#101522",
        "log_text": "#e0e6ff",
        "bot_move_text": "#9ca5ff",

        "star_flash": "#ffd966",
    },

    "Retro": {
        "bg": "#f4ecd8",
        "panel_bg": "#f4ecd8",
        "header_text": "#2b1c0f",
        "text": "#2b1c0f",
        "star": "#c0392b",

        "pos_text": "#116530",
        "neg_text": "#8e201b",
        "zero_text": "#555555",

        "star_cell": "#ffe8a3",
        "empty_cell": "#f7f0df",

        "hover_bg": "#ffe9c6",

        "log_bg": "#f7f0df",
        "log_text": "#2b1c0f",
        "bot_move_text": "#8e201b",

        "star_flash": "#ffe066",
    },
}

DEFAULT_THEME_NAME: str = "Dark"
