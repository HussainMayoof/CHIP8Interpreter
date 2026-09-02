import numpy as np


class Display:
    def __init__(self, width, height) -> None:
        self.width = width
        self.height = height
        self.screen = np.zeros((self.width, self.height))

    def get_pixel(self, x: int, y: int) -> int:
        return self.screen[x][y]

    def set_pixel(self, x: int, y: int, value: int) -> None:
        self.screen[x][y] = value

    def set_screen(self, new_screen: np.ndarray) -> None:
        self.screen = new_screen

    def clear(self) -> None:
        self.screen = np.zeros((self.width, self.height))
