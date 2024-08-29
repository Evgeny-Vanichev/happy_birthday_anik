import pygame

from tools import *
from constants import *

pygame.init()
screen = pygame.display.set_mode(SIZE)


def generate_location(level, city):
    new_player, x, y = None, None, None
    player_x, player_y = None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            Tile('empty', x, y)
            if level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                player_x, player_y = x, y
            # elif level[y][x] in '123456789':
            #     create_npc(level[y][x], x, y, city)
    new_player = Player(player_x, player_y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        if tile_type == 'wall':
            super().__init__(walls_group, tiles_group, all_sprites)
        else:
            super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.pos_x, self.pos_y = pos_x, pos_y
        self.image = player_image
        self.left = True
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 1)

    def turn_over(self, dx):
        if dx == 0:
            return
        if (dx < 0) ^ self.left:  # двигаемся не туда, куда повернуты
            self.image = pygame.transform.flip(self.image, True, False)
            self.left = not self.left

    def move(self, dx, dy):
        self.turn_over(dx)

        self.pos_x += dx
        self.pos_y += dy
        self.rect = self.rect.move(dx * tile_width, dy * tile_height)
        try:
            if not (0 <= self.pos_x <= level_x and 0 <= self.pos_y <= level_y):
                raise IndexError
            if pygame.sprite.spritecollideany(self, walls_group):
                raise IndexError
        except IndexError:
            self.rect = self.rect.move(-dx * tile_width, -dy * tile_height)
            self.pos_x -= dx
            self.pos_y -= dy


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        if 4 < target.pos_x < level_x - 4:
            self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        if 4 < target.pos_y < level_y - 4:
            self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


def check_move(event: pygame.event):
    move = (0, 0)
    if event.key in [pygame.K_LEFT, pygame.K_a]:
        move = (-1, 0)
        player.move(*move)
        pygame.time.set_timer(PLAYER_MOVE_EVENT, 250)
    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
        move = (1, 0)
        player.move(*move)
        pygame.time.set_timer(PLAYER_MOVE_EVENT, 250)
    elif event.key in [pygame.K_UP, pygame.K_w]:
        move = (0, -1)
        player.move(*move)
        pygame.time.set_timer(PLAYER_MOVE_EVENT, 250)
    elif event.key in [pygame.K_DOWN, pygame.K_s]:
        move = (0, 1)
        player.move(*move)
        pygame.time.set_timer(PLAYER_MOVE_EVENT, 250)
    return move


def enter_city(city_name):
    # global Npc_group
    # Npc_group = pygame.sprite.Group()

    tile_images['wall'] = load_image('icons/house.png')
    tile_images['empty'] = load_image('icons/road.png')

    global player, level_x, level_y
    level = load_location(city_name + '/city.txt')
    player, level_x, level_y = generate_location(level, city_name)

    move = (0, 0)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                move = check_move(event)
                # if event.key == pygame.K_SPACE:
                #     for sprite in Npc_group:
                #         if abs(sprite.pos_x - player.pos_x) <= 1 and abs(
                #                 sprite.pos_y - player.pos_y) <= 1:
                #             sprite.intro_dialog()
            elif event.type == pygame.KEYUP:
                move = (0, 0)
                pygame.time.set_timer(PLAYER_MOVE_EVENT, 250)
            elif event.type == PLAYER_MOVE_EVENT:
                player.move(*move)

        # изменяем ракурс камеры
        camera.update(player)
        # обновляем положение всех спрайтов
        for sprite in all_sprites:
            camera.apply(sprite)

        screen.fill((0, 0, 0))
        all_sprites.draw(screen)
        # for sprite in Npc_group:
        #     if not isinstance(sprite, NPC):
        #         continue
        #     if abs(sprite.pos_x - player.pos_x) <= 1 and abs(sprite.pos_y - player.pos_y) <= 1:
        #         draw_text('нажмите space для диалога',
        #                   x=sprite.rect.x - tile_width // 2,
        #                   y=sprite.rect.y - tile_height // 2,
        #                   foreground=(255, 255, 255),
        #                   background=(0, 0, 0), surface=screen)
        pygame.display.flip()
        clock.tick(FPS)


def town():
    global clock
    global size, WIDTH, HEIGHT
    global current_player
    global all_sprites
    global tiles_group
    global walls_group
    global player_group
    global camera
    global tile_images
    global player_image

    clock = pygame.time.Clock()

    # Загрузка файлов игры
    current_player = 'player1'
    current_city = 'city1'

    # группы спрайтов
    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    walls_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    camera = Camera()

    tile_images = {
        'wall': load_image('icons/house.png'),
        'empty': load_image('icons/road.png')
    }
    player_image = load_image('icons/player.png')
    enter_city(current_city)


town()
