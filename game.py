import tkinter as tk
from tkinter import messagebox

# Unicode chess pieces for rendering (white and black)
PIECE_UNICODE = {
    'wK': '\u2654',
    'wQ': '\u2655',
    'wR': '\u2656',
    'wB': '\u2657',
    'wN': '\u2658',
    'wP': '\u2659',
    'bK': '\u265A',
    'bQ': '\u265B',
    'bR': '\u265C',
    'bB': '\u265D',
    'bN': '\u265E',
    'bP': '\u265F'
}

class ChessGame:
    def __init__(self):
        # Board is 8x8 array; each square is either '' or piece code like 'wK', 'bP'
        self.reset_board()
        self.white_to_move = True
        self.move_log = []
        self.selected_square = None  # Selected coordinates (row, col)
        self.legal_moves = []
        self.in_check = False
        self.game_over = False
        self.check_mate = False
        self.stale_mate = False

    def reset_board(self):
        # Set board to initial chess position
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bP'] * 8,
            [''] * 8,
            [''] * 8,
            [''] * 8,
            [''] * 8,
            ['wP'] * 8,
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        ]

    def get_piece(self, row, col):
        return self.board[row][col]

    def is_white(self, piece):
        return piece.startswith('w')

    def is_black(self, piece):
        return piece.startswith('b')

    def opposite_color(self):
        return 'w' if not self.white_to_move else 'b'

    def location_under_attack(self, r, c, attacker_color):
        # Check if square (r,c) is attacked by any piece of attacker_color
        # We will generate all moves for attacker_color and see if any target (r,c)
        enemy_moves = self.all_moves(attacker_color)
        for move in enemy_moves:
            if move[2] == r and move[3] == c:
                return True
        return False

    def all_moves(self, color):
        # Generate all pseudo-legal moves for the given color (not checking for checks)
        moves = []
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p != '' and p.startswith(color):
                    moves.extend(self.piece_moves(r, c, p))
        return moves

    def piece_moves(self, r, c, piece):
        # Returns list of moves (r1,c1,r2,c2)
        moves = []
        color = piece[0]
        p_type = piece[1]

        directions = []
        if p_type == 'P':  # pawn
            moves.extend(self.pawn_moves(r, c, color))
        elif p_type == 'R':  # rook
            directions = [(1,0), (-1,0), (0,1), (0,-1)]
            moves.extend(self.sliding_moves(r, c, color, directions))
        elif p_type == 'B':  # bishop
            directions = [(1,1), (1,-1), (-1,1), (-1,-1)]
            moves.extend(self.sliding_moves(r, c, color, directions))
        elif p_type == 'Q':  # queen
            directions = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]
            moves.extend(self.sliding_moves(r, c, color, directions))
        elif p_type == 'N':  # knight
            knight_jumps = [(2,1), (2,-1), (-2,1), (-2,-1), (1,2), (1,-2), (-1,2), (-1,-2)]
            for dr, dc in knight_jumps:
                rr, cc = r + dr, c + dc
                if 0 <= rr < 8 and 0 <= cc < 8:
                    target = self.board[rr][cc]
                    if target == '' or target[0] != color:
                        moves.append((r, c, rr, cc))
        elif p_type == 'K':  # king
            king_moves = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]
            for dr, dc in king_moves:
                rr, cc = r + dr, c + dc
                if 0 <= rr < 8 and 0 <= cc < 8:
                    target = self.board[rr][cc]
                    if target == '' or target[0] != color:
                        moves.append((r, c, rr, cc))
            # Castling omitted for simplicity
        return moves

    def sliding_moves(self, r, c, color, directions):
        moves = []
        for dr, dc in directions:
            rr, cc = r + dr, c + dc
            while 0 <= rr < 8 and 0 <= cc < 8:
                target = self.board[rr][cc]
                if target == '':
                    moves.append((r, c, rr, cc))
                else:
                    if target[0] != color:
                        moves.append((r, c, rr, cc))
                    break
                rr += dr
                cc += dc
        return moves

    def pawn_moves(self, r, c, color):
        moves = []
        dir = -1 if color == 'w' else 1
        start_row = 6 if color == 'w' else 1
        # 1 step forward
        if self.board[r+dir][c] == '':
            moves.append((r, c, r+dir, c))
            # 2 steps forward
            if r == start_row and self.board[r+2*dir][c] == '':
                moves.append((r, c, r+2*dir, c))
        # Captures
        for dc in [-1, 1]:
            cc = c + dc
            rr = r + dir
            if 0 <= cc < 8 and 0 <= rr < 8:
                target = self.board[rr][cc]
                if target != '' and target[0] != color:
                    moves.append((r, c, rr, cc))
        # Promotion omitted for simplicity (auto promotes to queen)
        return moves

    def make_move(self, r1, c1, r2, c2):
        # Move piece and update state if move is legal
        if self.game_over:
            return False
        move = (r1, c1, r2, c2)
        legal_moves = self.get_legal_moves()
        if move not in legal_moves:
            return False
        piece = self.board[r1][c1]
        self.board[r2][c2] = piece
        self.board[r1][c1] = ''
        self.white_to_move = not self.white_to_move
        self.move_log.append(move)
        # Check for game over conditions
        self.update_game_status()
        return True

    def update_game_status(self):
        self.in_check = self.king_in_check(self.white_to_move)
        legal_moves = self.get_legal_moves()
        if self.in_check and len(legal_moves) == 0:
            self.game_over = True
            self.check_mate = True
        elif not self.in_check and len(legal_moves) == 0:
            self.game_over = True
            self.stale_mate = True
        else:
            self.game_over = False
            self.check_mate = False
            self.stale_mate = False

    def king_in_check(self, white):
        # Find king position
        king = 'wK' if white else 'bK'
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == king:
                    king_row, king_col = r, c
        # Opposite color attacker
        attacker_color = 'b' if white else 'w'
        return self.location_under_attack(king_row, king_col, attacker_color)

    def get_legal_moves(self):
        # From all pseudo-legal moves, filter out those that leave own king in check
        color = 'w' if self.white_to_move else 'b'
        moves = []
        for move in self.all_moves(color):
            r1, c1, r2, c2 = move
            # Make move on copy
            temp_board = [row[:] for row in self.board]
            temp_board[r2][c2] = temp_board[r1][c1]
            temp_board[r1][c1] = ''
            # Check if king safe
            king_safe = self.is_king_safe_after_move(temp_board, color)
            if king_safe:
                moves.append(move)
        return moves

    def is_king_safe_after_move(self, temp_board, color):
        # Find king position
        king = color + 'K'
        king_row = king_col = None
        for r in range(8):
            for c in range(8):
                if temp_board[r][c] == king:
                    king_row, king_col = r, c
        if king_row is None:
            # King is captured (should not happen in real chess)
            return False
        # Check for attackers
        opponent = 'b' if color == 'w' else 'w'
        # Generate opponent moves on temp board
        opponent_moves = []
        for r in range(8):
            for c in range(8):
                p = temp_board[r][c]
                if p != '' and p.startswith(opponent):
                    opponent_moves.extend(self.piece_moves_on_board(temp_board, r, c, p))
        # See if king pos is attacked
        for move in opponent_moves:
            if move[2] == king_row and move[3] == king_col:
                return False
        return True

    def piece_moves_on_board(self, board, r, c, piece):
        # Like piece_moves but working on provided board array
        moves = []
        color = piece[0]
        p_type = piece[1]

        directions = []
        if p_type == 'P':  # pawn
            moves.extend(self.pawn_moves_on_board(board, r, c, color))
        elif p_type == 'R':  # rook
            directions = [(1,0), (-1,0), (0,1), (0,-1)]
            moves.extend(self.sliding_moves_on_board(board, r, c, color, directions))
        elif p_type == 'B':  # bishop
            directions = [(1,1), (1,-1), (-1,1), (-1,-1)]
            moves.extend(self.sliding_moves_on_board(board, r, c, color, directions))
        elif p_type == 'Q':  # queen
            directions = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]
            moves.extend(self.sliding_moves_on_board(board, r, c, color, directions))
        elif p_type == 'N':  # knight
            knight_jumps = [(2,1), (2,-1), (-2,1), (-2,-1), (1,2), (1,-2), (-1,2), (-1,-2)]
            for dr, dc in knight_jumps:
                rr, cc = r + dr, c + dc
                if 0 <= rr < 8 and 0 <= cc < 8:
                    target = board[rr][cc]
                    if target == '' or target[0] != color:
                        moves.append((r, c, rr, cc))
        elif p_type == 'K':  # king
            king_moves = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]
            for dr, dc in king_moves:
                rr, cc = r + dr, c + dc
                if 0 <= rr < 8 and 0 <= cc < 8:
                    target = board[rr][cc]
                    if target == '' or target[0] != color:
                        moves.append((r, c, rr, cc))
        return moves

    def sliding_moves_on_board(self, board, r, c, color, directions):
        moves = []
        for dr, dc in directions:
            rr, cc = r + dr, c + dc
            while 0 <= rr < 8 and 0 <= cc < 8:
                target = board[rr][cc]
                if target == '':
                    moves.append((r, c, rr, cc))
                else:
                    if target[0] != color:
                        moves.append((r, c, rr, cc))
                    break
                rr += dr
                cc += dc
        return moves

    def pawn_moves_on_board(self, board, r, c, color):
        moves = []
        dir = -1 if color == 'w' else 1
        start_row = 6 if color == 'w' else 1
        if 0 <= r + dir < 8:
            if board[r+dir][c] == '':
                moves.append((r, c, r+dir, c))
                if r == start_row and board[r+2*dir][c] == '':
                    moves.append((r, c, r+2*dir, c))
            for dc in [-1, 1]:
                cc = c + dc
                rr = r + dir
                if 0 <= cc < 8 and 0 <= rr < 8:
                    target = board[rr][cc]
                    if target != '' and target[0] != color:
                        moves.append((r, c, rr, cc))
        return moves

