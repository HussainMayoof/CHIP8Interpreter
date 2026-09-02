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

    def scroll_vertical(self, pixels: int) -> None:
        for i in range(self.height - pixels, -1, -1):
            self.screen[i + 1] = self.screen[i]
            self.screen[i] = np.zeros(self.width)  # Blank every row after scrolling it

    def scroll_right(self, pixels: int) -> None:
        for i in range(self.width - pixels, -1, -1):
            self.screen[:, i + 1] = self.screen[:, i]
            self.screen[:, i] = 0  # Blank every column after scrolling it

    def scroll_left(self, pixels: int) -> None:
        for i in range(pixels, self.width, 1):
            self.screen[:, i - 1] = self.screen[:, i]
            self.screen[:, i] = 0  # Blank every column after scrolling it

    def clear(self) -> None:
        self.screen = np.zeros((self.width, self.height))
