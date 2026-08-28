import sys
import tkinter.filedialog
from pathlib import Path

import numpy as np
import pygame

from emulator import Emulator
from settings import DEFAULT_SETTINGS

WIDTH, HEIGHT, SCALE = 64, 32, 20
CPU_HZ, TIMER_HZ = 700, 60

BEEP_FREQUENCY, BEEP_AMPLITUDE = 440, 8000


def main(file_name: str, settings) -> None:
    # Get colours from settings
    on_colour = settings["Colours"]["On"]
    off_colour = settings["Colours"]["Off"]
    assert on_colour is not None and isinstance(on_colour, tuple)
    assert off_colour is not None and isinstance(off_colour, tuple)
    on_colour = np.array(on_colour)
    off_colour = np.array(off_colour)

    emulator = Emulator(settings)

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
        rgb = np.where(display[..., None], on_colour, off_colour)
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
    main(file, DEFAULT_SETTINGS)
