from .eval import evaluate
from xiangqi.core.const import Side
from xiangqi.core.movegen import gen_legal_moves

def minimax(board, depth, alpha, beta, is_red_turn):
    if depth == 0:
        return evaluate(board)

    if is_red_turn:
        max_eval = float('-inf')
        for move in gen_legal_moves(board, Side.RED):
            board.make_move(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.undo_move()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in gen_legal_moves(board, Side.BLACK):
            board.make_move(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.undo_move()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def find_best_move(board, depth=3):
    best_move = None
    best_value = float('-inf') if board.side_to_move == Side.RED else float('inf')

    for move in gen_legal_moves(board, board.side_to_move):
        board.make_move(move)
        board_value = minimax(board, depth - 1, float('-inf'), float('inf'), board.side_to_move == Side.BLACK)
        board.undo_move()

        if board.side_to_move == Side.RED:
            if board_value > best_value:
                best_value = board_value
                best_move = move
        else:
            if board_value < best_value:
                best_value = board_value
                best_move = move

    return best_move