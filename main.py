import sys
import time
import tkinter.filedialog

import numpy as np
import pygame

from emulator import Emulator

WIDTH, HEIGHT, SCALE = 64, 32, 20
CPU_HZ, TIMER_HZ = 700, 60

ON_COLOR = (255, 255, 255)
OFF_COLOR = (0, 0, 0)


def main() -> None:
    pygame.init()

    screen = pygame.display.set_mode(((WIDTH * SCALE), (HEIGHT * SCALE)))
    pygame.display.set_caption("CHIP-8 Interpreter")
    clock = pygame.time.Clock()

    emulator = Emulator()

    if len(sys.argv) > 1:
        emulator.load_rom(sys.argv[1])
    else:
        emulator.load_rom(tkinter.filedialog.askopenfilename())

    def draw(display: np.ndarray) -> None:
        rgb = np.where(display[..., None], ON_COLOR, OFF_COLOR)
        surface = pygame.surfarray.make_surface(rgb)
        surface = pygame.transform.scale(surface, (WIDTH * SCALE, HEIGHT * SCALE))
        screen.blit(surface, (0, 0))
        pygame.display.flip()

    last_timer_tick = time.time()
    timer_interval = 1 / TIMER_HZ
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        emulator.execute()
        draw(emulator.display.screen)

        now = time.time()
        if now - last_timer_tick >= timer_interval:
            emulator.dt.decrement()
            emulator.st.decrement()
            last_timer_tick = now

        if emulator.st.is_playing():
            print("Beep")

        clock.tick(CPU_HZ)


if __name__ == "__main__":
    main()
