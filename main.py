import ctypes
import sys
import time

import numpy as np
import sdl3 as sdl

from emulator import Emulator

WIDTH, HEIGHT, SCALE = 64, 32, 10
CPU_HZ, TIMER_HZ = 700, 60


def main() -> None:
    sdl.SDL_Init(sdl.SDL_INIT_VIDEO)
    window = sdl.SDL_CreateWindow(
        ctypes.c_char_p(b"CHIP-8 Interpreter"),
        ctypes.c_int(WIDTH * SCALE),
        ctypes.c_int(HEIGHT * SCALE),
        0,
    )
    renderer = sdl.SDL_CreateRenderer(window, ctypes.c_char_p(None))

    emulator = Emulator()
    emulator.load_rom(sys.argv[1])

    def draw(screen: np.ndarray) -> None:
        sdl.SDL_SetRenderDrawColor(
            renderer,
            ctypes.c_ubyte(0),
            ctypes.c_ubyte(0),
            ctypes.c_ubyte(0),
            ctypes.c_ubyte(255),
        )
        sdl.SDL_RenderClear(renderer)
        sdl.SDL_SetRenderDrawColor(
            renderer,
            ctypes.c_ubyte(255),
            ctypes.c_ubyte(255),
            ctypes.c_ubyte(255),
            ctypes.c_ubyte(255),
        )

        for x in range(WIDTH):
            for y in range(HEIGHT):
                if screen[x][y]:
                    rect = sdl.SDL_FRect(x * SCALE, y * SCALE, SCALE, SCALE)
                    sdl.SDL_RenderFillRect(renderer, ctypes.byref(rect))

        sdl.SDL_RenderPresent(renderer)

    last_timer_tick = time.time()
    cpu_interval = 1 / CPU_HZ
    timer_interval = 1 / TIMER_HZ
    running = True
    event = sdl.SDL_Event()

    while running:
        while sdl.SDL_PollEvent(ctypes.byref(event)):
            if event.type == sdl.SDL_EVENT_QUIT:
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

        time.sleep(cpu_interval)

    sdl.SDL_DestroyRenderer(renderer)
    sdl.SDL_DestroyWindow(window)
    sdl.SDL_Quit()


if __name__ == "__main__":
    main()
