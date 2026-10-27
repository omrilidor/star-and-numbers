"""
Pure game logic: state, legal moves, applying moves, turn skipping, game over.

No GUI code belongs here.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .board import Board, generate_board
from .config import DEFAULT_CONFIG, GameConfig

Cell = Tuple[int, int]


@dataclass
class GameState:
    board: Board
    star_r: int
    star_c: int
    scores: Dict[int, int] = field(default_factory=lambda: {1: 0, 2: 0})
    current_player: int = 1
    stuck_in_a_row: int = 0
    game_over: bool = False
    winner: Optional[int] = None  # None with game_over = tie
    config: GameConfig = DEFAULT_CONFIG

    def clone(self) -> "GameState":
        """Independent copy, safe to mutate (e.g. for AI lookahead)."""
        return GameState(
            board=[row[:] for row in self.board],
            star_r=self.star_r,
            star_c=self.star_c,
            scores=self.scores.copy(),
            current_player=self.current_player,
            stuck_in_a_row=self.stuck_in_a_row,
            game_over=self.game_over,
            winner=self.winner,
            config=self.config,
        )


@dataclass
class MoveResult:
    """What happened as a consequence of one move."""

    player: int
    r: int
    c: int
    value: int
    skipped: List[int] = field(default_factory=list)  # players whose turn was skipped
    game_over: bool = False


def create_initial_state(
    config: GameConfig = DEFAULT_CONFIG,
    rng: Optional[random.Random] = None,
) -> GameState:
    """Fresh game: new board, star at the center, Player 1 to move."""
    return GameState(
        board=generate_board(config, rng),
        star_r=config.center,
        star_c=config.center,
        config=config,
    )


def other_player(player: int) -> int:
    return 2 if player == 1 else 1


def legal_moves(state: GameState) -> List[Cell]:
    """
    Cells the current player may pick.

    Player 1 picks a non-empty cell in the star's column,
    Player 2 picks a non-empty cell in the star's row.
    """
    if state.game_over:
        return []

    size = state.config.size
    if state.current_player == 1:
        cells = [(r, state.star_c) for r in range(size)]
    else:
        cells = [(state.star_r, c) for c in range(size)]

    return [(r, c) for r, c in cells if state.board[r][c] is not None]


def is_move_legal(state: GameState, r: int, c: int) -> bool:
    return (r, c) in legal_moves(state)


def apply_move(state: GameState, r: int, c: int) -> MoveResult:
    """
    Apply a legal move for the current player:
    score the cell, empty it, move the star there, pass the turn
    (skipping players with no legal moves) and detect game over.
    """
    if not is_move_legal(state, r, c):
        raise ValueError(f"Illegal move at ({r}, {c})")

    value = state.board[r][c]
    assert value is not None
    player = state.current_player

    state.scores[player] += value
    state.board[r][c] = None
    state.star_r, state.star_c = r, c
    state.stuck_in_a_row = 0
    state.current_player = other_player(player)

    result = MoveResult(player=player, r=r, c=c, value=value)
    _advance_past_stuck_players(state, result)
    return result


def _advance_past_stuck_players(state: GameState, result: MoveResult) -> None:
    """Skip players with no legal moves; end the game after too many in a row."""
    while not legal_moves(state):
        state.stuck_in_a_row += 1
        if state.stuck_in_a_row >= state.config.max_stuck_in_a_row:
            _finish(state)
            result.game_over = True
            return
        result.skipped.append(state.current_player)
        state.current_player = other_player(state.current_player)


def _finish(state: GameState) -> None:
    state.game_over = True
    if state.scores[1] > state.scores[2]:
        state.winner = 1
    elif state.scores[2] > state.scores[1]:
        state.winner = 2
    else:
        state.winner = None
