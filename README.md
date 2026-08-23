# CHIP-8 Interpreter

This is my first emulator-adjacent project.

---

## Features

- Fully designed font created by me
- Currently only supports original CHIP-8 games
- Partial functionality

## ROMs Included

I have included a variety of CHIP-8 ROMs in the `roms` directory taken from the (CHIP-8 Archive)[https://johnearnest.github.io/chip8Archive]

---

## Usage

> **Prerequisites**
> 
> - [uv]([https://www.python.org/downloads/](https://docs.astral.sh/uv/getting-started/installation/))

1. Run `uv sync` to install dependencies
2. Run the following command to start the emulator

```bash
uv run main.py "path-to-rom"
```

---

## Resources Used

I would like to thank the authors of the following materials for their invaluable contribution to this project

- [Guide to making a CHIP-8 emulator](https://tobiasvl.github.io/blog/write-a-chip-8-emulator/#keypad) by Tobias Langhoff
- [SDL Wiki](https://wiki.libsdl.org/SDL3/FrontPage) and [PySDL3](https://github.com/Aermoss/PySDL3)

---

## To Do

- [ ] Add sounds
- [ ] Add GUI
- [ ] Add debugging
- [ ] Add SUPER-CHIP support
- [ ] Add XO-CHIP support
- [ ] 3DS port? (This will probably never happen)