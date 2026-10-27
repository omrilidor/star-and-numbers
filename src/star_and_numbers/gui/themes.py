"""
Visual themes.

Every theme must define every key in THEME_KEYS.
"""

from __future__ import annotations

from typing import Dict

Theme = Dict[str, str]

THEME_KEYS = (
    "bg", "panel_bg", "header_text", "text", "muted_text",
    "star", "star_cell", "star_flash",
    "pos_text", "neg_text", "zero_text",
    "empty_cell", "highlight_cell", "hover_bg",
    "p1_text", "p2_text", "bot_move_text",
    "log_bg", "log_text",
    "header_relief",  # "raised" or "flat" for the A-I / 1-9 coordinate labels
)

THEMES: Dict[str, Theme] = {
    # Darkest theme: near-black with a blue tint
    "Dark": {
        "bg": "#010207",
        "panel_bg": "#010207",
        "header_text": "#e0e6ff",
        "text": "#e0e6ff",
        "muted_text": "#9aa3c7",
        "star": "#ffd966",
        "star_cell": "#141a33",
        "star_flash": "#ffd966",
        "pos_text": "#8cff8c",
        "neg_text": "#ff8080",
        "zero_text": "#cccccc",
        "empty_cell": "#0b0d19",
        "highlight_cell": "#1c2246",
        "hover_bg": "#2f3a75",
        "p1_text": "#00e0ff",
        "p2_text": "#ff80ff",
        "bot_move_text": "#9ca5ff",
        "log_bg": "#020309",
        "log_text": "#e0e6ff",
        "header_relief": "flat",
    },
    # Classic Minesweeper-inspired palette
    "Light": {
        "bg": "#c0c0c0",
        "panel_bg": "#c0c0c0",
        "header_text": "#000000",
        "text": "#000000",
        "muted_text": "#333333",
        "star": "#b07d00",
        "star_cell": "#ffffcc",
        "star_flash": "#ffff66",
        "pos_text": "#008000",
        "neg_text": "#d00000",
        "zero_text": "#000000",
        "empty_cell": "#e0e0e0",
        "highlight_cell": "#cfe3ff",
        "hover_bg": "#9ec5ff",
        "p1_text": "#0000c0",
        "p2_text": "#800080",
        "bot_move_text": "#444444",
        "log_bg": "#ffffff",
        "log_text": "#000000",
        "header_relief": "raised",
    },
    # Synthwave / deep space
    "Neon": {
        "bg": "#070012",
        "panel_bg": "#0b0020",
        "header_text": "#e6d8ff",
        "text": "#e6d8ff",
        "muted_text": "#b7a9ff",
        "star": "#fff27a",
        "star_cell": "#2c0060",
        "star_flash": "#39ff14",
        "pos_text": "#00e5ff",
        "neg_text": "#ff3bd4",
        "zero_text": "#b7a9ff",
        "empty_cell": "#18003a",
        "highlight_cell": "#341070",
        "hover_bg": "#5a2aa0",
        "p1_text": "#00e5ff",
        "p2_text": "#ff3bd4",
        "bot_move_text": "#7affff",
        "log_bg": "#0a0018",
        "log_text": "#e6d8ff",
        "header_relief": "flat",
    },
}

DEFAULT_THEME_NAME: str = "Dark"
