from tools import *
import random


def do_nothing():
    pass


FPS = 50
SIZE = WIDTH, HEIGHT = 500, 500
PLAYER_MOVE_EVENT = pygame.USEREVENT + 1
DRAW_TEXT_EVENT = pygame.USEREVENT + 2
DRAW_TEXT_DELAY = 25
tile_width = tile_height = 50
# IS_PAUSED = False
OPACITY = 205
WISHES = ['Счастья!', 'Здоровья!', 'Побольше секса!']