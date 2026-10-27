# Star & Numbers

A two-player strategy game on a 9×9 grid of numbers. Players take turns picking numbers from the star's row or column. Each pick moves the star, which decides what your opponent can pick next.

Play against a friend on the same computer, or against a greedy bot.

## How to play

**The board**
- 9×9 grid of whole numbers from **-10** to **15**.
- **-10**, **10** and **15** each appear exactly once, in random places.
- Every other cell is random and usually close to 0 (normal distribution, mean 0, SD 4).
- The star starts on the empty center cell.

**Turns**
- **Player 1** picks any number in the star's **column**.
- **Player 2** picks any number in the star's **row**.
- You score the value you pick (negative numbers lower your score). That cell becomes empty and the star moves onto it.

**Ending**
- If the line you must pick from has no numbers left, your turn is skipped.
- When both players are stuck, the game ends. The higher score wins, and equal scores are a tie.

**Strategy:** every pick also chooses the line your opponent must play from. A big number is less useful if it gives your opponent a line with the 15 in it.

## Features

- Clickable board with labeled cells: rows **A–I**, columns **1–9**. Cells you can pick are highlighted.
- **Vs Greedy Bot** mode (the bot is Player 2) or **2 Players** on one computer.
- Event log of every move, skipped turn and result.
- Dark, Light and Neon themes.

## Requirements

- Python 3.9+
- Tkinter, which comes with the standard Python installers for Windows and macOS. On Linux, install it with your package manager, e.g. `sudo apt install python3-tk`.

No other packages are needed to play.

## Install and run

```bash
git clone https://github.com/omrilidor/star-and-numbers.git
cd star-and-numbers

python -m venv venv
# Windows:      venv\Scripts\activate
# macOS/Linux:  source venv/bin/activate

pip install -e .
star-and-numbers          # or: python -m star_and_numbers
```

## Development

```bash
pip install -e ".[dev]"
pytest
```

### Project layout

```
star-and-numbers/
├── pyproject.toml          # package metadata, entry point, pytest config
├── src/star_and_numbers/
│   ├── __main__.py         # entry point (python -m star_and_numbers)
│   ├── config.py           # GameConfig: board size, values, rules
│   ├── board.py            # random board generation
│   ├── engine.py           # game rules: legal moves, scoring, skips, game over
│   ├── ai.py               # bot strategies (greedy)
│   └── gui/
│       ├── app.py          # Tkinter interface
│       └── themes.py       # color themes
└── tests/                  # pytest suite for board, engine and bot
```

The game logic (`config`, `board`, `engine`, `ai`) doesn't depend on Tkinter. The GUI only displays the state and passes clicks to the engine.

### Extending

- **Rules:** create a `GameConfig` with different values, e.g. `GameConfig(size=7, mandatory_values=(-5, 20))`.
- **New bot:** write a function that takes a `GameState` and returns a `(row, col)` move, then return it from `get_bot_move` in `ai.py`.
- **New theme:** add an entry to `THEMES` in `gui/themes.py` that defines every key listed in `THEME_KEYS`.
