import pyxel

SCROLL_X = 0
SCROLL_Y = 0
MAX_SCROLL_X = 384
MAX_SCROLL_Y = 0
on_sticky = False

CURRENT_LEVEL = 0

SOLID_TILES = [
    (0, 1), (1, 1), (2, 1), (0, 2), (1, 2),
    (2, 2), (0, 3), (1, 3), (2, 3), (0, 5),
    (1, 5), (2, 5), (3, 5), (0, 6), (0, 7),
    (0, 8), (5, 6), (5, 7), (5, 8), (6, 6),
    (6, 7), (6, 8), (7, 6), (7, 7), (7, 8),
    (1, 6), (1, 7), (1, 8), (2, 6), (2, 7),
    (2, 8), (3, 6), (3, 7), (3, 8), (4, 5),
    (5, 5), (6, 5), (4, 6), (4, 7), (4, 8)
]

STICKY_TILES = [
    (1, 6), (1, 7), (1, 8), (2, 6), (2, 7),
    (2, 8), (3, 6), (3, 7), (3, 8), (4, 5),
    (5, 5), (6, 5), (4, 6), (4, 7), (4, 8)
]


def get_tile(tile_x: int, tile_y: int, tilemap: int = 0):
    return pyxel.tilemap(tilemap).pget(tile_x, tile_y + 16 * CURRENT_LEVEL)


def detect_collision(x, y, dy):
    global on_sticky
    x1 = x // 8
    y1 = y // 8
    x2 = (x + 7 - 1) // 8
    y2 = (y + 8 - 1) // 8

    for yi in range(y1, y2 + 1):
        for xi in range(x1, x2 + 1):
            tile = get_tile(xi, yi)
            if tile in SOLID_TILES:
                if tile in STICKY_TILES:
                    on_sticky = True
                else:
                    on_sticky = False
                return True

    if dy > 0 and y % 8 == 1:
        for xi in range(x1, x2 + 1):
            tile = get_tile(xi, y1 + 1)
            if tile in SOLID_TILES:
                if tile in STICKY_TILES:
                    on_sticky = True
                else:
                    on_sticky = False
                return True
    return False


def correct_distances(x, y, dx, dy):
    sign = 1 if dx > 0 else -1
    for _ in range(abs(dx)):
        if detect_collision(SCROLL_X + x + sign, y, dy):
            break
        x += sign

    sign = 1 if dy > 0 else -1
    for _ in range(abs(dy)):
        if detect_collision(SCROLL_X + x, y + sign, dy):
            break
        y += sign
    return x, y, dx, dy


class Player:
    def __init__(self, x, y, app):
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0

        self.app = app

        self.direction = -1
        self.direction = -1
        self.is_falling = False
        self.is_running = False

        self.speed = 2
        self.jump_power = 7

    def update(self):
        global SCROLL_X

        last_scroll_x = SCROLL_X
        last_x = self.x
        last_y = self.y

        # Déplacements horizontaux
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_Q):
            self.direction = 1
            self.dx = -self.speed

        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D):
            self.direction = -1
            self.dx = self.speed

        # Dplacement verticaux
        if on_sticky and (pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_Z)):
            self.dy = self.speed

        # Sauts
        self.dy = min(self.dy + 1, 3)
        if pyxel.btn(pyxel.KEY_SPACE) and self.dy == 3 and not self.is_falling:
            self.dy = -self.jump_power

        # Mise à jour réelle des valeurs
        self.x, self.y, self.dx, self.dy = correct_distances(self.x, self.y, self.dx, self.dy)

        # Fixe les dépassements du cadre
        if self.y < 0:
            self.y = 0
        if self.y > 120:
            self.y = 120
        if self.x < 0:
            self.x = 0
        if self.x > 120:
            self.x = 120

        # Fixe le scroll
        if self.x > 88:
            diff = min(MAX_SCROLL_X - SCROLL_X, self.x - 88)
            self.x -= diff
            SCROLL_X += diff
            self.app.spawn_enemy(self.x, self.x + diff)
        if self.x < 40:
            diff = min(SCROLL_X, 40 - self.x)
            self.x += diff
            SCROLL_X -= diff

        self.dx = int(self.dx * 0.8)
        self.is_falling = self.y > last_y
        self.is_running = self.x != last_x or SCROLL_X != last_scroll_x

    def draw(self):
        u = 24
        v = 16

        if self.is_running:
            u += 8 * 2

        if self.is_falling:
            pass

        pyxel.blt(self.x, self.y, 0, u, v, 8, 8, 9)


