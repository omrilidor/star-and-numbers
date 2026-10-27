"""Entry point: `python -m star_and_numbers`, the `star-and-numbers` command, or run this file directly."""

import sys
import tkinter as tk
from pathlib import Path

if not __package__:
    # Run as a plain script (e.g. the editor's Run button): make the package importable
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from star_and_numbers.gui.app import StarGameApp


def main() -> None:
    root = tk.Tk()
    StarGameApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
