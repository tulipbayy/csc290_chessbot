from datetime import datetime
import random
import sys
import chess  # pip install python-chess


def ask_user(message):
# prompt user and return the user input
    try:
        return input(message).strip()
    except EOFError:
        print("\n(bye)")
        raise SystemExit


def show_banner():
# shows the header banner in the beginning of the game
    print("=" * 60)
    print("        CSC 290 — Chess Bot v0.1 ")
    print("=" * 60)
    print("Started at:", datetime.now())


def choose_bot_color():
# asks the user to choose the color for bot
    ans = ask_user("Should the BOT play as White or Black? (w/b): ").lower()
    while ans not in ("w", "b"):
        ans = ask_user("Please type 'w' or 'b': ").lower()
    return ans == "w"  # True if white


def make_start_board():
# creates the starting chess board using FEN
    # optional FEN
    fen = ask_user("Enter a starting FEN or press Enter for the standard start: ")
    if fen == "":
        return chess.Board()
    try:
        return chess.Board(fen)
    except ValueError:
        print("Invalid FEN; starting from the standard setup.")
        return chess.Board()


def display_position(board, label="Position (FEN):"):
#prints the current chess board position in FEN notation
    print(label, board.fen())


def human_is_to_move(board, bot_is_white):
# figures out when it’s player’s turn
    # If bot is white -> human is black -> human to move when board.turn is BLACK
    # If bot is black -> human is white -> human to move when board.turn is WHITE
    if bot_is_white:
        return board.turn == chess.BLACK
    else:
        return board.turn == chess.WHITE


def read_human_move(board):
# interprets player’s UCI move
    text = ask_user("Your move (UCI like e2e4, or e7e8q for promotion): ").lower()
    try:
        mv = chess.Move.from_uci(text)
    except ValueError:
        return None
    return mv if mv in board.legal_moves else None


def pick_bot_move(board):
# generates a random bot move based on available moves
    all_moves = list(board.legal_moves)
    if not all_moves:
        return None
    cap = [m for m in all_moves if board.is_capture(m)]
    pool = cap if cap else all_moves
    return random.choice(pool)



def game_over_text(board):
# checks the board state and describes why the game ended
    if board.is_checkmate():
        # if checkmate, figure out who won.
        winner = "Black" if board.turn == chess.WHITE else "White"
        return f"Checkmate — {winner} wins."
    if board.is_stalemate():
        # no legal moves but not in check -> stalemate (draw)
        return "Draw — stalemate."
    if board.is_insufficient_material():
        # neither side has enough pieces to checkmate
        return "Draw — insufficient material."
    if board.is_seventyfive_moves():
        # 75 moves without a capture or pawn move -> automatic draw
        return "Draw — 75-move rule."
    if board.is_fivefold_repetition():
        # same board position repeated 5 times -> automatic draw
        return "Draw — fivefold repetition."
    # fallback if no specific condition matched
    return "Game over."


def main():
    show_banner()
    bot_is_white = choose_bot_color()
    board = make_start_board()
    display_position(board, "Starting FEN:")

# the main game loop
    while True:
        # human?
        if human_is_to_move(board, bot_is_white):
            color = "White" if board.turn == chess.WHITE else "Black"
            print(f"{color} to move (you).")
            mv = read_human_move(board)
            if mv is None:
                print("That wasn’t a legal UCI move. Try again.")
                continue
            board.push(mv)
            display_position(board)
            if board.is_game_over():
                print(game_over_text(board))
                break
            continue

        # bot
        bot_color = "White" if bot_is_white else "Black"
        mv = pick_bot_move(board)
        if mv is None:
            print(game_over_text(board))
            break
        print(f"Bot ({bot_color}) plays: {mv.uci()}")
        board.push(mv)
        display_position(board)
        if board.is_game_over():
            print(game_over_text(board))
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n(interrupted)")
        sys.exit(0)




