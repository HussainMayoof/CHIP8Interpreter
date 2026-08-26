from random import randint

from display import Display
from keyboard import Keyboard
from memory import Memory


class Register:
    def __init__(self, bits: int) -> None:
        self.size = bits // 8
        self.max = (1 << bits) - 1
        self.value = bytearray(self.size)

    def get_value(self) -> int:
        return int.from_bytes(self.value, byteorder="little")

    def set_value(self, value: int) -> None:
        overflowed = value & self.max
        self.value = bytearray(overflowed.to_bytes(self.size, byteorder="little"))


class Stack:
    def __init__(self) -> None:
        self.stack = []

    def push(self, value: int) -> None:
        self.stack.append(value)

    def pop(self) -> int:
        return self.stack.pop()


class DelayTimer:
    def __init__(self) -> None:
        self.value = 0

    def decrement(self) -> None:
        if self.value > 0:
            self.value -= 1

    def get_value(self) -> int:
        return self.value

    def set_value(self, new_value: int) -> None:
        self.value = new_value


class SoundTimer(DelayTimer):
    def is_playing(self) -> bool:
        return self.value > 0


# pylint: disable=too-many-instance-attributes
class Emulator:
    def __init__(self) -> None:
        self.memory = Memory()
        self.display = Display()
        self.keyboard = Keyboard()
        self.pc = Register(16)
        self.ir = Register(16)
        self.stack = Stack()
        self.dt = DelayTimer()
        self.st = SoundTimer()

        self.registers: list[Register] = [Register(8) for _ in range(16)]

    def get_register(self, address: int) -> int:
        return self.registers[address].get_value()

    def set_register(self, address: int, value: int) -> None:
        self.registers[address].set_value(value)

    def next_instruction(self) -> None:
        self.pc.set_value(self.pc.get_value() + 0x2)

    def load_rom(self, path: str):
        with open(path, "rb") as file:
            rom = file.read()

        for i, byte in enumerate(rom):
            self.memory.write(0x200 + i, byte)

        self.pc.set_value(0x200)

    def fetch(self) -> tuple[int, int, int, int]:
        pc = self.pc.get_value()
        byte1 = self.memory.read(pc)
        byte2 = self.memory.read(pc + 0x1)

        self.next_instruction()

        return byte1 >> 4, byte1 & 0x0F, byte2 >> 4, byte2 & 0x0F

    # pylint: disable=too-many-locals
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements
    def execute(self) -> None:
        nibble1, nibble2, nibble3, nibble4 = self.fetch()

        x = nibble2
        y = nibble3
        n = nibble4
        nn = (nibble3 << 4) + nibble4
        nnn = (nibble2 << 8) + (nibble3 << 4) + nibble4

        match nibble1:
            case 0x0:
                if (
                    nibble2 == 0x0 and nibble3 == 0xE and nibble4 == 0x0
                ):  # clear screen (00E0)
                    self.display.clear()

                if (
                    nibble2 == 0x0 and nibble3 == 0xE and nibble4 == 0xE
                ):  # return from subroutine (00EE)
                    self.pc.set_value(self.stack.pop())

            case 0x1:  # jump (1NNN)
                self.pc.set_value(nnn)

            case 0x2:  # call subroutine (2NNN)
                self.stack.push(self.pc.get_value())
                self.pc.set_value(nnn)

            # skip instructions
            case 0x3:  # (3XNN)
                if self.get_register(x) == nn:
                    self.next_instruction()

            case 0x4:  # (4XNN)
                if self.get_register(x) != nn:
                    self.next_instruction()

            case 0x5:  # (5XY0)
                if self.get_register(x) == self.get_register(y):
                    self.next_instruction()

            case 0x9:  # (9XY0)
                if self.get_register(x) != self.get_register(y):
                    self.next_instruction()

            case 0x6:  # set (6XNN)
                self.set_register(x, nn)

            case 0x7:  # add (7XNN)
                value = self.get_register(x) + nn
                self.set_register(x, value)

            case 0x8:
                match nibble4:
                    case 0x0:  # set (8XY0)
                        self.set_register(x, self.get_register(y))

                    case 0x1:  # or (8XY1)
                        self.set_register(
                            x, self.get_register(x) | self.get_register(y)
                        )

                    case 0x2:  # and (8XY2)
                        self.set_register(
                            x, self.get_register(x) & self.get_register(y)
                        )

                    case 0x3:  # xor (8XY3)
                        self.set_register(
                            x, self.get_register(x) ^ self.get_register(y)
                        )

                    case 0x4:  # add (8XY4)
                        value = self.get_register(x) + self.get_register(y)
                        self.set_register(x, value)
                        if value > 255:
                            self.set_register(0xF, 1)
                        else:
                            self.set_register(0xF, 0)

                    case 0x5:  # subtract (8XY5)
                        x_val = self.get_register(x)
                        y_val = self.get_register(y)
                        value = x_val - y_val
                        self.set_register(x, value)
                        if x_val >= y_val:
                            self.set_register(0xF, 1)
                        else:
                            self.set_register(0xF, 0)

                    case 0x7:  # subtract (8XY7)
                        x_val = self.get_register(x)
                        y_val = self.get_register(y)
                        value = y_val - x_val
                        self.set_register(x, value)
                        if x_val <= y_val:
                            self.set_register(0xF, 1)
                        else:
                            self.set_register(0xF, 0)

                    case 0x6:  # shift right (8XY6)
                        value = self.get_register(y)
                        self.set_register(x, value >> 1)
                        self.set_register(0xF, value & 1)

                    case 0xE:  # shift right (8XYE)
                        value = self.get_register(y)
                        self.set_register(x, value << 1)
                        overflow = 0
                        if value & 0x80:
                            overflow = 1
                        self.set_register(0xF, overflow)

            case 0xA:  # set index (ANNN)
                self.ir.set_value(nnn)

            case 0xB:  # jump with offset (BNNN)
                self.pc.set_value(nnn + self.get_register(0x0))

            case 0xC:  # random (CXNN)
                rand = randint(0, 0xFF)
                self.set_register(x, rand & nn)

            case 0xD:  # display (DXYN)
                x_start = self.get_register(x) % self.display.WIDTH
                y_val = self.get_register(y) % self.display.HEIGHT
                self.set_register(0xF, 0)

                for i in range(n):
                    if y_val >= self.display.HEIGHT:
                        break

                    sprite_byte = self.memory.read(self.ir.get_value() + i)
                    x_val = x_start

                    for j in range(7, -1, -1):
                        if x_val >= self.display.WIDTH:
                            break

                        bit = sprite_byte >> j & 1
                        if bit and self.display.get_pixel(x_val, y_val):
                            self.display.set_pixel(x_val, y_val, 0)
                            self.set_register(0xF, 1)
                        elif bit and not self.display.get_pixel(x_val, y_val):
                            self.display.set_pixel(x_val, y_val, 1)
                        x_val += 1

                    y_val += 1

            case 0xE:
                if nibble3 == 0x9 and nibble4 == 0xE:  # skip if pressed (EX9E)
                    if self.keyboard.is_pressed(self.get_register(x)):
                        self.next_instruction()

                else:  # skip if not pressed (EXA1)
                    if not self.keyboard.is_pressed(self.get_register(x)):
                        self.next_instruction()

            case 0xF:
                if nibble3 == 0x0 and nibble4 == 0x7:  # set VX to delay timer (FX07)
                    self.set_register(x, self.dt.get_value())

                if nibble3 == 0x1 and nibble4 == 0x5:  # set delay timer to VX (FX15)
                    self.dt.set_value(self.get_register(x))

                if nibble3 == 0x1 and nibble4 == 0x8:  # set sound timer to VX (FX18)
                    self.st.set_value(self.get_register(x))

                if nibble3 == 0x1 and nibble4 == 0xE:  # add to index (FX1E)
                    value = self.ir.get_value() + self.get_register(x)
                    if value > 0x0FFF:
                        self.set_register(0xF, 1)
                    else:
                        self.set_register(0xF, 0)
                    self.ir.set_value(value)

                if nibble3 == 0x0 and nibble4 == 0xA:  # get key (FX0A)
                    current = self.keyboard.get_current()
                    if len(current) == 0:
                        self.pc.set_value(self.pc.get_value() - 0x2)
                    else:
                        self.set_register(x, current[0])

                if nibble3 == 0x2 and nibble4 == 0x9:  # font (FX29)
                    self.ir.set_value(
                        self.memory.FONT_START + (self.get_register(x) * 5)
                    )

                if nibble3 == 0x3 and nibble4 == 0x3:  # BCD conversion (FX33)
                    value = self.get_register(x)
                    left = value // 100
                    middle = (value % 100) // 10
                    right = (value % 100) % 10
                    self.memory.write(self.ir.get_value(), left)
                    self.memory.write(self.ir.get_value() + 1, middle)
                    self.memory.write(self.ir.get_value() + 2, right)

                if nibble3 == 0x5 and nibble4 == 0x5:  # store registers (FX55)
                    for i in range(x + 1):
                        self.memory.write(self.ir.get_value() + i, self.get_register(i))

                if nibble3 == 0x6 and nibble4 == 0x5:  # get registers (FX65)
                    for i in range(x + 1):
                        self.set_register(i, self.memory.read(self.ir.get_value() + i))
