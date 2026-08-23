# CHIP-8 Interpreter

This is my first emulator-adjacent project.

---

## Features

- Fully designed font created by me
- Currently only has a few instructions, and can only work with the IBM Logo testing ROM

## ROMs Included

I have included a variety of CHIP-8 ROMs in the `roms` directory, including:

- IBM Logo

---

## Usage

> **Prerequisites**
> 
> - [uv]([https://www.python.org/downloads/](https://docs.astral.sh/uv/getting-started/installation/))

1. Run `uv sync` to install dependencies
2. Run the following command to start the emulator, replacing `"./roms/IBM.ch8"` with the path to your desired ROM

```bash
uv run main.py "./roms/IBM.ch8"
```

---

## Resources Used

I would like to thank the authors of the following materials for their invaluable contribution to this project

- [Guide to making a CHIP-8 emulator](https://tobiasvl.github.io/blog/write-a-chip-8-emulator/#keypad) by Tobias Langhoff