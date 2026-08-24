import sys
import tkinter.filedialog
from pathlib import Path

import numpy as np
import pygame

from emulator import Emulator

WIDTH, HEIGHT, SCALE = 64, 32, 20
CPU_HZ, TIMER_HZ = 700, 60

ON_COLOR = (255, 255, 255)
OFF_COLOR = (0, 0, 0)

BEEP_FREQUENCY, BEEP_AMPLITUDE = 440, 8000


def main(file_name: str) -> None:
    emulator = Emulator()

    emulator.load_rom(file_name)

    pygame.mixer.pre_init(channels=1, allowedchanges=0)
    pygame.init()

    screen = pygame.display.set_mode(((WIDTH * SCALE), (HEIGHT * SCALE)))
    pygame.display.set_caption(Path(file_name).stem)
    clock = pygame.time.Clock()

    mixer_info = pygame.mixer.get_init()
    if mixer_info is None:
        raise RuntimeError("Failed to initialize pygame mixer")

    freq = mixer_info[0]
    period = freq // BEEP_FREQUENCY
    wave = np.array(
        [BEEP_AMPLITUDE] * (period // 2) + [-BEEP_AMPLITUDE] * (period // 2),
        dtype=np.int16,
    )
    beep = pygame.sndarray.make_sound(wave)

    def draw(display: np.ndarray) -> None:
        rgb = np.where(display[..., None], ON_COLOR, OFF_COLOR)
        surface = pygame.surfarray.make_surface(rgb)
        surface = pygame.transform.scale(surface, (WIDTH * SCALE, HEIGHT * SCALE))
        screen.blit(surface, (0, 0))
        pygame.display.flip()

    last_timer_tick = 0
    timer_interval = 1000 / TIMER_HZ
    running = True

    while running:
        emulator.execute()
        draw(emulator.display.screen)

        elapsed = clock.tick(CPU_HZ)
        last_timer_tick += elapsed
        if last_timer_tick >= timer_interval:
            emulator.dt.decrement()
            emulator.st.decrement()
            last_timer_tick -= timer_interval

        if emulator.st.is_playing():
            if not pygame.mixer.get_busy():
                beep.play(loops=-1)
        else:
            beep.stop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        file = sys.argv[1]
    else:
        file = tkinter.filedialog.askopenfilename()
    main(file)