class Slime:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0

        self.jump_power = 3

        self.last_scroll_x = SCROLL_X
        self.direction = 1
        self.jumping = False

    def update(self, player_x):
        self.direction = 1 if player_x < self.x else -1
        d_player = abs(self.x - player_x)
        if d_player < 0:
            self.jumping = True
            self.dy = -self.jump_power
            self.dx = self.direction * self.jump_power

        if SCROLL_X != self.last_scroll_x:
            self.x += self.last_scroll_x - SCROLL_X
            self.last_scroll_x = SCROLL_X

        self.x, self.y, self.dx, self.dy = correct_distances(self.x, self.y, self.dx, self.dy)

    def draw(self):
        u = 24 + 8 * (1 if pyxel.frame_count % 30 < 15 else 0)
        v = 40 + 32 * self.direction
        pyxel.blt(self.x, self.y, 0, u, v, 8, 8, 9)


def flash_msg(text: str):
    x = (128 - (len(text) * 4 - 2)) // 2
    y = 30
    pyxel.text(x, y + 1, text, 7)
    pyxel.text(x, y, text, 0)


class App:
    def __init__(self):
        self.title = "TITRE"
        self.resources = "assets/2_edit.pyxres"
        self.respawn = [0, (32, 20)]  # [SCROLL_X, (player.x, player.y)]
        self.death_count = 0
        self.pause = False
        self.setting = False

        self.player = Player(32, 20, self)
        self.has_key = False
        self.mobs = []

        for coords in LEVELS[CURRENT_LEVEL]['mobs']:
            self.mobs.append(Slime(coords[0]*8, coords[1]*8))

        self.messages = []

        pyxel.init(128, 128, title=self.title)
        pyxel.load(self.resources)
        pyxel.run(self.update, self.draw)

    def death(self):
        global SCROLL_X
        self.death_count += 1
        SCROLL_X = self.respawn[0]
        x, y = self.respawn[1]
        self.player = Player(x, y, self)

    def spawn_enemy(self, left_x, right_x):
        left_x = pyxel.ceil(left_x / 8)
        right_x = pyxel.floor(right_x / 8)
        for x in range(left_x, right_x + 1):
            for y in range(16):
                tile = get_tile(x, y)
                if tile == (3, 0):
                    self.mobs.append(Slime(x * 8 + SCROLL_X, y * 8))

    def settings(self):
        self.setting = True
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if 53 <= pyxel.mouse_x <= 72 and 48 <= pyxel.mouse_y <= 57:
                pyxel.quit()
            if 49 <= pyxel.mouse_x <= 76 and 60 <= pyxel.mouse_y <= 69:
                self.setting = False
                self.pause = False

    @staticmethod
    def tuto_text():
        if SCROLL_X < 15:
            pyxel.text(6, 20, "Appuyez sur D pour avancer", 0)

    def get_key(self):
        tile = get_tile((self.player.x + SCROLL_X) // 8, (self.player.y + SCROLL_Y) // 8)
        if tile == (11, 5):
            set_tile((self.player.x + SCROLL_X) // 8, (self.player.y + SCROLL_Y) // 8, (0, 0))
            self.has_key = True

    def on_door(self):
        tile = get_tile((self.player.x + SCROLL_X) // 8, (self.player.y + SCROLL_Y) // 8)
        if tile == (10, 6):
            return True

    def update(self):
        if not self.pause:
            self.player.update()
            for enemy in self.mobs:
                enemy.update(self.player.x)

            if pyxel.btnp(pyxel.KEY_C):
                self.death()

            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                print(pyxel.mouse_x, pyxel.mouse_y)
                if 118 <= pyxel.mouse_x <= 126 and 2 <= pyxel.mouse_y <= 10:
                    self.pause = not self.pause
                    if self.pause:
                        self.settings()

            if self.player.y >= 100:
                self.death()

        if self.setting:
            self.settings()

    def draw(self):
        pyxel.cls(6)
        pyxel.mouse(True)

        pyxel.bltm(0, 0, 0, SCROLL_X, SCROLL_Y + 128 * CURRENT_LEVEL, 128, 128, 9)
        pyxel.blt(118, 2, 0, 40, 32, 8, 8, 9)

        self.player.draw()

        for enemy in self.mobs:
            enemy.draw()

        if CURRENT_LEVEL == 0:
            self.tuto_text()

        if self.setting:
            pyxel.rect(53, 48, 19, 9, 7)
            pyxel.text(55, 50, "Quit", 0)
            pyxel.rect(49, 60, 27, 9, 7)
            pyxel.text(51, 62, "Resume", 0)


if __name__ == "__main__":
    App()
