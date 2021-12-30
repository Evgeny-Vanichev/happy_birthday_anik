import pygame
import sys


def terminate():
    pygame.quit()
    sys.exit()


class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, text, group):
        super().__init__(group)
        self.image = pygame.Surface((w, h), pygame.SRCALPHA, 32)
        pygame.draw.rect(self.image, pygame.Color("red"), (0, 0, w, h))
        self.rect = pygame.Rect(x, y, w, h)
        self.state = 0
        self.text = text

    def update(self, *args):
        if len(args) == 0:
            return False
        x, y = args[0]
        if 0 <= x - self.rect.x <= self.rect.w and 0 <= y - self.rect.y <= self.rect.h:
            return True


def DialogWindow(npc_type):
    margin = 0.1
    w, h = width * (1 - 2 * margin), height * (1 - 2 * margin)
    dialogScreen = pygame.Surface((w, h))
    btn_sprites = pygame.sprite.Group()
    Button(w * margin, h * 0.8, w * 0.2, h * 0.1, npc_type, btn_sprites)
    Button(w * 0.7, h * 0.8, w * 0.2, h * 0.1, npc_type, btn_sprites)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                x -= width * 0.1
                y -= height * 0.1
                for sprite in btn_sprites:
                    if sprite.rect.collidepoint((x, y)):
                        return
        screen.fill((0, 0, 0))
        dialogScreen.fill((255, 255, 255))
        btn_sprites.draw(dialogScreen)
        screen.blit(dialogScreen, (width * margin, height * margin))
        pygame.display.flip()


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('PyGame')
    size = width, height = 300, 300
    screen = pygame.display.set_mode(size)
    running = True
    all_sprites = pygame.sprite.Group()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue
            if event.type == pygame.KEYDOWN:
                DialogWindow('1')
        screen.fill((0, 0, 0))
        pygame.display.flip()
        screen.fill((255, 255, 255))
    pygame.quit()
