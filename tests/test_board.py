import random
from collections import Counter

import pytest

from star_and_numbers.board import generate_board
from star_and_numbers.config import GameConfig


@pytest.mark.parametrize("seed", range(200))
def test_default_board_rules(seed):
    cfg = GameConfig()
    board = generate_board(cfg, random.Random(seed))

    assert len(board) == cfg.size and all(len(row) == cfg.size for row in board)
    assert board[cfg.center][cfg.center] is None  # the star's starting cell

    values = [v for row in board for v in row if v is not None]
    assert len(values) == cfg.size * cfg.size - 1
    assert all(cfg.value_min <= v <= cfg.value_max for v in values)

    counts = Counter(values)
    for v in cfg.mandatory_values:
        assert counts[v] == 1


def test_board_respects_config_size():
    cfg = GameConfig(size=5, mandatory_values=(7,))
    board = generate_board(cfg, random.Random(0))
    assert len(board) == 5 and all(len(row) == 5 for row in board)
    assert board[2][2] is None


def test_same_seed_same_board():
    assert generate_board(rng=random.Random(42)) == generate_board(rng=random.Random(42))


def test_too_many_mandatory_values_rejected():
    with pytest.raises(ValueError):
        GameConfig(size=2, mandatory_values=(1, 2, 3, 4))
