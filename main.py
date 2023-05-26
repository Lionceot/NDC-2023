import pyxel

SCROLL_X = 0
SCROLL_Y = 0
MAX_SCROLL_X = 0
MAX_SCROLL_Y = 0


def get_tile(tile_x: int, tile_y: int, tilemap: int = 0):
    return pyxel.tilemap(tilemap).pget(tile_x, tile_y)


def detect_collision(x, y, dy):
    x1 = x // 8
    y1 = y // 8
    x2 = (x + 8 - 1) // 8
    y2 = (y + 8 - 1) // 8

    for yi in range(y1, y2 + 1):
        for xi in range(x1, x2 + 1):
            if get_tile(xi, yi)[1] == 2:
                return True
    if dy > 0 and y % 8 == 1:
        for xi in range(x1, x2 + 1):
            if get_tile(xi, y1 + 1)[1] == 1:
                return True
    return False


def correct_distances(x, y, dx, dy):
    abs_dx = abs(dx)
    abs_dy = abs(dy)
    if abs_dx > abs_dy:
        sign = 1 if dx > 0 else -1
        for _ in range(abs_dx):
            if detect_collision(SCROLL_X + x + sign, y, dy):
                break
            x += sign
        sign = 1 if dy > 0 else -1
        for _ in range(abs_dy):
            if detect_collision(SCROLL_X + x, y + sign, dy):
                break
            y += sign
    else:
        sign = 1 if dy > 0 else -1
        for _ in range(abs_dy):
            if detect_collision(SCROLL_X + x, y + sign, dy):
                break
            y += sign
        sign = 1 if dx > 0 else -1
        for _ in range(abs_dx):
            if detect_collision(SCROLL_X + x + sign, y, dy):
                break
            x += sign
    return x, y, dx, dy


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.direction = 0
        self.is_falling = False
        self.is_running = False

        self.speed = 2
        self.jump_power = 6

    def update(self):
        global SCROLL_X

        last_scroll_x = SCROLL_X
        last_x = self.x
        last_y = self.y

        # Déplacements horizontaux
        if pyxel.btn(pyxel.KEY_LEFT):
            self.direction = 1
            if self.x > 32:
                self.dx = -self.speed

            elif SCROLL_X > 0:
                SCROLL_X = max(SCROLL_X - self.speed, 0)

            elif self.x > 0:
                self.dx = -self.speed

        if pyxel.btn(pyxel.KEY_RIGHT):
            self.direction = 0
            if self.x < 80:
                self.dx = self.speed

            elif SCROLL_X < MAX_SCROLL_X:
                SCROLL_X = min(SCROLL_X + self.speed, MAX_SCROLL_X)

            elif self.x < 120:  # frame width - character width
                self.dx = self.speed

        # Sauts
        self.dy = min(self.dy + 1, 3)
        if pyxel.btn(pyxel.KEY_SPACE) and self.dy == 3 and not self.is_falling:
            self.dy = -self.jump_power

        # Mise à jour réelle des valeurs
        self.x, self.y, self.dx, self.dy = correct_distances(self.x, self.y, self.dx, self.dy)

        # Fixe les dépassements du cadre
        if self.y > 120:
            self.y = 120
        if self.x < 0:
            self.x = 0
        if self.x > 120:
            self.x = 120

        self.dx = int(self.dx * 0.8)
        self.is_falling = self.y > last_y
        self.is_running = self.x != last_x or SCROLL_X != last_scroll_x

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 24, 16, 8, 8, 9)


class App:
    def __init__(self):
        self.title = "TITRE"
        self.resources = "assets/2_edit.pyxres"
        self.respawn = [0, (32, 20)]  # [SCROLL_X, (player.x, player.y)]

        self.player = Player(32, 20)

        pyxel.init(128, 128, title=self.title)
        pyxel.load(self.resources)
        pyxel.run(self.update, self.draw)

    def update(self):
        self.player.update()

    def draw(self):
        pyxel.cls(6)

        pyxel.bltm(0, 0, 0, 0, 0, 128, 128, 9)

        self.player.draw()


if __name__ == "__main__":
    App()
