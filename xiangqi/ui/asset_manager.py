import os
from pathlib import Path
from .theme import Theme
import pygame

PIECE_CODE_TO_FILENAME = {
    1: ("r_j", "b_j"),
    2: ("r_s", "b_s"),
    3: ("r_x", "b_x"),
    4: ("r_c", "b_c"),
    5: ("r_m", "b_m"),
    6: ("r_p", "b_p"),
    7: ("r_z", "b_z"),
}

class AssetManager:
    def __init__(self, theme: Theme):
        self.theme = theme
        self.piece_images = {}
        self.load_assets()

    def load_assets(self):
        base_path = Path(__file__).parent.parent / "assets" / "img" / self.theme.piece_style
        for piece_code, (red_filename, black_filename) in PIECE_CODE_TO_FILENAME.items():
            red_path = base_path / f"{red_filename}.png"
            black_path = base_path / f"{black_filename}.png"
            self.piece_images[piece_code] = pygame.image.load(str(red_path))
            self.piece_images[-piece_code] = pygame.image.load(str(black_path))
        self.bg = pygame.image.load(str(base_path / "bg.png"))
        self.red_box = pygame.image.load(str(base_path / "r_box.png"))
        self.black_box = pygame.image.load(str(base_path / "b_box.png"))
        self.dot = pygame.image.load(str(base_path / "dot.png"))

    def get_piece_image(self, piece_code: int) -> pygame.Surface | None:
        return self.piece_images.get(piece_code)

