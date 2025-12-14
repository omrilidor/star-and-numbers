# config.py

"""
Global configuration for the Star Board game.
This file should contain ONLY constants / simple settings – no logic.
"""

# ---------------------------------------------------------------------
# CORE GAME SETTINGS
# ---------------------------------------------------------------------

# Board size (SIZE x SIZE)
SIZE: int = 9

# Values that MUST appear exactly once each on the board
MANDATORY_VALUES = [-10, 10, 15]

# Random value distribution for the remaining cells:
# Drawn from Normal(mean, std_dev^2), then rounded & clipped.
VALUE_MEAN: float = 0.0
VALUE_STD_DEV: float = 4.0   # you said you changed SD to 4
VALUE_MIN: int = -10
VALUE_MAX: int = 15

# How many "stuck" turns in a row before the game ends
# (we currently use 2: both players stuck consecutively)
MAX_STUCK_IN_A_ROW: int = 2

# Which player is the bot in "vs bot" mode (None for no bot)
BOT_PLAYER_ID: int = 2


# ---------------------------------------------------------------------
# VISUAL SETTINGS – COLORS & THEMING BASE
# (You already had most of these; keep your existing values.)
# ---------------------------------------------------------------------

# Background color for the main window
BG_COLOR: str = "#12121f"

# Star color (text/fallback)
STAR_COLOR: str = "#ffd700"

# Default text color
TEXT_COLOR: str = "#e0e0ff"

# Number colors
POSITIVE_COLOR: str = "#7CFC00"   # positive values
NEGATIVE_COLOR: str = "#ff4d4d"   # negative values
ZERO_COLOR: str = "#a0a0b8"       # zero

# Cell background colors
STAR_CELL_COLOR: str = "#2b2940"
EMPTY_CELL_COLOR: str = "#1b1b2a"

# Brightness factor for highlighting the active row/column
# (You mentioned setting this to 30 – we store that intention here.)
HIGHLIGHT_BRIGHTNESS: float = 30.0

# Path to star icon image (optional; GUI will try to load it)
STAR_IMAGE_PATH: str = "star.png"
