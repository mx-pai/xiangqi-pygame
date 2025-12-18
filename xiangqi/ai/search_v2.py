from __future__ import annotations
import time
from xiangqi.core.board import Board
from xiangqi.core.move import Move
from xiangqi.core.movegen import gen_legal_moves
from xiangqi.core.const import Side, Piece
from .eval import evaluate
from .zobrist import calc_zobrist_key
from .ai_config import INF, MATE_VALUE


class SearchEngine:
    def __init__(self):
        self.nodes_count = 0
        self.best_move: Move | None = None  # 记录整次搜索的最佳走法
        self.start_time = 0
        self.time_limit = 10.0
        self.tt = {}  # 置换表放入实例中

    def _get_move_score(self, m: Move, pv_move: Move | None) -> int:

        if pv_move and m.frm == pv_move.frm and m.to == pv_move.to:
            return 1000000
        if m.captured:
            return abs(m.captured) * 10
        return 0

    def search(self, board: Board, max_depth: int = 4) -> Move | None:

        self.nodes_count = 0
        self.start_time = time.time()
        # self.best_move = None
        # self.tt.clear()

        for current_depth in range(1, max_depth + 1):
            # 1. 生成根节点走法
            moves = gen_legal_moves(board, board.side_to_move)
            if not moves:
                break

            # 2. 根节点排序
            # 优化：利用上一轮迭代找到的 self.best_move 来优化这一轮的排序
            moves.sort(key=lambda m: self._get_move_score(m, self.best_move), reverse=True)

            alpha = -INF
            beta = INF
            global_best_val = -INF
            current_iter_best_move = None

            # 3. 根节点搜索
            for mv in moves:
                board.make_move(mv)

                # 窗口反转: -beta, -alpha
                val = -self._negamax(board, current_depth - 1, -beta, -alpha)

                board.undo_move()

                # 找到更好的走法
                if val > global_best_val:
                    global_best_val = val
                    current_iter_best_move = mv

                # 更新 Alpha
                if global_best_val > alpha:
                    alpha = global_best_val

                # 超时检测
                if time.time() - self.start_time > self.time_limit:
                    break

            # 4. 打印本层结果
            elapsed = time.time() - self.start_time
            print(
                f"深度 {current_depth} 完成 | 分数: {global_best_val} | 最佳: {current_iter_best_move} | 耗时: {elapsed:.2f}s")

            # 5. 更新最终结果
            if current_iter_best_move:
                self.best_move = current_iter_best_move

            # 超时跳出迭代
            if elapsed > self.time_limit:
                break

        return self.best_move

    def _negamax(self, board: Board, depth: int, alpha: int, beta: int) -> int:
        self.nodes_count += 1

        # 1. 查置换表
        zobrist_key = calc_zobrist_key(board)
        tt_move = None

        if zobrist_key in self.tt:
            t_depth, t_score, t_flag, t_move = self.tt[zobrist_key]
            tt_move = t_move  # 提取出来用于排序

            # 如果以前算的深度够深，可以直接用结果
            if t_depth >= depth:
                if t_flag == 0:
                    return t_score
                elif t_flag == 1:
                    alpha = max(alpha, t_score)
                elif t_flag == 2:
                    beta = min(beta, t_score)

                # 如果调整后的窗口失效，说明命中剪枝
                if alpha >= beta:
                    return t_score

        # 2. 叶子节点估值
        if depth <= 0:
            val = evaluate(board)
            if board.side_to_move == Side.BLACK:
                val = -val
            return val

        # 3. 生成走法
        moves = gen_legal_moves(board, board.side_to_move)

        # 输棋/绝杀判定
        # 返回一个负的极大值，加上深度修正（死得越慢分越高）
        if not moves:
            return -MATE_VALUE + (10 - depth)

        # 4. 走法排序
        moves.sort(key=lambda m: self._get_move_score(m, tt_move), reverse=True)

        # 5. 递归搜索
        local_best_val = -INF
        local_best_move = None
        original_alpha = alpha

        for mv in moves:
            board.make_move(mv)

            val = -self._negamax(board, depth - 1, -beta, -alpha)

            board.undo_move()

            # 更新当前层最佳值
            if val > local_best_val:
                local_best_val = val
                local_best_move = mv

            # 更新 Alpha
            if val > alpha:
                alpha = val

            # Beta 剪枝
            if alpha >= beta:
                break

                #  6. 存入置换表
        tt_flag = 0  # EXACT
        if local_best_val <= original_alpha:
            tt_flag = 2  # UPPERBOUND (Fail Low): 这一层所有走法都没超过我的底线，这是一个很烂的局面
        elif local_best_val >= beta:
            tt_flag = 1  # LOWERBOUND (Fail High): 这一层有一步太好了，被剪枝了，真实值可能比这个还大

        self.tt[zobrist_key] = (depth, local_best_val, tt_flag, local_best_move)

        return local_best_val

