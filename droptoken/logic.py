# Here lives the board representation.
# The Board is only concerned with its state, token dropping and win condition checking.
# It is not concerned with turn order (it is unaware of players and whether some quit). 

class GameBoard(object):
    WINNING_RUN = 4

    def __init__(self, num_cols, num_rows):
        self.num_cols = num_cols
        self.num_rows = num_rows
        
        # board columns are mapped onto inner arrays
        # board[col][row] is how we'd access a cell
        self.board = [[None for _ in range(num_rows)] for _ in range(num_cols)]


    """
        Can this column accept more tokens?
        Input:
            column: int, column number (1-indexed)
        Return: boolean
            True - if yes
            False - if full, or column does not exist
    """
    def can_drop(self, column):
        if column <= 0 or column > self.num_cols:
            return False
        
        # if the top cell is empty, there is still capacily
        return not self.board[column-1][-1]


    """
        Drop a token into a column. NOTE: token must be truthy.
        Input:
            column: int, column number (1-indexed)
            token: an object representing a token. Something truthy that implements "==" (int or char will do)
        Return: boolean
            row - row-position of the token, if success
            None - if could not drop
    """
    def drop_token(self, column, token):
        if not self.can_drop(column):
            return None
        
        # find the first empty slot and insert token there
        for r, t in enumerate(self.board[column-1]):
            if not t:
                self.board[column - 1][r] = token
                break
        return r + 1


    """
        Check if the token at a specific position is part of a winning run of 4 (col, row or diagonals)
        Input:
            column: int, 1-indexed column position
            row: int, 1-indexed row position
        Return:
            True, if a winner
            False, if not a winner
    """
    def check_win(self, column, row):
        # shift to 0-indexing
        column -= 1
        row -= 1
        token = self.board[column][row]

        # This will scan the board in a given direction and count the longest run of tokens
        # it sees, in that direction, not counting the current one.
        # dc and dr determine direction of movement of the scanner, to calculate next step
        # E.g.: (dc, dr) = (1, 0) - to the right on this row, (dc, dr) = (0, -1) - down this column,
        #       (dc, dr) = (-1, 1) - on diagonal toward top left, etc. 
        def run_length(token, dc, dr):
            run = 0
            next_c, next_r = column + dc, row + dr
            # repeat while in bounds
            while next_c >= 0 and next_r >= 0 and next_c < self.num_cols and next_r < self.num_rows:
                if token != self.board[next_c][next_r]:
                    break
                run += 1
                next_c, next_r = next_c + dc, next_r + dr
            return run

        # check column
        run_col = run_length(token, 0, -1) + 1
        # check row
        run_row = run_length(token, -1, 0) + run_length(token, 1, 0) + 1
        # check both diagonals
        run_d1 = run_length(token, -1, -1) + run_length(token, 1, 1) + 1
        run_d2 = run_length(token, -1, 1) + run_length(token, 1, -1) + 1

        for r in [run_col, run_row, run_d1, run_d2]:
            if r >= self.WINNING_RUN:
                return True
        
        return False


    """
        Apply all moves to the board, in sequence.
        Input:
            moves: List( {'token': token, 'column': column}, ... )
        Return:
            True: all moves successfully applied
            False: something went wrong
        Side-effect:
            self.board has been updated and reflects all the moves in order.
    """
    def apply_moves(self, moves):
        success = True
        for m in moves:
            if not self.can_drop(m['column']):
                success = False
                break
            self.drop_token(m['column'], m['token'])
        return success
