from __future__ import annotations
from xiangqi.core.board import Board
from xiangqi.core.const import Piece, Side, rc_to_i, i_to_rc, BOARD_ROWS, BOARD_COLS

# --- 1. 基础子价值 ---
PIECE_VALUES = {
    Piece.SHUAI: 10000,
    Piece.CHE: 900,
    Piece.PAO: 450,
    Piece.MA: 400,
    Piece.XIANG: 20,
    Piece.SHI: 20,
    Piece.BING: 10,
    Piece.EMPTY: 0
}


# 兵的位置分：过河后价值提升，靠近九宫格价值提升
#todo:对每一个子都写一份
BING_PST = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0],  # R0 (底线)
    [0, 0, 0, 0, 0, 0, 0, 0, 0],  # R1
    [0, 0, 0, 0, 0, 0, 0, 0, 0],  # R2
    [0, 0, 0, 0, 20, 0, 0, 0, 0],  # R3 (未过河)
    [0, 0, 0, 0, 20, 0, 0, 0, 0],  # R4 (未过河)
    [10, 10, 20, 30, 40, 30, 20, 10, 10],  # R5 (过河)
    [20, 30, 40, 50, 60, 50, 40, 30, 20],  # R6
    [30, 40, 50, 60, 70, 60, 50, 40, 30],  # R7
    [40, 50, 60, 70, 80, 70, 60, 50, 40],  # R8
    [50, 60, 70, 80, 80, 80, 70, 60, 50],  # R9 (沉底)
]


def _get_pst_value(piece_type: int, r: int, c: int) -> int:
    """获取位置附加分 (始终以红方视角为基准输入 r)"""
    if piece_type == Piece.BING:
        # 防止越界，虽然理论上兵不会退到底线
        if 0 <= r < 10:
            return BING_PST[r][c]
    # todo:可以继续添加 MA_PST, CHE_PST 等
    return 0


def evaluate(board: Board) -> int:
    """
    静态估值函数
    返回分值: 正数代表红方优势，负数代表黑方优势
    """
    score = 0

    for pos, piece_code in enumerate(board.squares):
        if piece_code == 0:
            continue

        ptype = abs(piece_code)
        side_val = 1 if piece_code > 0 else -1  # 红1 黑-1

        # 1. 基础分
        val = PIECE_VALUES.get(ptype, 0)

        # 2. 位置分
        r, c = i_to_rc(pos)
        if side_val == 1:
            pst_val = _get_pst_value(ptype, 9 - r, c)
        else:
            pst_val = _get_pst_value(ptype, r, c)

        val += pst_val
        score += val * side_val

    # todo:简单的机动性加分 (可选)
    # score += (len(红方合法走法) - len(黑方合法走法)) * 5

    return score