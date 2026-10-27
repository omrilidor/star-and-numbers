"""Game rules and tunable constants."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GameConfig:
    """All rule parameters for a game. Defaults match the standard rules."""

    size: int = 9
    mandatory_values: tuple[int, ...] = (-10, 10, 15)

    # Non-mandatory cells: Normal(mean, std_dev), rounded, clipped to [min, max]
    value_mean: float = 0.0
    value_std_dev: float = 4.0
    value_min: int = -10
    value_max: int = 15

    # Consecutive "no legal move" turns that end the game (2 = both players stuck)
    max_stuck_in_a_row: int = 2

    def __post_init__(self) -> None:
        if self.size < 1:
            raise ValueError("Board size must be at least 1.")
        if len(self.mandatory_values) > self.size * self.size - 1:
            raise ValueError("Too many mandatory values for the board size.")
        if self.value_min > self.value_max:
            raise ValueError("value_min must not exceed value_max.")

    @property
    def center(self) -> int:
        return self.size // 2


DEFAULT_CONFIG = GameConfig()

# Player 2 is the bot in "vs bot" mode
BOT_PLAYER_ID: int = 2
