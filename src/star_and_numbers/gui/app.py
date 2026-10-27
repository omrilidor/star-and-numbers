"""Tkinter front end. All game rules live in `engine`; this module only displays and forwards clicks."""

from __future__ import annotations

import tkinter as tk
from typing import Callable, Dict, List, Optional, Tuple

from ..ai import get_bot_move
from ..config import BOT_PLAYER_ID, DEFAULT_CONFIG, GameConfig
from ..engine import GameState, MoveResult, apply_move, create_initial_state, legal_moves
from .themes import DEFAULT_THEME_NAME, THEMES, Theme

FONT = "Consolas"
BOT_DELAY_MS = 400
FLASH_STEPS = 4
FLASH_INTERVAL_MS = 80


def row_name(r: int) -> str:
    return chr(ord("A") + r)


def cell_name(r: int, c: int) -> str:
    return f"{row_name(r)}{c + 1}"


class StarGameApp:
    def __init__(self, root: tk.Tk, config: GameConfig = DEFAULT_CONFIG) -> None:
        self.root = root
        self.root.title("Star & Numbers")
        self.config = config

        self.state: Optional[GameState] = None
        self.bot_player: Optional[int] = None  # None = two human players
        self.animating = False
        self.last_bot_move = ""
        # Bumped on every new game so callbacks scheduled for an old game are ignored
        self._game_id = 0

        self.theme_name = tk.StringVar(value=DEFAULT_THEME_NAME)
        # Widgets recolored on theme change: (widget, {tk option: theme key})
        self._styled: List[Tuple[tk.Widget, Dict[str, str]]] = []
        self.instructions_visible = False

        self._build_widgets()
        self.apply_theme()
        self.draw()

    @property
    def theme(self) -> Theme:
        return THEMES[self.theme_name.get()]

    # ==================================================================
    # UI BUILD
    # ==================================================================

    def _style(self, widget: tk.Widget, **options: str) -> tk.Widget:
        """Register a widget to be recolored by apply_theme()."""
        self._styled.append((widget, options))
        return widget

    def _frame(self, parent: tk.Widget, bg: str = "panel_bg", **kw) -> tk.Frame:
        return self._style(tk.Frame(parent, **kw), bg=bg)  # type: ignore[return-value]

    def _label(self, parent: tk.Widget, fg: str = "text", bg: str = "panel_bg", **kw) -> tk.Label:
        kw.setdefault("font", (FONT, 10))
        return self._style(tk.Label(parent, **kw), fg=fg, bg=bg)  # type: ignore[return-value]

    def _button(self, parent: tk.Widget, text: str, command: Callable[[], None], **kw) -> tk.Button:
        kw.setdefault("font", (FONT, 9))
        btn = tk.Button(parent, text=text, command=command, **kw)
        return self._style(  # type: ignore[return-value]
            btn, bg="panel_bg", fg="text", activebackground="hover_bg", activeforeground="text"
        )

    def _build_widgets(self) -> None:
        self.root_frame = self._frame(self.root, bg="bg")
        self.root_frame.pack(fill="both", expand=True)

        self.sidebar = self._frame(self.root_frame)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)

        board_outer = self._frame(self.root_frame, bg="bg")
        board_outer.pack(side="left", expand=True, padx=10, pady=10)

        self._build_sidebar()
        self._build_board(board_outer)

    def _build_sidebar(self) -> None:
        sb = self.sidebar

        title_row = self._frame(sb)
        title_row.pack(anchor="w")
        self._label(title_row, text="Star & Numbers", fg="star", font=(FONT, 18, "bold")).pack(
            side="left", padx=(0, 8)
        )
        self._button(title_row, "Instructions", self.toggle_instructions).pack(side="left")

        theme_row = self._frame(sb)
        theme_row.pack(anchor="w", pady=(6, 4))
        self._label(theme_row, text="Theme:", fg="header_text", font=(FONT, 9, "bold")).pack(
            side="left", padx=(0, 4)
        )
        self.theme_menu = tk.OptionMenu(theme_row, self.theme_name, *THEMES, command=self.on_theme_change)
        self.theme_menu.config(font=(FONT, 9), highlightthickness=0)
        self._style(self.theme_menu, bg="panel_bg", fg="text", activebackground="hover_bg", activeforeground="text")
        self._style(self.theme_menu["menu"], bg="panel_bg", fg="text")
        self.theme_menu.pack(side="left")

        self._label(sb, text="Player 1 → picks from COLUMN\nPlayer 2 → picks from ROW", justify="left").pack(
            anchor="w", pady=(8, 4)
        )

        self.label_scores = self._label(sb, font=(FONT, 13, "bold"))
        self.label_scores.pack(anchor="w", pady=3)

        self.label_turn = self._label(sb, font=(FONT, 11, "bold"))
        self.label_turn.pack(anchor="w", pady=2)

        self.label_status = self._label(sb, fg="muted_text")
        self.label_status.pack(anchor="w", pady=2)

        self.label_bot_move = self._label(sb, fg="bot_move_text", font=(FONT, 9))
        self.label_bot_move.pack(anchor="w", pady=2)

        mode_row = self._frame(sb)
        mode_row.pack(anchor="w", pady=6)
        self._label(mode_row, text="New game:", fg="header_text", font=(FONT, 10, "bold")).pack(
            side="left", padx=(0, 5)
        )
        self.btn_vs_bot = self._button(mode_row, "Vs Greedy Bot", lambda: self.start_game(BOT_PLAYER_ID))
        self.btn_vs_bot.pack(side="left", padx=3)
        self.btn_vs_human = self._button(mode_row, "2 Players", lambda: self.start_game(None))
        self.btn_vs_human.pack(side="left", padx=3)

        self.btn_restart = self._button(
            sb, "Restart (same mode)", self.restart, font=(FONT, 10, "bold"), state="disabled"
        )
        self.btn_restart.pack(anchor="w", pady=(4, 8))

        self.instructions_frame = self._frame(sb, bd=1, relief="groove")
        self._label(
            self.instructions_frame, text=self._instructions_text(), font=(FONT, 9), justify="left"
        ).pack(padx=8, pady=8)

        self.log_frame = self._frame(sb)
        self.log_frame.pack(anchor="w", pady=8, fill="x")
        self._label(self.log_frame, text="Event log:", fg="header_text", font=(FONT, 10, "bold")).pack(anchor="w")
        self.log_widget = tk.Text(self.log_frame, height=12, width=44, state="disabled", wrap="word")
        self._style(
            self.log_widget,
            bg="log_bg",
            fg="log_text",
            insertbackground="log_text",
            selectbackground="hover_bg",
            selectforeground="log_text",
        )
        self.log_widget.pack(anchor="w", fill="x", pady=(2, 0))

    def _instructions_text(self) -> str:
        cfg = self.config
        mandatory = ", ".join(str(v) for v in cfg.mandatory_values)
        return (
            "Board:\n"
            f"• {cfg.size}×{cfg.size} grid of integers {cfg.value_min} to {cfg.value_max}.\n"
            f"• Exactly one each of: {mandatory}.\n"
            f"• Other values: random, mean {cfg.value_mean:g}, SD {cfg.value_std_dev:g}.\n"
            "• The star starts on the (empty) center cell.\n\n"
            "Turns:\n"
            "• Player 1 picks a number in the star's COLUMN.\n"
            "• Player 2 picks a number in the star's ROW.\n"
            "• Vs bot: Player 2 is a greedy bot.\n\n"
            "Picking:\n"
            "• You gain that value (negatives cost you).\n"
            "• The star moves to that cell.\n"
            "• That cell becomes empty.\n\n"
            "Game over:\n"
            "• A player with no numbers in their line\n"
            "  is skipped.\n"
            "• When both players are stuck, the game ends.\n"
            "• Highest score wins."
        )

    def _build_board(self, parent: tk.Widget) -> None:
        grid = self._frame(parent, bg="bg")
        grid.pack()
        size = self.config.size

        self.coord_labels: List[tk.Label] = []
        for i in range(size):
            for text, row, col in ((str(i + 1), 0, i + 1), (row_name(i), i + 1, 0)):
                lbl = self._label(grid, fg="header_text", bg="bg", text=text, font=(FONT, 12, "bold"), padx=6, pady=2)
                lbl.grid(row=row, column=col, padx=2, pady=2)
                self.coord_labels.append(lbl)

        self.buttons: List[List[tk.Button]] = []
        self._cell_bg: Dict[tk.Button, str] = {}  # background to restore after hover
        for r in range(size):
            row_buttons = []
            for c in range(size):
                btn = tk.Button(
                    grid,
                    width=4,
                    height=2,
                    font=(FONT, 12),
                    relief="raised",
                    bd=2,
                    highlightthickness=1,
                    command=lambda rr=r, cc=c: self.on_cell_click(rr, cc),
                )
                btn.grid(row=r + 1, column=c + 1, padx=2, pady=2)
                btn.bind("<Enter>", self.on_cell_enter)
                btn.bind("<Leave>", self.on_cell_leave)
                row_buttons.append(btn)
            self.buttons.append(row_buttons)

    # ==================================================================
    # THEME
    # ==================================================================

    def on_theme_change(self, *_args) -> None:
        self.apply_theme()
        self.draw()

    def apply_theme(self) -> None:
        theme = self.theme
        self.root.configure(bg=theme["bg"])
        for widget, options in self._styled:
            widget.configure(**{opt: theme[key] for opt, key in options.items()})
        relief = theme["header_relief"]
        for lbl in self.coord_labels:
            lbl.config(relief=relief, bd=2 if relief == "raised" else 0)

    # ==================================================================
    # LOG
    # ==================================================================

    def clear_log(self) -> None:
        self.log_widget.config(state="normal")
        self.log_widget.delete("1.0", "end")
        self.log_widget.config(state="disabled")

    def log(self, msg: str) -> None:
        self.log_widget.config(state="normal")
        self.log_widget.insert("end", msg + "\n")
        self.log_widget.see("end")
        self.log_widget.config(state="disabled")

    # ==================================================================
    # GAME FLOW
    # ==================================================================

    def player_name(self, player: int) -> str:
        return "Greedy Bot" if player == self.bot_player else f"Player {player}"

    def start_game(self, bot_player: Optional[int]) -> None:
        self.bot_player = bot_player
        self._game_id += 1
        self.state = create_initial_state(self.config)
        self.animating = False
        self.last_bot_move = ""
        self.btn_restart.config(state="normal")
        self.btn_vs_bot.config(relief="sunken" if bot_player is not None else "raised")
        self.btn_vs_human.config(relief="sunken" if bot_player is None else "raised")

        self.clear_log()
        self.log("New game: vs Greedy Bot (you are Player 1)." if bot_player else "New game: 2 players.")
        self._next_turn()

    def restart(self) -> None:
        if self.state is not None:
            self.start_game(self.bot_player)

    def _schedule(self, delay_ms: int, callback: Callable[[], None]) -> None:
        """root.after() that is dropped if a new game starts in the meantime."""
        game_id = self._game_id

        def run() -> None:
            if game_id == self._game_id:
                callback()

        self.root.after(delay_ms, run)

    def _next_turn(self) -> None:
        self.draw()
        state = self.state
        if state is not None and not state.game_over and state.current_player == self.bot_player:
            self._schedule(BOT_DELAY_MS, self.bot_move)

    def bot_move(self) -> None:
        state = self.state
        if state is None or state.game_over or state.current_player != self.bot_player:
            return
        move = get_bot_move(state)
        if move is not None:  # the engine never hands a turn to a stuck player
            self._play(*move)

    def on_cell_click(self, r: int, c: int) -> None:
        state = self.state
        if state is None or state.game_over or self.animating or state.current_player == self.bot_player:
            return
        if (r, c) in legal_moves(state):
            self._play(r, c)

    def _play(self, r: int, c: int) -> None:
        assert self.state is not None
        result = apply_move(self.state, r, c)
        self._log_move(result)
        if result.player == self.bot_player:
            self.last_bot_move = f"Greedy Bot took {result.value:+} at {cell_name(r, c)}"
        self.draw()
        self._flash_star(r, c, FLASH_STEPS)

    def _log_move(self, result: MoveResult) -> None:
        state = self.state
        assert state is not None
        self.log(f"{self.player_name(result.player)} took {result.value:+} at {cell_name(result.r, result.c)}")
        for player in result.skipped:
            self.log(f"{self.player_name(player)} has no numbers to pick: turn skipped.")
        if result.game_over:
            s1, s2 = state.scores[1], state.scores[2]
            if state.winner is None:
                self.log(f"Game over: tie at {s1}.")
            else:
                loser = 2 if state.winner == 1 else 1
                self.log(
                    f"Game over: {self.player_name(state.winner)} wins "
                    f"{state.scores[state.winner]} to {state.scores[loser]}."
                )

    # ==================================================================
    # ANIMATION
    # ==================================================================

    def _flash_star(self, r: int, c: int, steps: int) -> None:
        if steps <= 0:
            self.animating = False
            self._next_turn()
            return
        self.animating = True
        bg = self.theme["star_flash"] if steps % 2 == 0 else self.theme["star_cell"]
        btn = self.buttons[r][c]
        btn.config(bg=bg, activebackground=bg, state="disabled")
        self._cell_bg[btn] = bg
        self._schedule(FLASH_INTERVAL_MS, lambda: self._flash_star(r, c, steps - 1))

    # ==================================================================
    # HOVER
    # ==================================================================

    def on_cell_enter(self, event: tk.Event) -> None:
        btn = event.widget
        if btn["state"] == "normal":
            btn.config(bg=self.theme["hover_bg"])

    def on_cell_leave(self, event: tk.Event) -> None:
        btn = event.widget
        btn.config(bg=self._cell_bg.get(btn, self.theme["empty_cell"]))

    # ==================================================================
    # DRAW
    # ==================================================================

    def draw(self) -> None:
        self._draw_sidebar()
        self._draw_board()

    def _draw_sidebar(self) -> None:
        state, theme = self.state, self.theme

        if state is None:
            self.label_scores.config(text="Player 1: 0 | Player 2: 0")
            self.label_turn.config(text="Choose a mode to begin.", fg=theme["text"])
            self.label_status.config(text="")
            self.label_bot_move.config(text="")
            return

        self.label_scores.config(
            text=f"{self.player_name(1)}: {state.scores[1]} | {self.player_name(2)}: {state.scores[2]}"
        )

        if state.game_over:
            if state.winner is None:
                text = "Game over: tie!"
            else:
                text = f"Game over: {self.player_name(state.winner)} wins!"
            self.label_turn.config(text=text, fg=theme["text"])
            self.label_status.config(text="Pick a mode or Restart to play again.")
        else:
            player = state.current_player
            self.label_turn.config(
                text=f"{self.player_name(player)} to move",
                fg=theme["p1_text"] if player == 1 else theme["p2_text"],
            )
            if player == 1:
                self.label_status.config(text=f"Pick from column {state.star_c + 1}.")
            else:
                self.label_status.config(text=f"Pick from row {row_name(state.star_r)}.")

        if self.bot_player is not None:
            self.label_bot_move.config(text=self.last_bot_move or "The bot's moves will show here.")
        else:
            self.label_bot_move.config(text="")

    def _draw_board(self) -> None:
        state, theme = self.state, self.theme
        size = self.config.size

        human_turn = (
            state is not None
            and not state.game_over
            and not self.animating
            and state.current_player != self.bot_player
        )
        legal = set(legal_moves(state)) if state is not None else set()

        for r in range(size):
            for c in range(size):
                btn = self.buttons[r][c]

                if state is None:
                    self._paint_cell(btn, "", theme["empty_cell"], theme["text"], enabled=False)
                    continue

                if (r, c) == (state.star_r, state.star_c):
                    self._paint_cell(btn, "★", theme["star_cell"], theme["star"], enabled=False)
                    continue

                val = state.board[r][c]
                bg = theme["highlight_cell"] if (r, c) in legal else theme["empty_cell"]
                if val is None:
                    self._paint_cell(btn, "", bg, theme["text"], enabled=False)
                else:
                    fg = theme["pos_text"] if val > 0 else theme["neg_text"] if val < 0 else theme["zero_text"]
                    self._paint_cell(btn, str(val), bg, fg, enabled=human_turn and (r, c) in legal)

    def _paint_cell(self, btn: tk.Button, text: str, bg: str, fg: str, enabled: bool) -> None:
        self._cell_bg[btn] = bg
        btn.config(
            text=text,
            bg=bg,
            activebackground=bg,
            fg=fg,
            activeforeground=fg,
            disabledforeground=fg,  # keep number colors when the cell can't be clicked
            state="normal" if enabled else "disabled",
        )

    # ==================================================================
    # INSTRUCTIONS
    # ==================================================================

    def toggle_instructions(self) -> None:
        if self.instructions_visible:
            self.instructions_frame.pack_forget()
        else:
            self.instructions_frame.pack(pady=5, fill="x", before=self.log_frame)
        self.instructions_visible = not self.instructions_visible
