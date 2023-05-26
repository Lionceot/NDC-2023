import pyxel


class App:
    def __init__(self):
        self.title = "TITRE"
        pyxel.init(128, 128, title=self.title)
        pyxel.run(self.update, self.draw)

    def update(self):
        print(self.title)

    def draw(self):
        pass


if __name__ == "__main__":
    App()
