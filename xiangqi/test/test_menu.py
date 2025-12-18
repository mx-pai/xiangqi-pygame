import pygame
from ..ui.game import Game
from ..ui.game_config import GAME_WIDTH, GAME_HEIGHT

pygame.init()
screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption(". Test")
game = Game(screen)
game.run()