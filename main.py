import hashlib
import json
import sys
import tkinter.filedialog
from pathlib import Path

import numpy as np
import pygame

from emulator import Emulator
from settings import DEFAULT_SETTINGS

WIDTH, HEIGHT, SCALE = 64, 32, 20

CPU_HZ, TIMER_HZ = 700, 60
CPU_INTERVAL = 1000 / CPU_HZ
TIMER_INTERVAL = 1000 / TIMER_HZ

BEEP_FREQUENCY, BEEP_AMPLITUDE = 440, 8000

SUPPORTED_PLATFORMS = ["originalChip8", "hybridVIP", "modernChip8"]


def get_game_settings(file_name: str, settings):
    with open(file_name, "rb") as f:
        digest = hashlib.file_digest(f, "sha1").hexdigest()

    with open("./database/sha1-hashes.json") as f:
        hashes = json.load(f)

    if not digest in hashes:
        return settings

    with open("./database/programs.json", encoding="utf-8") as f:
        programs = json.load(f)

    program_data = programs[int(hashes[digest])]
    rom_data = program_data["roms"][digest]

    platform = ""

    for item in rom_data["platforms"]:
        if item in SUPPORTED_PLATFORMS:
            platform = item
            break

    if platform == "":
        return settings

    with open("./database/platforms.json", encoding="utf-8") as f:
        platforms = json.load(f)

    settings["Quirks"] = next(
        (item for item in platforms if item["id"] == platform), None
    )["quirks"]

    if "quirkyPlatforms" in rom_data and platform in rom_data["quirkyPlatforms"]:
        for quirk, value in rom_data["quirkyPlatforms"][platform]:
            settings["Quirks"][quirk] = value

    return settings


def main(file_name: str, settings) -> None:
    # Get colours from settings
    on_colour = settings["Colours"]["On"]
    off_colour = settings["Colours"]["Off"]
    assert on_colour is not None and isinstance(on_colour, tuple)
    assert off_colour is not None and isinstance(off_colour, tuple)
    on_colour = np.array(on_colour)
    off_colour = np.array(off_colour)

    settings = get_game_settings(file_name, settings)

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

    cpu_acc = 0.0
    timer_acc = 0.0
    running = True

    while running:
        elapsed = clock.tick()

        cpu_acc += elapsed
        timer_acc += elapsed

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        while timer_acc >= TIMER_INTERVAL:
            emulator.dt.decrement()
            emulator.st.decrement()
            emulator.display_ready = True
            draw(emulator.display.screen)
            timer_acc -= TIMER_INTERVAL

        while cpu_acc >= CPU_INTERVAL:
            emulator.execute()
            cpu_acc -= CPU_INTERVAL

        if emulator.st.is_playing():
            if not pygame.mixer.get_busy():
                beep.play(loops=-1)
        else:
            beep.stop()

    pygame.quit()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        file = sys.argv[1]
    else:
        file = tkinter.filedialog.askopenfilename()
    main(file, DEFAULT_SETTINGS)
