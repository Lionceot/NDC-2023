import pyxel


class App:
    def __init__(self):
        self.title = ""
        pyxel.init(128, 128, title=self.title)
        pyxel.run(self.update, self.draw)

    def update(self):
        pass

    def draw(self):
        pass


if __name__ == "__main__":
    App()
