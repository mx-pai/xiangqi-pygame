from __future__ import annotations
from xiangqi.core.board import Board
from xiangqi.core.const import Piece, Side, rc_to_i, i_to_rc, BOARD_ROWS, BOARD_COLS
from .ai_config import PIECE_PER_VALUE, PIECE_VALUES_TABLE, MATE_VALUE


def _get_pst_value(piece_type: int, r: int, c: int) -> int:
    """获取位置附加分 (以红方视角为基准输入 r)"""
    if piece_type in PIECE_VALUES_TABLE:
        if 0 <= r < BOARD_ROWS and 0 <= c < BOARD_COLS:
            return PIECE_VALUES_TABLE[piece_type][r][c]
    return 0


def evaluate(board: Board) -> int:
    """
    静态估值函数
    返回分值: 正数代表红方优势，负数代表黑方优势
    """
    red_shuai = any(piece == Piece.SHUAI for piece in board.squares)
    black_shuai = any(piece == -Piece.SHUAI for piece in board.squares)
    if not red_shuai:
        return -MATE_VALUE  # 黑方胜
    if not black_shuai:
        return MATE_VALUE   # 红方胜

    score = 0
    for i in range(BOARD_ROWS * BOARD_COLS):
        piece = board.piece_at(i)
        if piece == Piece.EMPTY:
            continue
        piece_type = abs(piece)
        piece_side = Side.RED if piece > 0 else Side.BLACK
        r, c = i_to_rc(i)

        base_value = PIECE_PER_VALUE.get(piece_type, 0)
        pst_r = r if piece_side == Side.RED else (BOARD_ROWS - 1 - r)
        pst_value = _get_pst_value(piece_type, pst_r, c)

        if piece_side == Side.RED:
            score += base_value + pst_value
        else:
            score -= (base_value + pst_value)
    return score