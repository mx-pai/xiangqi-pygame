from .eval import evaluate
from ..core.const import Side
from ..core.rules import in_check
from ..core.movegen import gen_legal_moves
import time
from .ai_config import INF

def minimax(board, depth, alpha, beta, is_red_turn):
    if depth == 0:
        return evaluate(board)

    if is_red_turn:
        max_eval = -INF
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
        min_eval = INF
        for move in gen_legal_moves(board, Side.BLACK):
            board.make_move(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.undo_move()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def order_moves(board, moves):
    def move_score(move):
        score = 0
        if move.captured:
            score += abs(move.captured) * 10
        board.make_move(move)
        if in_check(board, Side.RED if board.side_to_move == Side.BLACK else Side.BLACK):
            score += 50
        board.undo_move()
        return score
    return sorted(moves, key=move_score, reverse=True)

def find_best_move(board, max_depth=3, time_limit=5.0):
    best_move = None
    is_red_turn = board.side_to_move == Side.RED
    start_time = time.time()

    for current_depth in range(1, max_depth + 1):
        current_iter_best_move = None
        alpha = -INF
        beta = INF
        moves = order_moves(board, gen_legal_moves(board, board.side_to_move))

        for move in moves:
            if time.time() - start_time > time_limit:
                break
            board.make_move(move)
            board_value = minimax(board, current_depth - 1, alpha, beta, not is_red_turn)
            board.undo_move()

            if is_red_turn:
                if board_value > alpha:
                    alpha = board_value
                    current_iter_best_move = move
            else:
                if board_value < beta:
                    beta = board_value
                    current_iter_best_move = move

        if current_iter_best_move is not None:
            best_move = current_iter_best_move
        best_value = alpha if is_red_turn else beta
        print(
                f"深度 {current_depth} 完成 | 分数: {best_value} | 最佳: {current_iter_best_move} | 耗时: {time.time() - start_time:.2f}s")

    return best_move