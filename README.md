# Star & Numbers (Tkinter)

A turn-based board game on a 9×9 grid.  
Players move a star by selecting numbers from the star’s column/row and collecting points.

## Rules
- Board is 9×9 with integers in [-10, 15]
- Mandatory values: -10, 10, 15 appear exactly once each
- Other cells are generated from a clipped normal distribution (mean 0, SD 4)
- Star starts at the center
- Player 1 picks from the **star’s column**
- Player 2 picks from the **star’s row**
- Selected cell becomes empty and the star moves there
- If a player has no legal moves, their turn is skipped
- If both players are stuck consecutively, the game ends
- Highest score wins

## Features
- Tkinter GUI with clickable board
- Dark/Retro themes
- Greedy bot option
- Move/event log
- Subtle row/column highlight

## Run
```bash
python main.py
