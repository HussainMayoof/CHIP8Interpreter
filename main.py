import hashlib
import json
import os
import sys
import tkinter.filedialog
from pathlib import Path
from typing import cast

import numpy as np
import pygame

from emulator import Emulator
from settings import DEFAULT_SETTINGS

TIMER_HZ = 60
TIMER_INTERVAL = 1000 / TIMER_HZ

BEEP_FREQUENCY, BEEP_AMPLITUDE = 440, 8000

SUPPORTED_PLATFORMS = ["originalChip8", "hybridVIP", "modernChip8"]


def resource_path(relative_path: str):
    base_path = cast(
        str, getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    )
    return os.path.join(base_path, relative_path)


def get_game_data(file_name: str):
    with open(file_name, "rb") as f:
        digest = hashlib.file_digest(f, "sha1").hexdigest()

    with open(resource_path("./database/sha1-hashes.json")) as f:
        hashes = json.load(f)

    if not digest in hashes:
        return None

    with open(resource_path("./database/programs.json"), encoding="utf-8") as f:
        programs = json.load(f)

    return programs[int(hashes[digest])]


def get_rom_data(file_name: str):
    with open(file_name, "rb") as f:
        digest = hashlib.file_digest(f, "sha1").hexdigest()

    with open(resource_path("./database/sha1-hashes.json")) as f:
        hashes = json.load(f)

    if not digest in hashes:
        return None

    with open(resource_path("./database/programs.json"), encoding="utf-8") as f:
        programs = json.load(f)

    return programs[int(hashes[digest])]["roms"][digest]


def get_game_settings(file_name: str, settings):
    program_data = get_game_data(file_name)
    rom_data = get_rom_data(file_name)

    if program_data is None or rom_data is None:
        return settings

    platform = ""

    for item in rom_data["platforms"]:
        if item in SUPPORTED_PLATFORMS:
            platform = item
            break

    if platform == "":
        return settings

    with open(resource_path("./database/platforms.json"), encoding="utf-8") as f:
        platforms = json.load(f)

    platform_data = next(
        (item for item in platforms if item["id"] == platform), None
    )

    settings["Quirks"] = platform_data["quirks"]

    if "quirkyPlatforms" in rom_data and platform in rom_data["quirkyPlatforms"]:
        for quirk, value in rom_data["quirkyPlatforms"][platform]:
            settings["Quirks"][quirk] = value

    if "tickrate" in rom_data:
        settings["TickRate"] = rom_data["tickrate"]
    else:
        settings["TickRate"] = platform_data["defaultTickrate"]

    match platform_data["displayResolutions"][-1]:
        case "64x32":
            settings["Width"], settings["Height"], settings["Scale"] = 64, 32, 20
        case "128x64":
            settings["Width"], settings["Height"], settings["Scale"] = 128, 64, 10
        case "256x192":
            settings["Width"], settings["Height"], settings["Scale"] = 256, 192, 5

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

    cpu_hz = settings["TickRate"] * TIMER_HZ
    cpu_interval = 1000 / cpu_hz

    width, height, scale = settings["Width"], settings["Height"], settings["Scale"]

    emulator = Emulator(settings)

    emulator.load_rom(file_name)

    pygame.mixer.pre_init(channels=1, allowedchanges=0)
    pygame.init()

    screen = pygame.display.set_mode(((width * scale), (height * scale)))

    game_data = get_game_data(file_name)
    if get_game_data(file_name):
        pygame.display.set_caption(game_data["title"])
    else:
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
        surface = pygame.transform.scale(surface, (emulator.display.width * scale, emulator.display.height * scale))
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

        while cpu_acc >= cpu_interval:
            emulator.execute()
            cpu_acc -= cpu_interval

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
