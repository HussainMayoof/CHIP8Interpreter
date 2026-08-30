# HelloCHIP

A simple CHIP-8 interpreter/emulator written in Python, intended to be an emulation "Hello World" project.

---

## Features

- Fully designed font created by me
- All original instructions are supported
- Currently only supports original CHIP-8 games
- Partial functionality

## ROMs Included

I have included a variety of CHIP-8 ROMs in the `roms` directory taken from the [CHIP-8 Archive](https://johnearnest.github.io/chip8Archive)

---

## Usage

### Ready Build

You can extract the `.zip` or `.tar.gz` file included in the `Releases` section and run the `exe` file to start the app.

### Run from the Terminal

> **Prerequisites**
> 
> - [uv]([https://www.python.org/downloads/](https://docs.astral.sh/uv/getting-started/installation/))

1. Run `uv sync` to install dependencies
2. Run `uv run main.py "path-to-rom"` to start the emulator, or just run `uv run main.py` and select your ROM from the dialogue
3. You can also access the GUI using `run gui.py`

### Build from Source

> **Prerequisites**
> 
> - [uv]([https://www.python.org/downloads/](https://docs.astral.sh/uv/getting-started/installation/))

_I have not tested this on any platform other than Windows 11_

1. Run `uv sync` to install dependencies
2. Run `uv run pyinstaller gui.spec`
3. The executable file can be found in the `./dist/HelloCHIP` directory

---

## Resources Used

I would like to thank the authors of the following materials for their invaluable contribution to this project

- [Guide to making a CHIP-8 emulator](https://tobiasvl.github.io/blog/write-a-chip-8-emulator/#keypad) by Tobias Langhoff
- [PyQt6 Tutorial](https://www.pythonguis.com/pyqt6-tutorial/) by Martin Fitzpatrick
- [CHIP-8 Test Suite](https://github.com/Timendus/chip8-test-suite) by Timendus and other contributors
- [CHIP-8 Database](https://github.com/chip-8/chip-8-database) by the CHIP-8 Research Facility

## Third-Party Libraries

- [CHIP-8 Database](https://github.com/chip-8/chip-8-database) at `./database`

---

## To Do

- [ ] Add SUPER-CHIP support
- [ ] Add XO-CHIP support