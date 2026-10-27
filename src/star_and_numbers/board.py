"""
Initial board generation.

- size x size grid
- The star's starting cell (the center) is empty
- Exactly one of each mandatory value, at distinct random positions
- All other cells drawn from Normal(value_mean, value_std_dev),
  rounded to an integer, clipped to [value_min, value_max] and never
  equal to a mandatory value
"""

from __future__ import annotations

import random
from typing import List, Optional

from .config import DEFAULT_CONFIG, GameConfig

Board = List[List[Optional[int]]]  # None = empty cell


def random_cell_value(config: GameConfig, rng: random.Random) -> int:
    """
    Draw a single value for a non-mandatory cell.

    Mandatory values are redrawn so they stay unique on the board
    (otherwise clipping alone would often create extra -10s).
    """
    while True:
        val = round(rng.gauss(config.value_mean, config.value_std_dev))
        val = max(config.value_min, min(config.value_max, val))
        if val not in config.mandatory_values:
            return val


def generate_board(
    config: GameConfig = DEFAULT_CONFIG,
    rng: Optional[random.Random] = None,
) -> Board:
    """Create a new board. Pass a seeded `rng` for reproducible boards."""
    rng = rng or random.Random()
    size, center = config.size, config.center

    board: Board = [[None] * size for _ in range(size)]

    # The star starts on the center cell, so it holds no value
    coords = [(r, c) for r in range(size) for c in range(size) if (r, c) != (center, center)]
    rng.shuffle(coords)

    n_mandatory = len(config.mandatory_values)
    for (r, c), value in zip(coords, config.mandatory_values):
        board[r][c] = value

    for r, c in coords[n_mandatory:]:
        board[r][c] = random_cell_value(config, rng)

    return board
