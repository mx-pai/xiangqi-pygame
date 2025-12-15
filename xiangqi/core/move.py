from __future__ import annotations
from dataclasses import dataclass
from .const import i_to_rc, rc_to_i

@dataclass(frozen=True, slots=True)
class Move:
    """一个走法：from -> to，记录被吃子，用于撤销。"""
    frm: int
    to: int
    captured: int = 0

    def __str__(self) -> str:
        return f"Move({i_to_rc(self.frm)}->{i_to_rc(self.to)}, cap={self.captured})"
