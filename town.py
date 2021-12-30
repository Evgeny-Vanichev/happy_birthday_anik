import csv
import random
import sqlite3

import pygame
import thorpy
import sys
import os

FPS = 50

# Изображение не получится загрузить
# без предварительной инициализации pygame
pygame.init()
SIZE = WIDTH, HEIGHT = 500, 500
screen = pygame.display.set_mode(SIZE)
clock = pygame.time.Clock()


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level, city):
    new_player, x, y = None, None, None
    player_x, player_y = None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            Tile('empty', x, y)
            if level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                player_x, player_y = x, y
            elif level[y][x] in '123456789':
                create_npc(level[y][x], x, y, city)
    new_player = Player(player_x, player_y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


def create_npc(number, x, y, city):
    """NPC(level[y][x], x, y)"""
    con = sqlite3.connect("data\\npc\\npc.db")
    npc_type = con.cursor().execute(
        f"""SELECT function FROM functions
            WHERE id == {number}""").fetchone()[0]
    if npc_type == 'merchant':
        Merchant(number, npc_type, x, y, city)


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
        if dx < 0:
            if not self.left:
                self.image = pygame.transform.flip(self.image, True, False)
                self.left = True
                return
        else:
            if self.left:
                self.image = pygame.transform.flip(self.image, True, False)
                self.left = False

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


def draw_text(text, x, y, foreground=(255, 255, 255), background=(0, 0, 0), surface=screen):
    font = pygame.font.Font(None, 20)
    text = font.render(text, True, foreground)

    text_w = text.get_width()
    text_h = text.get_height()
    if background is not None:
        pygame.draw.rect(surface, background,
                         (x, y,
                          text_w + 10,
                          text_h + 10), 0)
    surface.blit(text, (x + 5, y + 5))


class NPC(pygame.sprite.Sprite):
    def __init__(self, npc_number, npc_type, pos_x, pos_y, city):
        super().__init__(all_sprites, Npc_group)
        self.flag = True
        self.pos_x, self.pos_y = pos_x, pos_y
        self.npc_type = npc_type
        self.city = city
        self.image = load_image(f'npc\\npc{npc_number}.png')
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + (50 - self.image.get_width()) // 2,
            tile_height * pos_y + (50 - self.image.get_height()) // 2)

    def get_line(self):
        filename = f"data/npc/{self.npc_type}.txt"
        # читаем уровень, убирая символы перевода строки
        with open(filename, 'r', encoding='utf-8') as mapFile:
            lines = [line.strip() for line in mapFile]
        return random.choice(lines)


class Merchant(NPC):
    def intro_dialog(self):
        self.flag = True
        line = self.get_line()
        screen2 = pygame.Surface((WIDTH, HEIGHT * 0.5))
        screen2.fill((250, 230, 180))
        font = pygame.font.Font(None, 25)
        text = font.render(line, True, (0, 0, 0))
        text_x = (WIDTH - text.get_width()) // 2
        text_y = HEIGHT * 0.1
        screen2.blit(text, (text_x, text_y))
        btn_open = thorpy.make_button("Магазин", func=self.open_shop)
        btn_open.surface = screen2
        btn_open.set_topleft((WIDTH * 0.2, HEIGHT * 0.4))
        btn_open.blit()
        btn_open.update()
        btn_quit = thorpy.make_button("Пока", func=self.finish_dialog)
        btn_quit.surface = screen2
        btn_quit.set_topleft((WIDTH * 0.8, HEIGHT * 0.4))
        btn_quit.blit()
        btn_quit.update()
        screen.blit(screen2, (0, 0))
        while self.flag:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                btn_open.react(event)
                btn_quit.react(event)
            pygame.display.flip()
            screen.blit(screen2, (0, 0))
            clock.tick(FPS)

    def open_shop(self):
        screen2 = pygame.Surface((WIDTH, HEIGHT))
        screen2.fill((250, 230, 180))
        elements = []
        inserters = []
        with open(f"data\\{self.city}\\2_shop.csv", mode='rt', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            for i, line in enumerate(reader):
                text1 = thorpy.OneLineText(line[0].ljust(20, ' ')+line[1])
                text1.set_font('consolas')
                inserter = thorpy.Inserter(value="0")
                box = thorpy.Box([text1, inserter])
                box.set_size((WIDTH * 0.75, 40))
                thorpy.store(box, mode="h")
                elements.append(box)
                inserters.append(inserter)

        central_box = thorpy.Box(elements=elements)
        ''''''
        central_box.set_main_color((255, 220, 130, 120))
        central_box.set_size((WIDTH * 0.8, HEIGHT * 0.8))
        central_box.set_topleft((50, 50))
        central_box.add_lift()
        menu = thorpy.Menu(central_box)
        for element in menu.get_population():
            element.surface = screen2
        central_box.blit()
        central_box.update()

        btn_buy = thorpy.make_button("Совершить покупку", func=self.finish_dialog)
        btn_buy.surface = screen2
        btn_buy.set_topleft((WIDTH * 0.1, HEIGHT * 0.9))
        btn_buy.blit()
        btn_buy.update()

        btn_quit = thorpy.make_button("Отменить покупку", func=self.finish_dialog)
        btn_quit.surface = screen2
        btn_quit.set_topleft((WIDTH * 0.7, HEIGHT * 0.9))
        btn_quit.blit()
        btn_quit.update()

        screen.blit(screen2, (0, 0))
        while self.flag:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                btn_quit.react(event)
                btn_buy.react(event)
                menu.react(event)
            pygame.display.flip()
            screen.blit(screen2, (0, 0))
            clock.tick(FPS)

    def finish_dialog(self):
        self.flag = False


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


def enter_city(city_name):
    global Npc_group
    Npc_group = pygame.sprite.Group()

    tile_images['wall'] = load_image('icons\\house.png')
    tile_images['empty'] = load_image('icons\\road.png')

    global player, level_x, level_y
    level = load_level(city_name + '\\city.txt')
    player, level_x, level_y = generate_level(level, city_name)
    PLAYER_MOVE_EVENT = pygame.USEREVENT + 1
    move = (0, 0)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    move = (-1, 0)
                    player.move(*move)
                    pygame.time.set_timer(PLAYER_MOVE_EVENT, 250)
                elif event.key == pygame.K_RIGHT:
                    move = (1, 0)
                    player.move(*move)
                    pygame.time.set_timer(PLAYER_MOVE_EVENT, 250)
                elif event.key == pygame.K_UP:
                    move = (0, -1)
                    player.move(*move)
                    pygame.time.set_timer(PLAYER_MOVE_EVENT, 250)
                elif event.key == pygame.K_DOWN:
                    move = (0, 1)
                    player.move(*move)
                    pygame.time.set_timer(PLAYER_MOVE_EVENT, 250)
                elif event.key == pygame.K_SPACE:
                    for sprite in Npc_group:
                        if abs(sprite.pos_x - player.pos_x) <= 1 and abs(
                                sprite.pos_y - player.pos_y) <= 1:
                            sprite.intro_dialog()
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
        for sprite in Npc_group:
            if not isinstance(sprite, NPC):
                continue
            if abs(sprite.pos_x - player.pos_x) <= 1 and abs(sprite.pos_y - player.pos_y) <= 1:
                draw_text('нажмите space для диалога',
                          sprite.rect.x - tile_width // 2,
                          sprite.rect.y - tile_height // 2)
        pygame.display.flip()
        clock.tick(FPS)


start_screen()

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
camera = Camera()

tile_width = tile_height = 50
tile_images = {
    'wall': load_image('icons\\house.png'),
    'empty': load_image('icons\\road.png')
}
player_image = load_image('icons\\player.png')

enter_city("city1")
