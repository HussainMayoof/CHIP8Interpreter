# COSMAC VIP Layout    My Layout
# 1 2 3 C              1 2 3 4
# 4 5 6 D              Q W E R
# 7 8 9 E              A S D F
# A 0 B F              Z X C V

import pygame


class Keyboard:
    def __init__(self) -> None:
        self.layout = [
            pygame.K_x,
            pygame.K_1,
            pygame.K_2,
            pygame.K_3,
            pygame.K_q,
            pygame.K_w,
            pygame.K_e,
            pygame.K_a,
            pygame.K_s,
            pygame.K_d,
            pygame.K_z,
            pygame.K_c,
            pygame.K_4,
            pygame.K_r,
            pygame.K_f,
            pygame.K_v,
        ]

    def get_current(self) -> list[int]:
        keys = pygame.key.get_pressed()
        keys_pressed = []
        for i, key in enumerate(self.layout):
            if bool(keys[key]):
                keys_pressed.append(i)
        return keys_pressed

    def is_pressed(self, key: int) -> bool:
        keys = pygame.key.get_pressed()
        return bool(keys[self.layout[key]])
