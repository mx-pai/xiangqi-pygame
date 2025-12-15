from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
import unicodedata

from .const import (
    BOARD_SIZE, BOARD_ROWS, BOARD_COLS,
    Side, Piece, rc_to_i, i_to_rc,
    char_of, side_of
)
from .move import Move

@dataclass
class Board:
    squares: List[int] = field(default_factory=lambda: [0] * BOARD_SIZE)
    side_to_move: Side = Side.RED
    move_stack: List[Move] = field(default_factory=list)

    @staticmethod
    def initial() -> "Board":
        b = Board()
        b._setup_initial_position()
        return b

    def _setup_initial_position(self) -> None:
        """标准象棋初始局面（红在下 r=9，黑在上 r=0）"""
        s = self.squares
        # 清空
        for i in range(BOARD_SIZE):
            s[i] = 0

        # 黑方（上）
        s[rc_to_i(0, 0)] = -Piece.CHE
        s[rc_to_i(0, 1)] = -Piece.MA
        s[rc_to_i(0, 2)] = -Piece.XIANG
        s[rc_to_i(0, 3)] = -Piece.SHI
        s[rc_to_i(0, 4)] = -Piece.SHUAI
        s[rc_to_i(0, 5)] = -Piece.SHI
        s[rc_to_i(0, 6)] = -Piece.XIANG
        s[rc_to_i(0, 7)] = -Piece.MA
        s[rc_to_i(0, 8)] = -Piece.CHE
        s[rc_to_i(2, 1)] = -Piece.PAO
        s[rc_to_i(2, 7)] = -Piece.PAO
        for c in [0, 2, 4, 6, 8]:
            s[rc_to_i(3, c)] = -Piece.BING

        # 红方（下）
        s[rc_to_i(9, 0)] = +Piece.CHE
        s[rc_to_i(9, 1)] = +Piece.MA
        s[rc_to_i(9, 2)] = +Piece.XIANG
        s[rc_to_i(9, 3)] = +Piece.SHI
        s[rc_to_i(9, 4)] = +Piece.SHUAI
        s[rc_to_i(9, 5)] = +Piece.SHI
        s[rc_to_i(9, 6)] = +Piece.XIANG
        s[rc_to_i(9, 7)] = +Piece.MA
        s[rc_to_i(9, 8)] = +Piece.CHE
        s[rc_to_i(7, 1)] = +Piece.PAO
        s[rc_to_i(7, 7)] = +Piece.PAO
        for c in [0, 2, 4, 6, 8]:
            s[rc_to_i(6, c)] = +Piece.BING

        self.side_to_move = Side.RED
        self.move_stack.clear()

    def piece_at(self, idx: int) -> int:
        return self.squares[idx]

    def make_move(self, mv: Move) -> None:
        """执行走法（不检查合法性）"""
        piece = self.squares[mv.frm]
        captured = self.squares[mv.to]
        # push 带 captured 的 move（便于 undo）
        real_mv = Move(mv.frm, mv.to, captured=captured)
        self.move_stack.append(real_mv)

        self.squares[mv.to] = piece
        self.squares[mv.frm] = 0
        self.side_to_move = Side(-int(self.side_to_move))

    def undo_move(self) -> None:
        """撤销一步"""
        if not self.move_stack:
            return
        mv = self.move_stack.pop()
        piece = self.squares[mv.to]
        self.squares[mv.frm] = piece
        self.squares[mv.to] = mv.captured
        self.side_to_move = Side(-int(self.side_to_move))

    def pretty(self) -> str:
        """文本棋盘显示"""
        cell_w = 4
        lines = []

        header = "    " + "".join(
            Board._pad_center(str(c), cell_w) for c in range(BOARD_COLS)
        )
        lines.append(header)

        for r in range(BOARD_ROWS):
            row_str = "".join(
                Board._pad_center(char_of(self.squares[rc_to_i(r, c)]), cell_w) for c in range(BOARD_COLS)
            )
            lines.append(f"{Board._pad_center(str(r), 3)} {row_str}")

            if r == 4:
                mid = Board._pad_center("楚河", BOARD_COLS * cell_w // 2) + Board._pad_center("汉界", BOARD_COLS * cell_w // 2)
                lines.append(f"    {mid}")

        turn = "执帅方" if self.side_to_move == Side.RED else "执将方"
        return "\n".join(lines) + f"\n回合: {turn}"

    def iter_pieces(self, side: Side):
        for i, p in enumerate(self.squares):
            if p != 0 and side_of(p) == side:
                yield i, p

    def _wcwidth(ch: str) -> int:
        return 2 if unicodedata.east_asian_width(ch) in ('W', 'F') else 1

    def _wcswidth(s: str) -> int:
        return sum(Board._wcwidth(ch) for ch in s)

    def _pad_center(s: str, width: int) -> str:
        s = str(s)
        w = Board._wcswidth(s)
        if w >= width:
            return s
        pad = width - w
        left = pad // 2
        right = pad - left
        return " " * left + s + " " * right







