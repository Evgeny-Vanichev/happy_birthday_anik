import pygame
import thorpy

from scipt_reader import *
from sprites import *
import sqlite3

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
            elif level[y][x] in '123456789':
                create_npc(level[y][x], x, y, city)
    new_player = Player(player_x, player_y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


def create_npc(number, x, y, city):
    """NPC(level[y][x], x, y)"""
    con = sqlite3.connect("data/npc/npc.db")
    npc_type = con.cursor().execute(
        f"""SELECT function FROM functions
                WHERE id == {number}""").fetchone()[0]
    if npc_type == 'person':
        NPC(number, x, y, city)
    elif npc_type == 'object':
        Object(number, x, y, city)


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
        self.inventory = ["КЛЮЧ ОТ ВОРОТ"]

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
            for sprite in Npc_group:
                if not isinstance(sprite, Object):
                    continue
                if sprite.state == 'yes':
                    continue
                if sprite.pos_x == self.pos_x and sprite.pos_y == self.pos_y:
                    raise IndexError
        except IndexError:
            self.rect = self.rect.move(-dx * tile_width, -dy * tile_height)
            self.pos_x -= dx
            self.pos_y -= dy

    def give(self, item):
        self.inventory.append(item)
        step(add=True)
        draw_text('F/space',
                  x=self.rect.x - tile_width // 2,
                  y=self.rect.y - tile_height // 2,
                  foreground=(255, 255, 255),
                  background=(0, 0, 0), surface=screen)


class NPC(pygame.sprite.Sprite):
    def __init__(self, npc_number, pos_x, pos_y, city):
        super().__init__(all_sprites, Npc_group)

        self.pos_x, self.pos_y = pos_x, pos_y
        self.city = city
        self.image = load_image(f'npc\\npc{npc_number}.png')
        self.number = npc_number
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + (50 - self.image.get_width()) // 2,
            tile_height * pos_y + (50 - self.image.get_height()) // 2)
        self.current_line = ""
        self.current_reaction = ""
        self.interaction = False

    def default_line(self):
        return "С днём рождения!\n" + random.choice(['Счастья!', 'Здоровья!', 'Побольше секса!'])

    def default_reaction(self):
        return 'Привееет!'

    def get_line(self):
        global NEXT_UPDATE
        if str(NEXT_UPDATE['who']) == str(self.number):
            self.current_line = NEXT_UPDATE['line']
            self.current_reaction = NEXT_UPDATE['reaction']
            if NEXT_UPDATE['what'] == 'item':
                self.interaction = True
                self.item = NEXT_UPDATE['item']
            try:
                NEXT_UPDATE = next(scipt)
            except:
                pass
        if self.current_line != "":
            return self.current_line, self.current_reaction
        return self.default_line(), self.default_reaction()

    def intro_dialog(self):
        thorpy.init(screen, thorpy.theme_game1)

        line, reaction = self.get_line()

        NPC_line = thorpy.Text(line, max_width=WIDTH*0.7)
        dialogue_state = [1]

        def set_new_npc_line(npc_line_label=NPC_line):
            if self.interaction:
                player.give(self.item)
                exit_dialogue()
            line, reaction = self.get_line()
            npc_line_label.set_text(line, max_width=WIDTH * 0.7)
            btn_open.set_text(reaction)

        def exit_dialogue():
            dialogue_state[0] = 0

        btn_open = new_button(reaction, set_new_npc_line)
        btn_quit = new_button("Пока", exit_dialogue)
        buttons = thorpy.Group([btn_open, btn_quit])
        buttons.sort_children('h')
        menu = thorpy.Box([NPC_line, buttons])
        menu.sort_children('v')
        menu.set_max_text_width(WIDTH * 0.65, apply_to_children=True)

        menu.set_size((WIDTH * 0.7, HEIGHT * 0.6))
        menu.set_center(WIDTH // 2, HEIGHT * 0.4)

        menu.set_opacity_bck_color(OPACITY)
        updater = menu.get_updater()

        while dialogue_state[0]:
            events = pygame.event.get()
            mouse_rel = pygame.mouse.get_rel()
            for event in events:
                if event.type == pygame.QUIT:
                    terminate()
            all_sprites.draw(screen)
            updater.update(events=events,
                           mouse_rel=mouse_rel)
            pygame.display.flip()
            clock.tick(FPS)


class Object(NPC):
    def __init__(self, npc_number, pos_x, pos_y, city):
        super().__init__(npc_number, pos_x, pos_y, city)

        self.state = 'non'

        self.image = load_image(f'npc\\npc{npc_number}_non.png')

        con = sqlite3.connect("data/npc/npc.db")
        self.non_line = con.cursor().execute(
            f"""SELECT default_line FROM functions
                    WHERE id == {self.number}""").fetchone()[0]
        self.interact_line = con.cursor().execute(
            f"""SELECT interact_line FROM functions
                    WHERE id == {self.number}""").fetchone()[0]
        self.yes_line = con.cursor().execute(
            f"""SELECT yes_line FROM functions
                    WHERE id == {self.number}""").fetchone()[0]
        self.non_to_yes = con.cursor().execute(
            f"""SELECT item FROM functions
                    WHERE id == {self.number}""").fetchone()[0]

    def default_line(self):
        if self.state == 'non':
            return self.non_line
        return self.yes_line

    def default_reaction(self):
        return self.interact_line

    def intro_dialog(self):
        thorpy.init(screen, thorpy.theme_game1)

        line, reaction = self.get_line()
        NPC_line = new_text(line)
        dialogue_state = [1]

        def exit_dialogue():
            dialogue_state[0] = 0

        if self.state == 'non':
            def try_to_interact(npc_line_label=NPC_line):
                if self.non_to_yes in player.inventory:
                    STEP = globals().get('STEP')
                    globals().update({'STEP': STEP + 1})
                    self.state = 'yes'
                    self.image = load_image(f'npc\\npc{self.number}_yes.png')
                    exit_dialogue()
                else:
                    NPC_line.set_text('Вероятно, мне не хватает:\n' + self.non_to_yes)

            btn_interact = new_button(self.non_line, try_to_interact)
            btn_quit = new_button("Вернусь потом", exit_dialogue)
            buttons = thorpy.Group([btn_interact, btn_quit])
            buttons.sort_children('v')
            menu = thorpy.Box([NPC_line, buttons])
        else:
            btn_quit = new_button("Ура!", exit_dialogue)
            buttons = thorpy.Group([btn_quit])
            buttons.sort_children('h')
            menu = thorpy.Box([NPC_line, buttons])
        menu.sort_children('v')

        menu.set_size((WIDTH * 0.7, HEIGHT * 0.6))
        menu.set_center(WIDTH // 2, HEIGHT * 0.4)

        menu.set_opacity_bck_color(OPACITY)
        updater = menu.get_updater()

        while dialogue_state[0]:
            events = pygame.event.get()
            mouse_rel = pygame.mouse.get_rel()
            for event in events:
                if event.type == pygame.QUIT:
                    terminate()
            all_sprites.draw(screen)
            updater.update(events=events,
                           mouse_rel=mouse_rel)
            pygame.display.flip()
            clock.tick(FPS)


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


def new_button(text, func):
    button = thorpy.Button(text)
    button.at_unclick = func
    return button


def new_text(text):
    return thorpy.Text(text, font_size=32, max_width=WIDTH * 0.6)


def open_pause_menu():
    paused = [1]

    def unpause():
        paused[0] = 0

    thorpy.init(screen, thorpy.theme_game1)
    controls = []
    for txt in ['Меню паузы', '']:
        controls.append(new_text(txt))

    for i, (txt, func) in enumerate(zip(
            ['Продолжить (space)', 'Сохранить и выйти (Q)'],
            [unpause, terminate]
    )):
        controls.append(new_button(txt, func))

    pause_menu_elements = thorpy.Box(controls)
    pause_menu_elements.sort_children('v')

    pause_menu_elements.set_size((WIDTH * 0.7, HEIGHT * 0.6))
    pause_menu_elements.set_center(WIDTH // 2, HEIGHT * 0.4)

    pause_menu_elements.set_opacity_bck_color(OPACITY)
    updater = pause_menu_elements.get_updater()

    while paused[0]:
        events = pygame.event.get()
        mouse_rel = pygame.mouse.get_rel()
        for event in events:
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_SPACE, pygame.K_ESCAPE]:
                    paused[0] = 0
                elif event.key == pygame.K_q:
                    terminate()
        all_sprites.draw(screen)
        updater.update(events=events,
                       mouse_rel=mouse_rel)

        pygame.display.flip()
        clock.tick(FPS)


def open_inventory():
    print(player.inventory)
    paused = [1]

    def unpause():
        paused[0] = 0

    def settext(idx):
        if idx == -1:
            info_text.set_text(" " * 11)
            return
        info_text.set_text(player.inventory[idx])
        # info_text.set_text(str(idx))

    thorpy.init(screen, thorpy.theme_game1)
    info_text = thorpy.Text(" " * 11)
    inventory_buttons = []
    for i, item in enumerate(player.inventory):
        inventory_buttons.append(
            thorpy.ImageButton("", load_image(f"icons\\{item}.png").copy())
        )
        inventory_buttons[-1].at_unclick = lambda x=i: settext(x)

    for _ in range(len(player.inventory), 12):
        inventory_buttons.append(thorpy.Button(" "))
        inventory_buttons[-1].at_unclick = lambda: settext(-1)

    inventory_buttons = thorpy.Box(inventory_buttons)
    inventory_buttons.sort_children('grid', nx=4, ny=3)

    controls = thorpy.Group([info_text, inventory_buttons])
    controls.sort_children('h')

    pause_menu_elements = thorpy.Box([thorpy.Text('Инвентарь', font_size=64), controls])
    pause_menu_elements.sort_children('v')

    pause_menu_elements.set_size((WIDTH * 0.7, HEIGHT * 0.6))
    pause_menu_elements.set_center(WIDTH // 2, HEIGHT * 0.4)

    pause_menu_elements.set_opacity_bck_color(OPACITY)
    updater = pause_menu_elements.get_updater()

    while paused[0]:
        events = pygame.event.get()
        mouse_rel = pygame.mouse.get_rel()
        for event in events:
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_TAB, pygame.K_i]:
                    paused[0] = 0
                elif event.key == pygame.K_q:
                    terminate()
        all_sprites.draw(screen)
        updater.update(events=events,
                       mouse_rel=mouse_rel)

        pygame.display.flip()
        clock.tick(FPS)


def enter_city(city_name):
    tile_images['wall'] = load_image('icons/house.png')
    tile_images['empty'] = load_image('icons/road.png')

    global player, level_x, level_y
    level = load_location(city_name + '/city1.txt')
    player, level_x, level_y = generate_location(level, city_name)

    move = (0, 0)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                move = check_move(event)
                if event.key in [pygame.K_ESCAPE]:
                    open_pause_menu()
                elif event.key in [pygame.K_TAB, pygame.K_i]:
                    open_inventory()
                if event.key in [pygame.K_SPACE, pygame.K_f]:
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
                draw_text('F/space',
                          x=sprite.rect.x - tile_width // 2,
                          y=sprite.rect.y - tile_height // 2,
                          foreground=(255, 255, 255),
                          background=(0, 0, 0), surface=screen)
        pygame.display.flip()
        clock.tick(FPS)


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


def town():
    global clock
    global camera
    global current_player, current_city
    global tile_images, player_image
    global NEXT_UPDATE, scipt
    clock = pygame.time.Clock()

    # Загрузка файлов игры
    current_player = 'player1'
    current_city = 'city1'

    tile_images = {
        'wall': load_image('icons/house.png'),
        'empty': load_image('icons/road.png')
    }
    player_image = load_image('icons/player.png')
    scipt = yield_scipt_lines()
    NEXT_UPDATE = next(scipt)

    # камера
    camera = Camera()
    enter_city(current_city)


town()
