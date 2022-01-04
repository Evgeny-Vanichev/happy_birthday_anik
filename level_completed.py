import pygame
import sys
from random import randint

FPS = 50
size = width, height = 500, 500


def terminate():
    pygame.quit()
    sys.exit()


def level_completed():
    pygame.init()
    screen = pygame.display.set_mode(size)
    screen.fill((0, 0, 0))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if 105 <= event.pos[0] <= 405 and 300 <= event.pos[1] <= 350:
                    return

        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, pygame.Color(50, 50, 230), (105, 300, 300, 50), 0)
        font = pygame.font.Font(None, 80)
        text = font.render('Level completed!', True, (randint(0, 255), randint(0, 255), randint(0, 255)))
        text_x = 20
        text_y = 200
        screen.blit(text, (text_x, text_y))
        font = pygame.font.Font(None, 30)
        text1 = font.render('Continue', True, (173, 216, 230))
        text1_x = 210
        text1_y = 315
        screen.blit(text1, (text1_x, text1_y))
        pygame.display.flip()