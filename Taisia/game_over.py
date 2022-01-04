import pygame
import sys
from random import randint

FPS = 50
size = width, height = 500, 500


def game_over():
    pygame.init()
    screen = pygame.display.set_mode(size)
    screen.fill((0, 0, 0))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 100)
        text = font.render('Game Over', True, (randint(0, 255), randint(0, 255), randint(0, 255)))
        text_x = 70
        text_y = 200
        screen.blit(text, (text_x, text_y))
        pygame.display.flip()
    pygame.quit()
    sys.exit()