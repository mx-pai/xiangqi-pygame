from xiangqi.core.board import Board
from .scenes import Scene
import pygame
from xiangqi.core.const import Side, rc_to_i, side_of, i_to_rc
from xiangqi.core.movegen import gen_legal_moves
from xiangqi.ai.search_v2 import SearchEngine
from xiangqi.ai.search import find_best_move

class PlayScene(Scene):
    def on_enter(self, **kwards):
        self.board = Board.initial() # 初始化棋盘一次即可
        self.inset = {"l":0.07, "r":0.06, "t":0.09, "b":0.10} # 棋盘内边距比例/微调过后
        self.selected = None
        self.cand_moves = []
        self.search_engine = SearchEngine()
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            rc = self.pixel_to_rc(event.pos)
            if rc is None:
                self.selected = None
                self.cand_moves = []
                return

            row, col = rc
            to = rc_to_i(row, col)
            # 调试用
            # print(f"Clicked on row={row}, col={col}")
            piece_to = self.board.squares[to]

            if self.selected is not None:
                move = next((mv for mv in self.cand_moves if mv.to == to), None)
                if move is not None:
                    self.board.make_move(move)
                    self.selected = None
                    self.cand_moves = []
                    # print(f"Made move: {move}")

                    if self.board.side_to_move == Side.BLACK:
                        black_moves = gen_legal_moves(self.board, Side.BLACK)
                        if black_moves:
                            ai_move = find_best_move(self.board, max_depth=4)
                            if ai_move is not None:
                                self.board.make_move(ai_move)
                                # print(f"AI made move: {ai_move}")
                                self.selected = None
                                self.cand_moves = []
                        else:
                            print("Black has no legal moves. Game over.")
                    return

                if piece_to == 0:
                    self.selected = None
                    self.cand_moves = []
                    return

            piece = piece_to
            if piece != 0 and side_of(piece) == self.board.side_to_move:
                frm = to
                self.selected = (row, col)
                allmoves = gen_legal_moves(self.board, self.board.side_to_move)
                self.cand_moves = [mv for mv in allmoves if mv.frm == frm] # 只保留该选中棋子的走法
                return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_z:
            if self.board.move_stack:
                self.board.undo_move()
                self.selected = None
                self.cand_moves = []

    def draw(self, screen: pygame.Surface):
        bg = self.game.assets.bg
        screen_w, screen_h = screen.get_size()
        bg_w, bg_h = bg.get_size()
        scale= max(screen_w / bg_w, screen_h / bg_h)

        new_w, new_h = int(bg_w * scale), int(bg_h * scale)
        bg_scaled = pygame.transform.smoothscale(bg, (new_w, new_h))
        bg_x, bg_y= (screen_w - new_w) // 2, (screen_h - new_h) // 2
        screen.blit(bg_scaled, (bg_x, bg_y))

        # 棋盘
        board_bg = self.game.assets.board_bg
        grid_w = int(screen_w * 0.8)
        grid_h = int(grid_w * 9 / 8)

        if grid_h > screen_h * 0.8:
            grid_h = int(screen_h * 0.8)
            grid_w = int(grid_h * 8 / 9)

        board_w = int(grid_w * 1.125)
        board_h = int(grid_h * 1.125)
        board_x = (screen_w - board_w) // 2
        board_y = (screen_h - board_h) // 2

        board_bg_scaled = pygame.transform.smoothscale(board_bg, (board_w, board_h))
        screen.blit(board_bg_scaled, (board_x, board_y))

        # 棋盘格子区域
        # 交叉点区域
        l = int(self.inset["l"] * board_w)
        r = int(self.inset["r"] * board_w)
        t = int(self.inset["t"] * board_h)
        b = int(self.inset["b"] * board_h)
        self.grid_rect = pygame.Rect(
            board_x + l,
            board_y + t,
            board_w - l - r,
            board_h - t - b
        )

        self.dx = self.grid_rect.width / 8
        self.dy = self.grid_rect.height / 9

        # 调试用 外框红色矩阵 + 棋盘绿色交叉网格点
        # pygame.draw.rect(screen, (255,0,0), self.grid_rect, 2)
        # for row in range(10):
        #     for col in range(9):
        #         x = self.grid_rect.left + col * self.dx
        #         y = self.grid_rect.top + row * self.dy
        #         pygame.draw.circle(screen, (0,255,0), (int(x), int(y)), 3)

        self.draw_pieces(screen)

    def draw_pieces(self, screen):
        piece_size = int(min(self.dx, self.dy) * 0.9)
        selected_idx = rc_to_i(*self.selected) if self.selected else None

        for row in range(10):
            for col in range(9):
                idx = rc_to_i(row, col)
                piece_code = self.board.squares[idx]
                if piece_code == 0:
                    continue
                if selected_idx is not None and idx == selected_idx:
                    continue
                x, y = self.rc_to_pixel(row, col)

                piece_img = self.game.assets.get_piece_image(piece_code)
                img_scaled = pygame.transform.smoothscale(piece_img, (piece_size, piece_size))
                rect = img_scaled.get_rect(center=(x, y))

                screen.blit(img_scaled, rect)

        self.draw_move_hints(screen)

        self.draw_selected_piece(screen, piece_size)

    def draw_move_hints(self, screen):
        dot_img = self.game.assets.dot
        dot_size = int(min(self.dx, self.dy) * 0.3)
        dot_scaled = pygame.transform.smoothscale(dot_img, (dot_size, dot_size))

        for mv in self.cand_moves:
            to_row, to_col = i_to_rc(mv.to)
            x, y = self.rc_to_pixel(to_row, to_col)
            rect = dot_scaled.get_rect(center=(x, y))
            screen.blit(dot_scaled, rect)

    def draw_selected_piece(self, screen, piece_size):
        if self.selected is None:
            return

        row, col = self.selected
        idx = rc_to_i(row, col)
        piece_code = self.board.squares[idx]

        if piece_code == 0:
            return

        x, y = self.rc_to_pixel(row, col)

        box_img = self.game.assets.red_box if side_of(piece_code) == 1 else self.game.assets.black_box
        box_scaled = pygame.transform.smoothscale(box_img, (piece_size, piece_size))
        screen.blit(box_scaled, box_scaled.get_rect(center=(x, y)))
        piece_img = self.game.assets.get_piece_image(piece_code)
        img_scaled = pygame.transform.smoothscale(piece_img, (piece_size, piece_size)).convert_alpha()
        img_scaled.set_alpha(200)  # 半透明效果
        screen.blit(img_scaled, img_scaled.get_rect(center=(x, y)))

    def pixel_to_rc(self, pos):
        """将屏幕像素坐标转换为棋盘行列号（row, col），若点击区域不在棋盘内则返回 None"""
        x, y = pos
        col = round((x - self.grid_rect.left) / self.dx)
        row = round((y - self.grid_rect.top) / self.dy)
        if 0 <= col <= 8 and 0 <= row <= 9:
            return row, col
        return None

    def rc_to_pixel(self, row, col):
        """将棋盘行列号转换为屏幕像素坐标（x, y）"""
        x = self.grid_rect.left + col * self.dx
        y = self.grid_rect.top + row * self.dy
        return int(x), int(y)







