import pygame
import sys
import os

FPS = 50

# Изображение не получится загрузить
# без предварительной инициализации pygame
pygame.init()
SIZE = WIDTH, HEIGHT = 500, 500
screen = pygame.display.set_mode(SIZE)
clock = pygame.time.Clock()


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
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
                NPC(level[y][x], x, y)
    new_player = Player(player_x, player_y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


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


class NPC(pygame.sprite.Sprite):
    def __init__(self, number, pos_x, pos_y):
        super().__init__(all_sprites, Npc_group)
        self.type = number
        self.pos_x, self.pos_y = pos_x, pos_y
        self.image = load_image(f'npc\\npc{number}.png')
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + (50 - self.image.get_width()) // 2,
            tile_height * pos_y + (50 - self.image.get_height()) // 2)

    def show_dialog(self):
        start_screen()


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


def terminate():
    pygame.quit()
    sys.exit()


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


def draw_text(text, x, y):
    font = pygame.font.Font(None, 20)
    text = font.render(text, True, (255, 255, 255))
    text_w = text.get_width()
    text_h = text.get_height()
    pygame.draw.rect(screen, (0, 0, 0),
                     (x, y,
                      text_w + 10, text_h + 10), 0)
    screen.blit(text, (x + 5, y + 5))


def enter_city(city_name):
    global Npc_group
    Npc_group = pygame.sprite.Group()

    tile_images['wall'] = load_image('house.png')
    tile_images['empty'] = load_image('road.png')

    global player, level_x, level_y
    level = load_level(city_name)
    player, level_x, level_y = generate_level(level)
    PLAYER_MOVE_EVENT = pygame.USEREVENT + 1
    move = (0, 0)
    time = 0
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
                            sprite.show_dialog()
                """print()
                print(*level, sep='\n')"""
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
            if abs(sprite.pos_x - player.pos_x) <= 1 and abs(sprite.pos_y - player.pos_y) <= 1:
                draw_text('нажмите space для диалога',
                          sprite.rect.x - tile_width // 2,
                          sprite.rect.y - tile_height //2 )
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
    'wall': load_image('house.png'),
    'empty': load_image('road.png')
}
player_image = load_image('player.png')

enter_city("city1.txt")
