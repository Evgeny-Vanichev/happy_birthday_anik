import pygame
import sys
from random import randint

FPS = 50
size = width, height = 500, 500


def terminate():
    pygame.quit()
    sys.exit()


def win_game():
    pygame.init()
    screen = pygame.display.set_mode(size)
    screen.fill((0, 0, 0))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 80)
        text = font.render('You win!', True, (randint(0, 255), randint(0, 255), randint(0, 255)))
        text_x = 150
        text_y = 200
        screen.blit(text, (text_x, text_y))
        pygame.display.flip()