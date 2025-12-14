# ai.py

"""
AI logic for the Star Board Game.

Currently implements a simple "greedy" strategy:
- The bot always chooses the legal move with the highest value.
"""

from __future__ import annotations

from typing import Optional, Tuple

from engine import GameState, get_legal_indices


def get_greedy_move(state: GameState) -> Optional[Tuple[int, int, int]]:
    """
    Return the greedy move for the current player as (r, c, value),
    or None if there are no legal moves.

    Greedy rule:
    - Among all legal cells in the allowed row/column, pick the one with
      the maximum value.
    """
    if state.game_over:
        return None

    size = state.config.size
    r0, c0 = state.star_r, state.star_c
    legal_indices = get_legal_indices(state)

    best: Optional[Tuple[int, int, int]] = None  # (r, c, value)

    if state.current_player == 1:
        # Player 1 picks from column c0 → look over all legal rows
        for r in legal_indices:
            val = state.board[r][c0]
            if val is None:
                continue
            if best is None or val > best[2]:
                best = (r, c0, val)
    else:
        # Player 2 picks from row r0 → look over all legal columns
        for c in legal_indices:
            val = state.board[r0][c]
            if val is None:
                continue
            if best is None or val > best[2]:
                best = (r0, c, val)

    return best


def get_bot_move(state: GameState) -> Optional[Tuple[int, int, int]]:
    """
    Public entry point for the bot.

    For now, just uses the greedy strategy, but this function is here
    so we can easily swap strategies later (e.g. random, depth search, etc.).
    """
    return get_greedy_move(state)
