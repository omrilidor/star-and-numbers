"""
Bot strategies.

Currently a single "greedy" strategy: take the highest-valued legal cell.
"""

from __future__ import annotations

from typing import Optional

from .engine import Cell, GameState, legal_moves


def greedy_move(state: GameState) -> Optional[Cell]:
    """Highest-valued legal cell, or None if there are no legal moves."""
    moves = legal_moves(state)
    if not moves:
        return None
    return max(moves, key=lambda rc: state.board[rc[0]][rc[1]])


def get_bot_move(state: GameState) -> Optional[Cell]:
    """Entry point for the bot; swap the strategy here."""
    return greedy_move(state)
