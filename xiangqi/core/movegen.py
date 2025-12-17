from __future__ import annotations
from .board import Board
from .move import Move
from .const import Side, Piece, type_of, side_of, i_to_rc, rc_to_i, BOARD_ROWS, BOARD_COLS
from . import rules

def gen_pseudo_legal_moves(board: Board, side: Side) -> list[Move]:
    moves: list[Move] = []
    for pos, p in board.iter_pieces(side):
        t = type_of(p)
        if t == Piece.CHE:
            moves.extend(_gen_che(board, pos, side))
        elif t == Piece.MA:
            moves.extend(_gen_ma(board, pos, side))
        elif t == Piece.PAO:
            moves.extend(_gen_pao(board, pos, side))
        elif t == Piece.BING:
            moves.extend(_gen_bing(board, pos, side))
        elif t == Piece.SHUAI:
            moves.extend(_gen_shuai(board, pos, side))
        elif t == Piece.SHI:
            moves.extend(_gen_shi(board, pos, side))
        elif t == Piece.XIANG:
            moves.extend(_gen_xiang(board, pos, side))
    return moves

def gen_legal_moves(board: Board, side: Side) -> list[Move]:
    """生成side方的所有合法走法"""
    legal: list[Move] = []
    for mv in gen_pseudo_legal_moves(board, side):
        board.make_move(mv)
        # 检查"原side是否被将军"
        if (not rules.in_check(board, side)) and (not rules.is_face_to_face(board)):
            legal.append(mv)
        board.undo_move()
    return legal

def _in_bounds(r: int, c: int) -> bool:
    return 0 <= r < BOARD_ROWS and 0 <= c < BOARD_COLS

def _in_palace(r: int, c: int, side: Side) -> bool:
    if side == Side.RED:
        return 7 <= r <= 9 and 3 <= c <= 5
    else:
        return 0 <= r <= 2 and 3 <= c <= 5

def _has_crossed_river(r: int, side: Side) -> bool:
    if side == Side.RED:
        return r < 5
    else:
        return r > 4

def _in_own_side(r: int, side: Side) -> bool:
    return (r >= 5) if side == Side.RED else (r <= 4)

def _try_add(board: Board, side: Side, frm: int, to: int, moved_piece: int, moves: list[Move]) -> bool:
    target = board.piece_at(to)
    if target == 0:
        moves.append(Move(frm, to, moved_piece=moved_piece))
        return True
    else:
        if side_of(target) != side:
            moves.append(Move(frm, to, moved_piece=moved_piece, captured=target))
        return False

def _gen_che(board: Board, pos: int, side: Side) -> list[Move]:
    moves: list[Move] = []
    piece = board.piece_at(pos)
    r, c = i_to_rc(pos)
    # 四个方向直线
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        rr, cc = r + dr, c + dc
        while _in_bounds(rr, cc):
            to = rc_to_i(rr, cc)
            if not _try_add(board, side, pos, to, piece, moves):
                break
            rr += dr
            cc += dc
    return moves

def _gen_ma(board: Board, pos: int, side: Side) -> list[Move]:
    moves: list[Move] = []
    piece = board.piece_at(pos)
    r, c = i_to_rc(pos)
    for dr, dc, lr, lc in [(-2,-1,-1,0),(-2,1,-1,0),(2,-1,1,0),(2,1,1,0),
                           (-1,-2,0,-1),(-1,2,0,1),(1,-2,0,-1),(1,2,0,1)]:
        rr, cc = r + dr, c + dc
        lr, lc = r + lr, c + lc
        if _in_bounds(rr, cc) and board.piece_at(rc_to_i(lr, lc)) == 0:
            to = rc_to_i(rr, cc)
            _try_add(board, side, pos, to, piece, moves)
    return moves

def _gen_pao(board: Board, pos: int, side: Side) -> list[Move]:
    moves: list[Move] = []
    piece = board.piece_at(pos)
    r, c = i_to_rc(pos)
    # 四个方向直线
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        rr, cc = r + dr, c + dc
        screen_found = False
        # 先照车那样走空格
        while _in_bounds(rr, cc):
            to = rc_to_i(rr, cc)
            target = board.piece_at(to)

            if not screen_found:
                if target == 0:
                    moves.append(Move(pos, to, moved_piece=piece))
                else:
                    screen_found = True # 找到炮架，准备吃子
            else:
                if target != 0:
                    if side_of(target) != side:
                        moves.append(Move(pos, to, moved_piece=piece, captured=target))
                    break
            rr += dr
            cc += dc
    return moves

def _gen_bing(board: Board, pos: int, side: Side) -> list[Move]:
    moves: list[Move] = []
    piece = board.piece_at(pos)
    r, c = i_to_rc(pos)
    forward = -1 if side == Side.RED else 1
    # 未过河
    rr, cc = r + forward, c
    if _in_bounds(rr, cc):
        to = rc_to_i(rr, cc)
        _try_add(board, side, pos, to, piece, moves)

    # 过河后可左右
    if _has_crossed_river(r, side):
        for dc in [-1, 1]:
            rr, cc = r, c + dc
            if _in_bounds(rr, cc):
                to = rc_to_i(rr, cc)
                _try_add(board, side, pos, to, piece, moves)
    return moves

def _gen_shuai(board: Board, pos: int, side: Side) -> list[Move]:
    moves: list[Move] = []
    piece = board.piece_at(pos)
    r, c = i_to_rc(pos)
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        rr, cc = r + dr, c + dc
        if _in_bounds(rr, cc) and _in_palace(rr, cc, side):
            to = rc_to_i(rr, cc)
            _try_add(board, side, pos, to, piece,moves)
    return moves

def _gen_shi(board: Board, pos: int, side: Side) -> list[Move]:
    moves: list[Move] = []
    piece = board.piece_at(pos)
    r, c = i_to_rc(pos)
    for dr, dc in [(-1,-1),(-1,1),(1,-1),(1,1)]:
        rr, cc = r + dr, c + dc
        if _in_bounds(rr, cc) and _in_palace(rr, cc, side):
            to = rc_to_i(rr, cc)
            _try_add(board, side, pos, to, piece, moves)
    return moves

def _gen_xiang(board: Board, pos: int, side: Side) -> list[Move]:
    moves: list[Move] = []
    piece = board.piece_at(pos)
    r, c = i_to_rc(pos)

    for dr, dc, lr, lc in [(-2,-2,-1,-1),(-2,2,-1,1),(2,-2,1,-1),(2,2,1,1)]:
        rr, cc = r + dr, c + dc
        lr, lc= r + lr, c + lc
        if (_in_own_side(rr, side) and _in_bounds(rr, cc) and board.piece_at(rc_to_i(lr, lc)) == 0):
            to = rc_to_i(rr, cc)
            _try_add(board, side, pos, to, piece, moves)

    return moves