class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Chess Game")
        self.root.resizable(False, False)
        self.square_size = 64
        self.board_color_light = "#f0d9b5"
        self.board_color_dark = "#b58863"
        self.highlight_color = "#c1e1c1"
        self.selected_color = "#f7ecaa"
        self.highlight_moves_color = "#96c2ff"

        self.game = ChessGame()
        self.canvas = tk.Canvas(root, width=8*self.square_size, height=8*self.square_size)
        self.canvas.pack()

        self.status_label = tk.Label(root, text="White to move", font=("Arial", 14))
        self.status_label.pack(pady=10)

        self.restart_button = tk.Button(root, text="Restart Game", command=self.restart_game)
        self.restart_button.pack(pady=5)

        self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.selected_square = None
        self.highlighted_moves = []

        self.draw_board()
        self.draw_pieces()

    def restart_game(self):
        self.game = ChessGame()
        self.selected_square = None
        self.highlighted_moves = []
        self.update_status()
        self.draw_board()
        self.draw_pieces()

    def draw_board(self):
        self.canvas.delete("square")
        for row in range(8):
            for col in range(8):
                x1 = col * self.square_size
                y1 = row * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                color = self.board_color_light if (row+col) %2 == 0 else self.board_color_dark
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, tags="square")

    def draw_pieces(self):
        self.canvas.delete("piece")
        for r in range(8):
            for c in range(8):
                piece = self.game.board[r][c]
                if piece != '':
                    x = c * self.square_size + self.square_size//2
                    y = r * self.square_size + self.square_size//2
                    self.canvas.create_text(x, y, text=PIECE_UNICODE[piece], font=("Arial", 36), tags="piece")

    def on_canvas_click(self, event):
        if self.game.game_over:
            messagebox.showinfo("Game Over", "The game is over. Please restart to play again.")
            return
        col = event.x // self.square_size
        row = event.y // self.square_size
        if not (0 <= row < 8 and 0 <= col <8):
            return

        if self.selected_square is None:
            piece = self.game.get_piece(row, col)
            if piece == '':
                return
            if (piece.startswith('w') and self.game.white_to_move) or (piece.startswith('b') and not self.game.white_to_move):
                # Select piece and highlight legal moves
                self.selected_square = (row, col)
                self.highlighted_moves = [move for move in self.game.get_legal_moves() if move[0] == row and move[1] == col]
                self.highlight_selected_square()
        else:
            # Attempt to move selected piece to clicked square
            r1, c1 = self.selected_square
            r2, c2 = row, col
            if (r1, c1, r2, c2) in self.highlighted_moves:
                success = self.game.make_move(r1, c1, r2, c2)
                if success:
                    self.selected_square = None
                    self.highlighted_moves = []
                    self.update_status()
                    self.draw_board()
                    self.draw_pieces()
                    if self.game.game_over:
                        self.show_game_over()
                else:
                    self.selected_square = None
                    self.highlighted_moves = []
                    self.draw_board()
                    self.draw_pieces()
            else:
                # Select different piece or cancel selection
                piece = self.game.get_piece(row, col)
                turn_color = 'w' if self.game.white_to_move else 'b'
                if piece != '' and piece.startswith(turn_color):
                    self.selected_square = (row, col)
                    self.highlighted_moves = [move for move in self.game.get_legal_moves() if move[0] == row and move[1] == col]
                    self.highlight_selected_square()
                else:
                    self.selected_square = None
                    self.highlighted_moves = []
                    self.draw_board()
                    self.draw_pieces()

    def highlight_selected_square(self):
        # Redraw board, highlight selected and moves
        self.draw_board()
        self.draw_pieces()
        if self.selected_square:
            r, c = self.selected_square
            x1 = c * self.square_size
            y1 = r * self.square_size
            x2 = x1 + self.square_size
            y2 = y1 + self.square_size
            self.canvas.create_rectangle(x1, y1, x2, y2, outline=self.selected_color, width=4, tags="highlight")

        for move in self.highlighted_moves:
            r, c = move[2], move[3]
            x1 = c * self.square_size + self.square_size//3
            y1 = r * self.square_size + self.square_size//3
            x2 = x1 + self.square_size//3
            y2 = y1 + self.square_size//3
            self.canvas.create_oval(x1, y1, x2, y2, fill=self.highlight_moves_color, outline='', tags="highlight")

    def update_status(self):
        if self.game.game_over:
            if self.game.check_mate:
                winner = "Black" if self.game.white_to_move else "White"
                status = f"Checkmate! {winner} wins."
            elif self.game.stale_mate:
                status = "Stalemate! Draw."
            else:
                status = "Game over."
        else:
            turn = "White" if self.game.white_to_move else "Black"
            status = f"{turn} to move."
            if self.game.in_check:
                status += " Check!"
        self.status_label.config(text=status)

    def show_game_over(self):
        if self.game.check_mate:
            winner = "Black" if self.game.white_to_move else "White"
            messagebox.showinfo("Game Over", f"Checkmate! {winner} wins.")
        elif self.game.stale_mate:
            messagebox.showinfo("Game Over", "Stalemate! It's a draw.")
        else:
            messagebox.showinfo("Game Over", "Game is over.")

def main():
    root = tk.Tk()
    gui = ChessGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

