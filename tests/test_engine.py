import random

import pytest

from star_and_numbers.ai import greedy_move
from star_and_numbers.config import GameConfig
from star_and_numbers.engine import GameState, apply_move, create_initial_state, is_move_legal, legal_moves

CFG3 = GameConfig(size=3, mandatory_values=())


def make_state(board, star=(1, 1), player=1, config=CFG3):
    return GameState(board=board, star_r=star[0], star_c=star[1], current_player=player, config=config)


def test_player1_picks_from_column_player2_from_row():
    board = [
        [1, 2, 3],
        [4, None, 5],
        [6, 7, 8],
    ]
    state = make_state(board)
    assert sorted(legal_moves(state)) == [(0, 1), (2, 1)]

    state.current_player = 2
    assert sorted(legal_moves(state)) == [(1, 0), (1, 2)]


def test_star_cell_is_never_a_legal_move_at_start():
    state = create_initial_state(rng=random.Random(0))
    assert (state.star_r, state.star_c) not in legal_moves(state)


def test_apply_move_scores_empties_moves_star_and_passes_turn():
    board = [
        [1, 2, 3],
        [4, None, 5],
        [6, 7, 8],
    ]
    state = make_state(board)
    result = apply_move(state, 2, 1)

    assert state.scores == {1: 7, 2: 0}
    assert state.board[2][1] is None
    assert (state.star_r, state.star_c) == (2, 1)
    assert state.current_player == 2
    assert result.value == 7 and result.skipped == [] and not result.game_over


def test_illegal_move_raises():
    state = make_state([[1, 2, 3], [4, None, 5], [6, 7, 8]])
    assert not is_move_legal(state, 0, 0)  # not in the star's column
    with pytest.raises(ValueError):
        apply_move(state, 0, 0)


def test_stuck_player_is_skipped_and_reported():
    # After P1 takes (0,1), P2 must pick from row 0, which is then empty -> skipped.
    board = [
        [None, 5, None],
        [None, None, None],
        [None, 3, None],
    ]
    state = make_state(board)
    result = apply_move(state, 0, 1)

    assert result.skipped == [2]
    assert state.current_player == 1
    assert not state.game_over


def test_game_ends_when_both_players_stuck():
    board = [
        [None, 5, None],
        [None, None, None],
        [None, None, None],
    ]
    state = make_state(board)
    result = apply_move(state, 0, 1)

    assert result.game_over
    assert state.game_over and state.winner == 1
    assert legal_moves(state) == []


def test_tie():
    board = [
        [None, 5, None],
        [None, None, None],
        [None, None, None],
    ]
    state = make_state(board)
    state.scores[2] = 5
    apply_move(state, 0, 1)
    assert state.game_over and state.winner is None


def test_clone_is_independent_and_keeps_config():
    state = make_state([[1, 2, 3], [4, None, 5], [6, 7, 8]])
    copy = state.clone()
    apply_move(copy, 0, 1)
    assert state.board[0][1] == 2 and state.scores[1] == 0
    assert copy.config is state.config


@pytest.mark.parametrize("seed", range(30))
def test_full_random_games_terminate_consistently(seed):
    rng = random.Random(seed)
    state = create_initial_state(rng=rng)
    total = sum(v for row in state.board for v in row if v is not None)

    for _ in range(state.config.size ** 2):
        if state.game_over:
            break
        moves = legal_moves(state)
        assert moves, "a player with no moves must never be given the turn"
        apply_move(state, *rng.choice(moves))

    assert state.game_over
    remaining = sum(v for row in state.board for v in row if v is not None)
    assert state.scores[1] + state.scores[2] + remaining == total


def test_greedy_bot_picks_highest_legal_value():
    board = [
        [9, 1, 9],
        [-3, None, 4],
        [9, 2, 9],
    ]
    state = make_state(board, player=2)
    assert greedy_move(state) == (1, 2)


def test_greedy_bot_no_moves():
    state = make_state([[None] * 3 for _ in range(3)])
    assert greedy_move(state) is None
