

#!/usr/bin/env python3
# chessbot.py — CS Chess Bot v0.1 (Python 3.8+ compatible)

from datetime import datetime
from typing import Optional
import random
import sys

import chess  # pip install python-chess


BANNER = """
=====================================================
                 Chess Bot v0.1
=====================================================
"""


def ask(prompt: str) -> str:
    """Prompt user and return trimmed input. Exit cleanly if input is closed."""
    try:
        return input(prompt).strip()
    except EOFError:
        print("\nGoodbye.")
        raise SystemExit


def print_fen(board: chess.Board, prefix: str = "New FEN position:") -> None:
    """Print the board as a FEN string (single-line position snapshot)."""
    print(f"{prefix} {board.fen()}")


def parse_uci_move(board: chess.Board, text: str) -> Optional[chess.Move]:
    """
    Convert 'e2e4' (optionally with promotion like 'e7e8q') to a Move.
    Return None if invalid format or illegal in this position.
    """
    try:
        move = chess.Move.from_uci(text)
    except ValueError:
        return None
    return move if move in board.legal_moves else None


def choose_bot_move(board: chess.Board) -> Optional[chess.Move]:
    """
    Assignment policy:
      - If any capturing moves exist, choose one at random.
      - Otherwise, choose any legal move at random.
    """
    legal = list(board.legal_moves)
    if not legal:
        return None
    captures = [m for m in legal if board.is_capture(m)]
    pool = captures if captures else legal
    return random.choice(pool)


def game_over_message(board: chess.Board) -> str:
    """Human-readable reason for game end."""
    if board.is_checkmate():
        # Side to move has no legal moves and is in check -> previous mover wins
        winner = "Black" if board.turn == chess.WHITE else "White"
        return f"Checkmate. {winner} wins."
    if board.is_stalemate():
        return "Draw by stalemate."
    if board.is_insufficient_material():
        return "Draw by insufficient material."
    if board.is_seventyfive_moves():
        return "Draw by 75-move rule."
    if board.is_fivefold_repetition():
        return "Draw by fivefold repetition."
    # (50-move and threefold are claimable; we do not auto-claim in v0.1.)
    return "Game over."


def main() -> None:
    # 1) Banner + timestamp
    print(BANNER)
    print(f"Time: {datetime.now()}")

    # 2) Ask which color the BOT plays
    side = ask("Computer Player? (w=white/b=black): ").lower()
    while side not in {"w", "b"}:
        side = ask("Please enter 'w' (white) or 'b' (black): ").lower()
    bot_is_white = (side == "w")

    # 3) Optional starting FEN
    fen = ask("Starting FEN position? (hit ENTER for standard starting position): ")
    try:
        board = chess.Board(fen) if fen else chess.Board()
    except ValueError:
        print("Invalid FEN. Starting from standard position instead.")
        board = chess.Board()

    # Helper: Is it the human's turn right now?
    # If bot is white, human is black → human moves when board.turn == BLACK.
    # If bot is black, human is white → human moves when board.turn == WHITE.
    def human_turn_now() -> bool:
        return (board.turn == chess.WHITE and not bot_is_white) or \
               (board.turn == chess.BLACK and bot_is_white)

    # Show initial position
    print_fen(board, "Starting FEN position:")

    # 4) Main loop: prompt human/bot in turn, print FEN after each move
    while True:
        # Human's turn?
        if human_turn_now():
            color_name = "White" if board.turn == chess.WHITE else "Black"
            uci = ask(f"{color_name}: ").lower()
            move = parse_uci_move(board, uci)
            if move is None:
                print("Illegal or invalid move. Use UCI like e2e4 (promotion: e7e8q). Try again.")
                continue

            board.push(move)
            print_fen(board)
            if board.is_game_over():
                print(game_over_message(board))
                break
            continue

        # Bot's turn
        bot_color_name = "white" if bot_is_white else "black"
        move = choose_bot_move(board)
        if move is None:
            # No legal moves for the side to move → game is over
            print(game_over_message(board))
            break

        print(f"Bot (as {bot_color_name}): {move.uci()}")
        board.push(move)
        print_fen(board)
        if board.is_game_over():
            print(game_over_message(board))
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting.")
        sys.exit(0)


