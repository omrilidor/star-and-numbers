# gui/app.py

from __future__ import annotations

import tkinter as tk
from typing import Optional

from config import (
    SIZE,
    HIGHLIGHT_BRIGHTNESS,
    STAR_IMAGE_PATH,
    BOT_PLAYER_ID,
)
from engine import (
    GameConfig,
    GameState,
    create_initial_state,
    is_move_legal,
    apply_move,
    handle_no_moves_if_needed,
)
from ai import get_bot_move
from themes import THEMES, DEFAULT_THEME_NAME


class StarGameApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("9x9 Star Board Game")

        # Try loading star icon
        try:
            self.star_image = tk.PhotoImage(file=STAR_IMAGE_PATH)
        except Exception:
            self.star_image = None

        # Game engine state
        self.config = GameConfig(size=SIZE)
        self.state: Optional[GameState] = None

        # Mode selection
        self.bot_player: Optional[int] = None
        self.mode_selected: bool = False

        # Animation flag
        self.animating: bool = False

        # Bot move text
        self.last_bot_move: str = ""

        # Theme
        self.theme_name = tk.StringVar(value=DEFAULT_THEME_NAME)
        self.theme = THEMES[self.theme_name.get()]

        # Widget references
        self.root_frame: Optional[tk.Frame] = None
        self.sidebar: Optional[tk.Frame] = None
        self.board_outer: Optional[tk.Frame] = None
        self.grid_frame: Optional[tk.Frame] = None

        self.theme_menu: Optional[tk.OptionMenu] = None

        self.instructions_frame: Optional[tk.Frame] = None
        self.instructions_label: Optional[tk.Label] = None
        self.instructions_visible: bool = False

        self.label_scores: Optional[tk.Label] = None
        self.label_turn: Optional[tk.Label] = None
        self.label_legal: Optional[tk.Label] = None
        self.label_bot_move: Optional[tk.Label] = None

        self.btn_new_game: Optional[tk.Button] = None
        self.btn_vs_bot: Optional[tk.Button] = None
        self.btn_vs_human: Optional[tk.Button] = None

        self.log_title_label: Optional[tk.Label] = None
        self.log_widget: Optional[tk.Text] = None

        # Board widgets
        self.coord_labels: list[tk.Label] = []
        self.buttons: list[list[tk.Button]] = []

        self.create_widgets()
        self.apply_theme()
        self.draw()

    # ====================================================================
    # THEME HELPERS
    # ====================================================================

    def _is_light_theme(self) -> bool:
        return self.theme_name.get() == "Light"

    def _try_set_bg(self, widget: tk.Widget, bg: str) -> None:
        """
        Set background for *any* widget that supports it. (Frames, Labels, Buttons,
        OptionMenus, etc.). This is the key fix for the remaining dark patches.
        """
        try:
            widget.configure(bg=bg)
        except Exception:
            # Some widgets don't support bg; ignore safely.
            pass

    def _try_set_fg(self, widget: tk.Widget, fg: str) -> None:
        """Set foreground color if supported (Labels, Buttons, etc.)."""
        try:
            widget.configure(fg=fg)
        except Exception:
            pass

    def _set_colors_recursive(self, widget: tk.Widget, bg: str, fg: Optional[str] = None) -> None:
        """
        Recursively apply background (and optional foreground) to all descendants.
        This eliminates leftover Dark-theme frames/labels/buttons that otherwise
        keep their old color and show as "black patches".
        """
        self._try_set_bg(widget, bg)
        if fg is not None:
            self._try_set_fg(widget, fg)

        for child in widget.winfo_children():
            self._set_colors_recursive(child, bg, fg)

    # ====================================================================
    # UI BUILD
    # ====================================================================

    def create_widgets(self) -> None:
        self.root.configure(bg=self.theme["bg"])

        # Main frame
        self.root_frame = tk.Frame(self.root, bg=self.theme["bg"])
        self.root_frame.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = tk.Frame(self.root_frame, bg=self.theme["panel_bg"])
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)

        # Board outer
        self.board_outer = tk.Frame(self.root_frame, bg=self.theme["bg"])
        self.board_outer.pack(side="left", expand=True, padx=10, pady=10)

        # Title row
        title_row = tk.Frame(self.sidebar, bg=self.theme["panel_bg"])
        title_row.pack(anchor="w")

        tk.Label(
            title_row,
            text="9x9 Star Board Game",
            fg=self.theme["star"],
            bg=self.theme["panel_bg"],
            font=("Consolas", 18, "bold"),
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            title_row,
            text="Instructions",
            font=("Consolas", 9),
            command=self.toggle_instructions,
        ).pack(side="left")

        # Theme selector row
        theme_row = tk.Frame(self.sidebar, bg=self.theme["panel_bg"])
        theme_row.pack(anchor="w", pady=(6, 4))

        tk.Label(
            theme_row,
            text="Theme:",
            font=("Consolas", 9, "bold"),
            fg=self.theme["header_text"],
            bg=self.theme["panel_bg"],
        ).pack(side="left", padx=(0, 4))

        self.theme_menu = tk.OptionMenu(
            theme_row,
            self.theme_name,
            *THEMES.keys(),
            command=self.on_theme_change,
        )
        self.theme_menu.config(font=("Consolas", 9))
        self.theme_menu.pack(side="left")

        # Info labels
        tk.Label(
            self.sidebar,
            text="Player 1 → COLUMN\nPlayer 2 → ROW",
            font=("Consolas", 10),
            fg=self.theme["text"],
            bg=self.theme["panel_bg"],
            justify="left",
        ).pack(anchor="w", pady=(8, 4))

        self.label_scores = tk.Label(
            self.sidebar,
            text="Scores",
            font=("Consolas", 13, "bold"),
            fg=self.theme["text"],
            bg=self.theme["panel_bg"],
        )
        self.label_scores.pack(anchor="w", pady=3)

        self.label_turn = tk.Label(
            self.sidebar,
            text="",
            font=("Consolas", 11, "bold"),
            fg=self.theme["text"],
            bg=self.theme["panel_bg"],
        )
        self.label_turn.pack(anchor="w", pady=2)

        self.label_legal = tk.Label(
            self.sidebar,
            text="Choose a mode to begin.",
            font=("Consolas", 10),
            fg=self.theme["zero_text"],
            bg=self.theme["panel_bg"],
        )
        self.label_legal.pack(anchor="w", pady=2)

        self.label_bot_move = tk.Label(
            self.sidebar,
            text="",
            font=("Consolas", 9),
            fg=self.theme["bot_move_text"],
            bg=self.theme["panel_bg"],
        )
        self.label_bot_move.pack(anchor="w", pady=2)

        # Mode selection row
        mode_row = tk.Frame(self.sidebar, bg=self.theme["panel_bg"])
        mode_row.pack(anchor="w", pady=6)

        tk.Label(
            mode_row,
            text="Mode:",
            font=("Consolas", 10, "bold"),
            fg=self.theme["header_text"],
            bg=self.theme["panel_bg"],
        ).pack(side="left", padx=(0, 5))

        self.btn_vs_bot = tk.Button(
            mode_row,
            text="Vs Greedy Bot",
            font=("Consolas", 9),
            command=self.choose_mode_bot,
        )
        self.btn_vs_bot.pack(side="left", padx=3)

        self.btn_vs_human = tk.Button(
            mode_row,
            text="2 Players",
            font=("Consolas", 9),
            command=self.choose_mode_human,
        )
        self.btn_vs_human.pack(side="left", padx=3)

        self.btn_new_game = tk.Button(
            self.sidebar,
            text="New Game",
            font=("Consolas", 10, "bold"),
            command=self.new_game,
            state="disabled",
        )
        self.btn_new_game.pack(anchor="w", pady=(4, 8))

        # Instructions (collapsible)
        self.instructions_frame = tk.Frame(self.sidebar, bg=self.theme["panel_bg"], bd=1, relief="groove")
        instructions_text = (
            "Game Instructions:\n"
            "• Board is 9×9 with integers -10 to 15.\n"
            "• Exactly one -10, one 10, and one 15 on the board.\n"
            "• Other values are random with mean 0, SD 4.\n"
            "• The star starts in the center.\n\n"
            "Turns:\n"
            "• Player 1: pick from the star’s COLUMN.\n"
            "• Player 2: pick from the star’s ROW.\n"
            "• Vs bot: Player 2 is a greedy bot.\n\n"
            "Picking:\n"
            "• You gain that value.\n"
            "• The star moves to that square.\n"
            "• That square becomes empty.\n\n"
            "Game over:\n"
            "• A player with no moves is 'stuck'.\n"
            "• Two stuck turns in a row ends the game.\n"
            "• Highest score wins."
        )
        self.instructions_label = tk.Label(
            self.instructions_frame,
            text=instructions_text,
            font=("Consolas", 9),
            justify="left",
            bg=self.theme["panel_bg"],
            fg=self.theme["text"],
        )
        self.instructions_label.pack(padx=8, pady=8)

        # Event log
        log_frame = tk.Frame(self.sidebar, bg=self.theme["panel_bg"])
        log_frame.pack(anchor="w", pady=8, fill="x")

        self.log_title_label = tk.Label(
            log_frame,
            text="Event log:",
            font=("Consolas", 10, "bold"),
            bg=self.theme["panel_bg"],
            fg=self.theme["header_text"],
        )
        self.log_title_label.pack(anchor="w")

        self.log_widget = tk.Text(
            log_frame,
            height=12,
            width=40,
            state="disabled",
            wrap="word",
            bg=self.theme["log_bg"],
            fg=self.theme["log_text"],
        )
        self.log_widget.pack(anchor="w", fill="x", pady=(2, 0))

        # Board grid frame
        self.grid_frame = tk.Frame(self.board_outer, bg=self.theme["bg"])
        self.grid_frame.pack()
        grid = self.grid_frame

        # Column headers (tile-like in Light)
        for c in range(SIZE):
            lbl = tk.Label(
                grid,
                text=str(c + 1),
                font=("Consolas", 12, "bold"),
                fg=self.theme["header_text"],
                bg=self.theme["bg"],
                relief="raised",
                bd=2,
                padx=6,
                pady=2,
            )
            lbl.grid(row=0, column=c + 1, padx=2, pady=2)
            self.coord_labels.append(lbl)

        # Row headers (tile-like)
        for r in range(SIZE):
            lbl = tk.Label(
                grid,
                text=chr(ord("A") + r),
                font=("Consolas", 12, "bold"),
                fg=self.theme["header_text"],
                bg=self.theme["bg"],
                relief="raised",
                bd=2,
                padx=6,
                pady=2,
            )
            lbl.grid(row=r + 1, column=0, padx=2, pady=2)
            self.coord_labels.append(lbl)

        # Tile buttons
        self.buttons = []
        for r in range(SIZE):
            row_buttons = []
            for c in range(SIZE):
                btn = tk.Button(
                    grid,
                    text="",
                    width=4,
                    height=2,
                    font=("Consolas", 12),
                    command=lambda rr=r, cc=c: self.on_cell_click(rr, cc),
                    relief="raised",
                    bd=2,
                    highlightthickness=1,
                )
                btn.grid(row=r + 1, column=c + 1, padx=2, pady=2)

                btn.bind("<Enter>", self.on_cell_enter)
                btn.bind("<Leave>", self.on_cell_leave)

                btn._base_bg = self.theme["empty_cell"]  # type: ignore[attr-defined]
                row_buttons.append(btn)
            self.buttons.append(row_buttons)

    # ====================================================================
    # THEME
    # ====================================================================

    def on_theme_change(self, *_args) -> None:
        self.theme = THEMES[self.theme_name.get()]
        self.apply_theme()
        self.draw()

    def apply_theme(self) -> None:
        # Root bg
        self.root.configure(bg=self.theme["bg"])

        # IMPORTANT: recolor all widgets that support bg (Frames/Labels/Buttons/etc.)
        # This is what fixes the last remaining navy/black bars.
        if self.root_frame:
            self._set_colors_recursive(self.root_frame, self.theme["bg"])
        if self.sidebar:
            self._set_colors_recursive(self.sidebar, self.theme["panel_bg"], fg=self.theme["text"])
        if self.board_outer:
            self._set_colors_recursive(self.board_outer, self.theme["bg"])

        # Explicit important widgets
        if self.log_widget:
            self.log_widget.config(
                bg=self.theme["log_bg"],
                fg=self.theme["log_text"],
                insertbackground=self.theme["log_text"],
                selectbackground=self.theme.get("hover_bg", self.theme["log_bg"]),
                selectforeground=self.theme["log_text"],
            )

        if self.label_scores:
            self.label_scores.config(bg=self.theme["panel_bg"], fg=self.theme["text"])
        if self.label_turn:
            self.label_turn.config(bg=self.theme["panel_bg"], fg=self.theme["text"])
        if self.label_legal:
            self.label_legal.config(bg=self.theme["panel_bg"], fg=self.theme["zero_text"])
        if self.label_bot_move:
            self.label_bot_move.config(bg=self.theme["panel_bg"], fg=self.theme["bot_move_text"])

        if self.instructions_frame:
            self.instructions_frame.config(bg=self.theme["panel_bg"])
        if self.instructions_label:
            self.instructions_label.config(bg=self.theme["panel_bg"], fg=self.theme["text"])

        if self.log_title_label:
            self.log_title_label.config(bg=self.theme["panel_bg"], fg=self.theme["header_text"])

        # Coordinate headers + style switch
        for lbl in self.coord_labels:
            lbl.config(bg=self.theme["bg"], fg=self.theme["header_text"])
            if self._is_light_theme():
                lbl.config(relief="raised", bd=2)
            else:
                lbl.config(relief="flat", bd=0)

        # OptionMenu button + dropdown menu (Tk quirk)
        if self.theme_menu:
            self.theme_menu.config(
                bg=self.theme["panel_bg"],
                fg=self.theme["text"],
                activebackground=self.theme["panel_bg"],
            )
            try:
                menu = self.theme_menu["menu"]
                menu.config(bg=self.theme["panel_bg"], fg=self.theme["text"])
            except Exception:
                pass

    # ====================================================================
    # LOG
    # ====================================================================

    def clear_log(self) -> None:
        if not self.log_widget:
            return
        self.log_widget.config(state="normal")
        self.log_widget.delete("1.0", "end")
        self.log_widget.config(state="disabled")

    def log(self, msg: str) -> None:
        if not self.log_widget:
            return
        self.log_widget.config(state="normal")
        self.log_widget.insert("end", msg + "\n")
        self.log_widget.see("end")
        self.log_widget.config(state="disabled")

    # ====================================================================
    # COLOR UTILS
    # ====================================================================

    def _lighter(self, hex_color: str, factor: Optional[float] = None) -> str:
        """Treat HIGHLIGHT_BRIGHTNESS as % towards white."""
        if factor is None:
            factor = HIGHLIGHT_BRIGHTNESS
        strength = max(0.0, min(float(factor), 100.0)) / 100.0

        h = hex_color.lstrip("#")
        if len(h) != 6:
            return "#" + h

        r = int(h[0:2], 16)
        g = int(h[2:4], 16)
        b = int(h[4:6], 16)

        r = int(r + (255 - r) * strength)
        g = int(g + (255 - g) * strength)
        b = int(b + (255 - b) * strength)

        return f"#{r:02x}{g:02x}{b:02x}"

    # ====================================================================
    # MODE / NEW GAME
    # ====================================================================

    def choose_mode_bot(self) -> None:
        self.bot_player = BOT_PLAYER_ID
        self.mode_selected = True
        self._disable_mode_buttons()
        if self.btn_new_game:
            self.btn_new_game.config(state="normal")

        self._start_new_state(clear_log=True)
        self.log("New game started: Greedy Bot is Player 2.")
        self._start_turn()

    def choose_mode_human(self) -> None:
        self.bot_player = None
        self.mode_selected = True
        self._disable_mode_buttons()
        if self.btn_new_game:
            self.btn_new_game.config(state="normal")

        self._start_new_state(clear_log=True)
        self.log("New game started: 2 human players.")
        self._start_turn()

    def _disable_mode_buttons(self) -> None:
        if self.btn_vs_bot:
            self.btn_vs_bot.config(state="disabled")
        if self.btn_vs_human:
            self.btn_vs_human.config(state="disabled")

    def new_game(self) -> None:
        if not self.mode_selected:
            return

        self._start_new_state(clear_log=True)
        if self.bot_player == BOT_PLAYER_ID:
            self.log("New game (mode: vs Greedy Bot).")
        else:
            self.log("New game (mode: 2 Players).")
        self._start_turn()

    def _start_new_state(self, clear_log: bool = False) -> None:
        self.state = create_initial_state(self.config)
        self.animating = False
        self.last_bot_move = ""
        if clear_log:
            self.clear_log()
        if self.label_bot_move:
            self.label_bot_move.config(text="")

    # ====================================================================
    # INSTRUCTIONS
    # ====================================================================

    def toggle_instructions(self) -> None:
        if not self.instructions_visible:
            if self.instructions_frame:
                self.instructions_frame.pack(pady=5, fill="x")
            self.instructions_visible = True
        else:
            if self.instructions_frame:
                self.instructions_frame.pack_forget()
            self.instructions_visible = False

    # ====================================================================
    # HOVER
    # ====================================================================

    def on_cell_enter(self, event) -> None:
        btn = event.widget
        if btn["state"] == "normal":
            btn.config(bg=self.theme["hover_bg"])

    def on_cell_leave(self, event) -> None:
        btn = event.widget
        base = getattr(btn, "_base_bg", self.theme["empty_cell"])
        btn.config(bg=base)

    # ====================================================================
    # DRAW
    # ====================================================================

    def draw(self) -> None:
        state = self.state

        # Scores label
        if self.label_scores:
            if state is None:
                self.label_scores.config(text="Scores → P1: 0 | P2: 0")
            else:
                if self.bot_player == BOT_PLAYER_ID:
                    self.label_scores.config(
                        text=f"Scores → P1: {state.scores[1]} | Greedy Bot: {state.scores[2]}"
                    )
                else:
                    self.label_scores.config(
                        text=f"Scores → P1: {state.scores[1]} | P2: {state.scores[2]}"
                    )

        # Turn / winner
        if state is None or not self.mode_selected:
            if self.label_turn:
                self.label_turn.config(text="Choose a mode to begin.", fg=self.theme["text"])
        else:
            if state.game_over:
                if state.winner is None:
                    t = "Game over: tie! Click New Game to play again."
                else:
                    t = f"Game over: Player {state.winner} wins! Click New Game to play again."
                self.label_turn.config(text=t, fg=self.theme["text"])
            else:
                mode_text = "COLUMN" if state.current_player == 1 else "ROW"
                if self._is_light_theme():
                    color = self.theme.get("header_text", "#000000")
                else:
                    color = "#00E0FF" if state.current_player == 1 else "#FF80FF"
                self.label_turn.config(text=f"Player {state.current_player} → {mode_text} move", fg=color)

        # Legal/status
        if not self.mode_selected:
            self.label_legal.config(text="Choose a mode to begin.")
        elif state is None or state.game_over:
            self.label_legal.config(text="")
        else:
            if state.current_player == 1:
                self.label_legal.config(text=f"Pick from COLUMN {state.star_c + 1}.")
            else:
                self.label_legal.config(text=f"Pick from ROW {state.star_r + 1}.")

        # Bot move line
        if self.bot_player == BOT_PLAYER_ID and state is not None:
            if self.last_bot_move:
                self.label_bot_move.config(text=self.last_bot_move)
            else:
                self.label_bot_move.config(text="Bot move will be shown here.")
        else:
            self.label_bot_move.config(text="")

        # Human turn?
        human_turn = (
            self.mode_selected
            and state is not None
            and not state.game_over
            and not self.animating
            and state.current_player != self.bot_player
        )

        # No state: blank board
        if state is None:
            for r in range(SIZE):
                for c in range(SIZE):
                    btn = self.buttons[r][c]
                    bg = self.theme["empty_cell"]
                    btn._base_bg = bg  # type: ignore[attr-defined]
                    btn.config(text="", bg=bg, activebackground=bg, state="disabled", image="")
            return

        # Draw board
        for r in range(SIZE):
            for c in range(SIZE):
                btn = self.buttons[r][c]
                val = state.board[r][c]

                # Base background
                if (r, c) == (state.star_r, state.star_c):
                    bg = self.theme["star_cell"]
                else:
                    bg = self.theme["empty_cell"]

                # Highlight active row/column
                if (r, c) != (state.star_r, state.star_c) and not state.game_over:
                    if state.current_player == 1 and c == state.star_c:
                        bg = self._lighter(bg)
                    elif state.current_player == 2 and r == state.star_r:
                        bg = self._lighter(bg)

                btn._base_bg = bg  # type: ignore[attr-defined]

                # Content
                if (r, c) == (state.star_r, state.star_c):
                    if self.star_image:
                        btn.config(text="", image=self.star_image, bg=bg, activebackground=bg)
                    else:
                        btn.config(text="★", fg=self.theme["star"], bg=bg, activebackground=bg, image="")
                else:
                    if val is None:
                        btn.config(text="", bg=bg, activebackground=bg, image="")
                    else:
                        if val > 0:
                            fg = self.theme["pos_text"]
                        elif val < 0:
                            fg = self.theme["neg_text"]
                        else:
                            fg = self.theme["zero_text"]
                        btn.config(text=str(val), fg=fg, bg=bg, activebackground=bg, image="")

                # Enabled/disabled
                btn.config(state="normal" if human_turn else "disabled")

    # ====================================================================
    # BOT / HUMAN MOVES
    # ====================================================================

    def _start_turn(self) -> None:
        state = self.state
        if state is None:
            self.draw()
            return

        if state.game_over:
            self.draw()
            return

        if self.bot_player is not None and state.current_player == self.bot_player:
            self.draw()
            self.root.after(250, self.bot_move)
        else:
            self.draw()

    def bot_move(self) -> None:
        state = self.state
        if state is None or state.game_over:
            self.draw()
            return

        if self.bot_player is None or state.current_player != self.bot_player:
            self.draw()
            return

        move = get_bot_move(state)
        if move is None:
            handle_no_moves_if_needed(state)
            if state.game_over:
                self.log("Game over: tie." if state.winner is None else f"Game over: Player {state.winner} wins.")
            self.draw()
            return

        r, c, val = move
        row_letter = chr(ord("A") + r)
        col_num = c + 1

        self.last_bot_move = f"Greedy Bot chose {val:+} at {row_letter}{col_num}"
        self.log(f"Greedy Bot took {val:+} at {row_letter}{col_num}")

        apply_move(state, r, c)
        self.draw()
        self.animate_star_flash(state.star_r, state.star_c)

    def on_cell_click(self, r: int, c: int) -> None:
        state = self.state
        if state is None or not self.mode_selected or state.game_over or self.animating:
            return

        if self.bot_player is not None and state.current_player == self.bot_player:
            return

        if not is_move_legal(state, r, c):
            return

        val = state.board[r][c]
        if val is None:
            return

        row_letter = chr(ord("A") + r)
        col_num = c + 1
        self.log(f"P{state.current_player} took {val:+} at {row_letter}{col_num}")

        apply_move(state, r, c)

        if self.bot_player == BOT_PLAYER_ID:
            self.last_bot_move = ""
            if self.label_bot_move:
                self.label_bot_move.config(text="")

        self.draw()
        self.animate_star_flash(state.star_r, state.star_c)

    # ====================================================================
    # ANIMATION
    # ====================================================================

    def animate_star_flash(self, r: int, c: int, steps: int = 4) -> None:
        state = self.state
        if state is None:
            self.animating = False
            self.draw()
            return

        if steps <= 0:
            self.animating = False
            self._start_turn()
            return

        self.animating = True
        btn = self.buttons[r][c]
        current_bg = btn.cget("bg")
        new_bg = self.theme["star_flash"] if current_bg == self.theme["star_cell"] else self.theme["star_cell"]

        btn.config(bg=new_bg, activebackground=new_bg)
        btn._base_bg = new_bg  # type: ignore[attr-defined]
        self.root.after(80, lambda: self.animate_star_flash(r, c, steps - 1))
