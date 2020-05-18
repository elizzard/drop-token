import pytest

from droptoken.logic import GameBoard

def test_create_board_with_correct_num_cols():
    game = GameBoard(5, 4)
    assert len(game.board) == 5

def test_create_board_with_correct_num_rows():
    game = GameBoard(5, 4)
    assert len(game.board[0]) == 4

def test_create_board_with_all_cells_set_to_none():
    nc, nr = 3, 2
    game = GameBoard(nc, nr)
    for c in range(nc):
        for r in range(nr):
            assert not game.board[c][r]

def test_can_drop_token_into_empty_column():
    nc, nr = 1, 3
    game = GameBoard(nc, nr)
    assert game.can_drop(1)

def test_can_drop_token_into_almost_full_column():
    nc, nr = 1, 3
    game = GameBoard(nc, nr)
    game.board[0] = [1, 1, None]
    assert game.can_drop(1)

def test_cannot_drop_token_into_full_column():
    nc, nr = 1, 3
    game = GameBoard(nc, nr)
    game.board[0] = [1, 1, 1]
    assert not game.can_drop(1)

def test_cannot_drop_token_into_nonexisting_column():
    nc, nr = 1, 3
    game = GameBoard(nc, nr)
    assert not game.can_drop(0)    

def test_can_fill_whole_board_with_tokens():
    nc, nr = 3, 2
    token = 1
    game = GameBoard(nc, nr)
    for c in range(1, nc + 1):
        for r in range(1, nr + 1):
            assert game.drop_token(c, token)

def test_dropping_token_to_nonexisting_column_fails():
    nc, nr = 2, 2
    token = 1
    game = GameBoard(nc, nr)
    assert not game.drop_token(nc + 1, token)

def test_winning_condition_detected_for_full_column():
    nc, nr = 4, 4
    token = 1
    game = GameBoard(nc, nr)
    for r in range(1, nr + 1):
        game.drop_token(1, token)
    assert game.check_win(1,4)

def test_winning_condition_detected_for_full_row_from_right_edge():
    nc, nr = 4, 4
    token = 1
    game = GameBoard(nc, nr)
    for c in range(1, nr + 1):
        game.drop_token(c, token)
    assert game.check_win(4,1)

def test_winning_condition_detected_for_full_row_rfrom_left_edge():
    nc, nr = 4, 4
    token = 1
    game = GameBoard(nc, nr)
    for c in range(1, nr + 1):
        game.drop_token(c, token)
    assert game.check_win(1,1)

def test_winning_condition_detected_for_full_row_rfrom_middle():
    nc, nr = 4, 4
    token = 1
    game = GameBoard(nc, nr)
    for c in range(1, nr + 1):
        game.drop_token(c, token)
    assert game.check_win(2,1)

def test_winning_condition_detected_for_main_diagonal_from_top():
    nc, nr = 4, 4
    game = GameBoard(nc, nr)
    game.board = [
        [2, 2, 2, 0],
        [1, 2, 0, 0],
        [1, 1, 2, 0],
        [1, 1, 1, 2]
    ]
    assert game.check_win(4,4)

def test_winning_condition_detected_for_main_diagonal_from_bottom():
    nc, nr = 4, 4
    game = GameBoard(nc, nr)
    game.board = [
        [2, 2, 2, 0],
        [1, 2, 0, 0],
        [1, 1, 2, 0],
        [1, 1, 1, 2]
    ]
    assert game.check_win(1,1)

def test_winning_condition_detected_for_main_diagonal_from_mid():
    nc, nr = 4, 4
    game = GameBoard(nc, nr)
    game.board = [
        [2, 2, 2, 0],
        [1, 2, 0, 0],
        [1, 1, 2, 0],
        [1, 1, 1, 2]
    ]
    assert game.check_win(3,3) 

def test_winning_condition_detected_for_secondary_diagonal_from_top():
    nc, nr = 4, 4
    game = GameBoard(nc, nr)
    game.board = [
        [2, 2, 2, 1],
        [2, 2, 1, 0],
        [2, 1, 1, 1],
        [1, 1, 0, 0]
    ]
    assert game.check_win(1,4) 

def test_winning_condition_detected_for_secondary_diagonal_from_bottom():
    nc, nr = 4, 4
    game = GameBoard(nc, nr)
    game.board = [
        [2, 2, 2, 1],
        [2, 2, 1, 1],
        [2, 1, 1, 1],
        [1, 0, 0, 0]
    ]
    assert game.check_win(4, 1) 

def test_winning_condition_detected_for_secondary_diagonal_from_mid():
    nc, nr = 4, 4
    game = GameBoard(nc, nr)
    game.board = [
        [2, 2, 2, 1],
        [2, 2, 1, 0],
        [2, 1, 1, 1],
        [1, 1, 0, 0]
    ]
    assert game.check_win(2, 3)

def test_no_win_detected():
    nc, nr = 4, 4
    game = GameBoard(nc, nr)
    game.board = [
        [2, 2, 2, 0],
        [2, 2, 1, 0],
        [2, 1, 1, 1],
        [1, 1, 1, 0]
    ]
    assert not game.check_win(4, 3)

def test_apply_all_moves_should_succeed():
    nc, nr = 4, 2
    game = GameBoard(nc, nr)
    moves = [
        {'token': 1, 'column': 4},
        {'token': 2, 'column': 1},
        {'token': 1, 'column': 1},
        {'token': 2, 'column': 3}
    ]
    expected_board = [
        [2, 1],
        [None, None],
        [2, None],
        [1, None]
    ]
    assert game.apply_moves(moves)
    assert game.board == expected_board

def test_apply_all_moves_should_fail():
    nc, nr = 3, 2
    game = GameBoard(nc, nr)
    moves = [
        {'token': 1, 'column': 4},
        {'token': 2, 'column': 1},
    ]
    assert not game.apply_moves(moves)  