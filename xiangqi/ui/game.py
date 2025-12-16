from .theme import Theme
from .asset_manager import AssetManager
import pygame

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.theme = Theme.style_1()
        self.assets = AssetManager(self.theme)
        self.scene = None

    def change_scene(self, new_scene, **kwargs):
        #TODO
        pass

    def set_theme(self, theme: Theme):
        self.theme = theme
        self.assets = AssetManager(self.theme)

    def run(self):
        pass