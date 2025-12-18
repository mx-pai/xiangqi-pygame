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
        pygame.mixer.init()
        pygame.mixer.music.load('xiangqi/assets/audio/bgm.mp3')
        pygame.mixer.music.play(-1)
        from .menuscene import MenuScene
        self.change_scene(MenuScene(self))

    def change_scene(self, new_scene, **kwargs):
        if self.scene:
            self.scene.on_exit()
        self.scene = new_scene
        self.scene.on_enter(**kwargs)

    def set_theme(self, theme: Theme):
        self.theme = theme
        self.assets = AssetManager(self.theme)
        if self.scene and hasattr(self.scene, 'on_theme_change'):
            self.scene.on_theme_change(theme)

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif self.scene:
                    self.scene.handle_event(event)
            if self.scene:
                self.scene.update(dt)
                self.scene.draw(self.screen)
            pygame.display.flip()
        pygame.quit()