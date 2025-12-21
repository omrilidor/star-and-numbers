# themes.py

"""
Visual theme definitions for the Star Board Game.

Themes:
- Dark: modern dark UI
- Light: classic Minesweeper-inspired palette
"""

from __future__ import annotations
from typing import Dict, Any

THEMES: Dict[str, Dict[str, Any]] = {
    # ============================================================
    # DARK THEME
    # ============================================================
    "Dark": {
        "bg": "#0f1220",
        "panel_bg": "#0f1220",

        "header_text": "#e0e6ff",
        "text": "#e0e6ff",
        "star": "#ffd966",

        "pos_text": "#8cff8c",
        "neg_text": "#ff8080",
        "zero_text": "#cccccc",

        "empty_cell": "#1a1f3a",
        "star_cell": "#2a315a",

        "hover_bg": "#2b3350",

        "log_bg": "#101522",
        "log_text": "#e0e6ff",
        "bot_move_text": "#9ca5ff",

        "star_flash": "#ffd966",
    },

    # ============================================================
    # LIGHT THEME (MINESWEEPER)
    # ============================================================
    "Light": {
        # Minesweeper gray everywhere
        "bg": "#c0c0c0",
        "panel_bg": "#c0c0c0",

        # Board tiles
        "empty_cell": "#e0e0e0",

        # Text
        "header_text": "#000000",
        "text": "#000000",
        "star": "#ffd966",
        "star_cell": "#ffffcc",

        # Numbers: Minesweeper green for positives
        "pos_text": "#008000",   # ✅ green
        "neg_text": "#ff0000",   # red
        "zero_text": "#000000",

        # Hover / highlight
        "star_cell": "#ffffcc",
        "hover_bg": "#dcdcdc",


        # Log colors (change these to your taste)
        "log_bg": "#ffffff",
        "log_text": "#000000",
        "bot_move_text": "#555555",

        # Animation
        "star_flash": "#ffff66",
        "tile_light_edge": "#ffffff",
        "tile_dark_edge": "#7a7a7a",
        "tile_border": "#9a9a9a",
        "accent": "#0000ff",          # minesweeper-ish blue
        "sidebar_box_bg": "#c0c0c0",  # no dark boxes

    },
    "Neon": {
        # Backgrounds (deep space / synthwave)
        "bg": "#070012",
        "panel_bg": "#0b0020",

        # Text
        "header_text": "#e6d8ff",
        "text": "#e6d8ff",

        # Star (leave for now; just a nice accent)
        "star": "#fff27a",

        # Numbers (your request)
        "pos_text": "#00e5ff",   # neon bright light blue
        "neg_text": "#ff3bd4",   # neon pink
        "zero_text": "#b7a9ff",  # soft neon lavender

        # Cells
        "empty_cell": "#18003a",
        "star_cell": "#1b0040",

        # Hover
        "hover_bg": "#18003a",

        # Log
        "log_bg": "#0a0018",
        "log_text": "#e6d8ff",
        "bot_move_text": "#7affff",

        # Animation
        "star_flash": "#39ff14",  # neon green flash
    },

}

DEFAULT_THEME_NAME: str = "Dark"
