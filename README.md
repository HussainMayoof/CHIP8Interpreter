# CHIP-8 Interpreter

This is my first emulator-adjacent project.

---

## Features

- Fully designed font created by me
- Currently only supports original CHIP-8 games
- Partial functionality

## ROMs Included

I have included a variety of CHIP-8 ROMs in the `roms` directory taken from the [CHIP-8 Archive](https://johnearnest.github.io/chip8Archive)

---

## Usage

> **Prerequisites**
> 
> - [uv]([https://www.python.org/downloads/](https://docs.astral.sh/uv/getting-started/installation/))

1. Run `uv sync` to install dependencies
2. Run `uv run main.py "path-to-rom"` to start the emulator, or just run `uv run main.py` and select your ROM from the dialogue
3. (WIP) you can also access the GUI using `run gui.py`

---

## Resources Used

I would like to thank the authors of the following materials for their invaluable contribution to this project

- [Guide to making a CHIP-8 emulator](https://tobiasvl.github.io/blog/write-a-chip-8-emulator/#keypad) by Tobias Langhoff
- [PyQt6 Tutorial](https://www.pythonguis.com/pyqt6-tutorial/) by Martin Fitzpatrick

---

## To Do

- [ ] Fully implement GUI
- [ ] Add debugging
- [ ] Add SUPER-CHIP support
- [ ] Add XO-CHIP support
- [ ] 3DS port? (This will probably never happen)