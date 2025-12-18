# TODO: Zobrist 哈希
# - 用于置换表
from __future__ import annotations
import random
from ..core.const import BOARD_SIZE, Piece, Side

_zobrist_table = [[0] * BOARD_SIZE for _ in range(15)]
_turn_key = 0

#每个子每个位置对应一个64位哈希值
def _init_zobrist():
    """初始化随机数表，只需调用一次"""
    global _turn_key
    rng = random.Random(42)

    for p_idx in range(15):
        for sq in range(BOARD_SIZE):
            _zobrist_table[p_idx][sq] = rng.getrandbits(64)

    _turn_key = rng.getrandbits(64)


_init_zobrist()


def _piece_to_idx(piece_code: int) -> int:
    """将棋子编码(-7 ~ 7) 映射到数组索引 (0 ~ 14)"""
    return piece_code + 7

#对每一份board生成唯一的指纹，同一棋盘不同side也有差异
def calc_zobrist_key(board) -> int:
    #todo:增量更新
    key = 0
    for i, p in enumerate(board.squares):
        if p != 0:
            idx = _piece_to_idx(p)
            key ^= _zobrist_table[idx][i]

    if board.side_to_move == Side.BLACK:
        key ^= _turn_key

    return key