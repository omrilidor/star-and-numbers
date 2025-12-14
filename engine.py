# engine.py

"""
Pure game logic for the Star Board Game.

This module contains:
- GameConfig: constants needed by the engine.
- GameState: the full board state at any moment.
- All logic for applying moves, switching turns, and detecting game over.

NO GUI CODE BELONGS HERE.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple

from config import (
    SIZE,
    MAX_STUCK_IN_A_ROW,
)
from board_generator import generate_initial_board


Board = List[List[Optional[int]]]  # After the game starts, cells may become None


# ----------------------------------------------------------------------
# GAME CONFIG
# ----------------------------------------------------------------------

@dataclass
class GameConfig:
    size: int = SIZE
    max_stuck_in_a_row: int = MAX_STUCK_IN_A_ROW


# ----------------------------------------------------------------------
# GAME STATE
# ----------------------------------------------------------------------

@dataclass
class GameState:
    board: Board
    star_r: int
    star_c: int
    scores: dict = field(default_factory=lambda: {1: 0, 2: 0})
    current_player: int = 1
    stuck_in_a_row: int = 0
    game_over: bool = False
    winner: Optional[int] = None
    config: GameConfig = field(default_factory=GameConfig)

    def clone(self) -> "GameState":
        """Return a shallow clone (useful for AI testing)."""
        return GameState(
            board=[row[:] for row in self.board],
            star_r=self.star_r,
            star_c=self.star_c,
            scores=self.scores.copy(),
            current_player=self.current_player,
            stuck_in_a_row=self.stuck_in_a_row,
            game_over=self.game_over,
            winner=self.winner,
        )


# ----------------------------------------------------------------------
# INITIALIZATION
# ----------------------------------------------------------------------

def create_initial_state(config: GameConfig = GameConfig()) -> GameState:
    """
    Create a fresh GameState:
    - New generated board
    - Star starts at the center
    - Player 1 goes first (column)
    """
    board = generate_initial_board()
    center = config.size // 2
    return GameState(
        board=board,
        star_r=center,
        star_c=center,
        config=config,
    )


# ----------------------------------------------------------------------
# MOVE LOGIC
# ----------------------------------------------------------------------

def get_legal_indices(state: GameState) -> Set[int]:
    """
    Returns the set of legal row/column indices for the current player.

    Player 1: chooses from COLUMN → returns set of valid ROW indices.
    Player 2: chooses from ROW → returns set of valid COLUMN indices.
    """
    r0, c0 = state.star_r, state.star_c

    legal: Set[int] = set()

    if state.current_player == 1:
        # Player 1 picks from column c0 → return rows
        for r in range(state.config.size):
            if state.board[r][c0] is not None:
                legal.add(r)

    else:
        # Player 2 picks from row r0 → return columns
        for c in range(state.config.size):
            if state.board[r0][c] is not None:
                legal.add(c)

    return legal


def is_move_legal(state: GameState, r: int, c: int) -> bool:
    """
    A move is legal if:
    - The cell is in the correct row/column based on player
    - The cell has a number (not None)
    """
    if state.game_over:
        return False

    if state.board[r][c] is None:
        return False

    legal = get_legal_indices(state)

    if state.current_player == 1:
        return (c == state.star_c) and (r in legal)
    else:
        return (r == state.star_r) and (c in legal)


def apply_move(state: GameState, r: int, c: int) -> None:
    """
    Apply a legal move:
    - Add the cell value to the player's score
    - Set the cell to None
    - Move the star to the chosen cell
    - Advance to the next player
    - Check for game termination
    """
    if not is_move_legal(state, r, c):
        raise ValueError(f"Illegal move at ({r}, {c})")

    val = state.board[r][c]
    assert val is not None, "Legal move must target a non-empty cell"

    # Score update
    state.scores[state.current_player] += val

    # Clear the cell
    state.board[r][c] = None

    # Move star
    state.star_r = r
    state.star_c = c

    # Reset stuck counter
    state.stuck_in_a_row = 0

    # Switch player
    state.current_player = 2 if state.current_player == 1 else 1

    # Check if next player has moves
    handle_no_moves_if_needed(state)


# ----------------------------------------------------------------------
# TURN / GAME OVER LOGIC
# ----------------------------------------------------------------------

def handle_no_moves_if_needed(state: GameState) -> None:
    """
    If the newly current player has NO legal moves:
    - Increment stuck counter
    - If stuck twice in a row → game ends
    - Otherwise, skip this player and switch turn again
    """
    if state.game_over:
        return

    legal = get_legal_indices(state)

    if legal:
        return  # This player can play normally

    # Player is stuck
    state.stuck_in_a_row += 1

    if state.stuck_in_a_row >= state.config.max_stuck_in_a_row:
        # Game over! Determine winner
        state.game_over = True
        if state.scores[1] > state.scores[2]:
            state.winner = 1
        elif state.scores[2] > state.scores[1]:
            state.winner = 2
        else:
            state.winner = None  # tie
        return

    # Otherwise skip this turn
    state.current_player = 2 if state.current_player == 1 else 1

    # After skipping, check again for the new player
    handle_no_moves_if_needed(state)
