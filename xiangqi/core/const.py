from __future__ import annotations
from dataclasses import dataclass
from enum import IntEnum

# 90格：r 0..9, c 0..8
BOARD_ROWS = 10
BOARD_COLS = 9
BOARD_SIZE = BOARD_ROWS * BOARD_COLS

def rc_to_i(r: int, c: int) -> int:
    return r * BOARD_COLS + c

def i_to_rc(i: int) -> tuple[int, int]:
    return divmod(i, BOARD_COLS)

class Side(IntEnum):
    RED = 1
    BLACK = -1

class Piece(IntEnum):
    EMPTY = 0
    SHUAI = 1     # 帅/将
    SHI = 2       # 仕/士
    XIANG = 3     # 相/象
    CHE = 4       # 车
    MA = 5        # 马
    PAO = 6       # 炮
    BING = 7      # 兵/卒

def side_of(piece_code: int) -> Side | None:
    if piece_code > 0:
        return Side.RED
    if piece_code < 0:
        return Side.BLACK
    return None

def type_of(piece_code: int) -> Piece:
    return Piece(abs(piece_code))

PIECE_CHAR = {
    0: "·",
    +Piece.SHUAI: "帅",
    +Piece.SHI: "仕",
    +Piece.XIANG: "相",
    +Piece.CHE: "车",
    +Piece.MA: "马",
    +Piece.PAO: "炮",
    +Piece.BING: "兵",
    -Piece.SHUAI: "将",
    -Piece.SHI: "士",
    -Piece.XIANG: "象",
    -Piece.CHE: "车",
    -Piece.MA: "马",
    -Piece.PAO: "炮",
    -Piece.BING: "卒",
}

def char_of(piece_code: int) -> str:
    return PIECE_CHAR.get(piece_code, "?")
