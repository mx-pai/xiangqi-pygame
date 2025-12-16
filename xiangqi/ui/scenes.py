import pygame
class Scene:
    """
    switchable game scene 基类。
    """
    def __init__(self, game):
        self.game = game

    def on_enter(self, **kwards):
        pass

    def on_exit(self):
        pass

    def handle_event(self, event: pygame.event.Event):
        pass

    def update(self, dt: float):
        pass

    def draw(self, screen: pygame.Surface):
        pass