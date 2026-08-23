# COSMAC VIP Layout    My Layout
# 1 2 3 C              1 2 3 4
# 4 5 6 D              Q W E R
# 7 8 9 E              A S D F
# A 0 B F              Z X C V

import sdl3 as sdl


class Keyboard:
    def __init__(self) -> None:
        self.layout = [  # scancodes for keys representing values from 0 to f
            27,
            30,
            31,
            32,
            20,
            26,
            8,
            4,
            22,
            7,
            29,
            6,
            33,
            21,
            9,
            25,
        ]

    def get_current(self) -> list[int]:
        keys = sdl.SDL_GetKeyboardState(None)
        keys_pressed = []
        for i, key in enumerate(self.layout):
            if bool(keys[key]):
                keys_pressed.append(i)
        return keys_pressed

    def is_pressed(self, key: int) -> bool:
        keys = sdl.SDL_GetKeyboardState(None)
        return bool(keys[self.layout[key]])
