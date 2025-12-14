# board_generator.py

"""
Board generation logic for the Star Game.

Responsible ONLY for creating the initial numeric board according to
the configuration:

- SIZE x SIZE grid
- Exactly one each of the mandatory values (e.g. -10, 10, 15)
- All other cells drawn from a normal distribution with mean VALUE_MEAN
  and standard deviation VALUE_STD_DEV, rounded to an integer and
  clipped to [VALUE_MIN, VALUE_MAX].
"""

from __future__ import annotations

import random
from typing import List

from config import (
    SIZE,
    MANDATORY_VALUES,
    VALUE_MEAN,
    VALUE_STD_DEV,
    VALUE_MIN,
    VALUE_MAX,
)


Board = List[List[int]]


def _random_cell_value() -> int:
    """
    Draw a single integer value for a non-mandatory cell.

    - Sample from Normal(VALUE_MEAN, VALUE_STD_DEV^2)
    - Round to nearest integer
    - Clip to [VALUE_MIN, VALUE_MAX]
    """
    x = random.gauss(VALUE_MEAN, VALUE_STD_DEV)  # normal distribution
    val = int(round(x))

    if val < VALUE_MIN:
        val = VALUE_MIN
    elif val > VALUE_MAX:
        val = VALUE_MAX

    return val


def generate_initial_board() -> Board:
    """
    Create a SIZE x SIZE board of integers with:

    - Exactly one of each value in MANDATORY_VALUES, placed at
      distinct random positions.
    - All other cells filled with random values from the configured
      normal distribution, rounded and clipped.

    The board contains plain integers; None is not used here.
    """

    # Start with an empty grid (we'll fill explicitly)
    board: Board = [[0 for _ in range(SIZE)] for _ in range(SIZE)]

    # All coordinates on the board
    coords = [(r, c) for r in range(SIZE) for c in range(SIZE)]
    random.shuffle(coords)

    # Reserve positions for mandatory values
    if len(MANDATORY_VALUES) > len(coords):
        raise ValueError("Too many mandatory values for the board size.")

    special_positions = coords[: len(MANDATORY_VALUES)]

    # Place each mandatory value at a distinct random coordinate
    for (r, c), value in zip(special_positions, MANDATORY_VALUES):
        board[r][c] = value

    # Fill the remaining cells with random values from the distribution
    for r, c in coords[len(MANDATORY_VALUES) :]:
        board[r][c] = _random_cell_value()

    return board
