from display import Display
from memory import Memory


class Register:
    def __init__(self, bits: int) -> None:
        self.size = bits // 8
        self.value = bytearray(self.size)

    def get_value(self) -> int:
        return int.from_bytes(self.value, byteorder="little")

    def set_value(self, value: int) -> None:
        self.value = bytearray(value.to_bytes(self.size, byteorder="little"))

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

class SoundTimer:
    def __init__(self) -> None:
        self.value = 0

    def decrement(self) -> None:
        if self.value > 0:
            self.value -= 1

    def is_playing(self) -> bool:
        return self.value > 0

# pylint: disable=too-many-instance-attributes
class Emulator:
    def __init__(self) -> None:
        self.memory = Memory()
        self.display = Display()
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

        self.pc.set_value(pc + 0x2)

        return byte1 >> 4, byte1 & 0x0f, byte2 >> 4, byte2 & 0x0f

    # pylint: disable=too-many-locals
    # pylint: disable=too-many-branches
    def execute(self) -> None:
        nibble1, nibble2, nibble3, nibble4 = self.fetch()

        x = nibble2
        y = nibble3
        n = nibble4
        nn = (nibble3 << 4) + nibble4
        nnn = (nibble2 << 8) + (nibble3 << 4) + nibble4

        match nibble1:
            case 0x0: # clear screen
                if nibble2 == 0x0 and nibble3 == 0xe and nibble4 == 0x0:
                    self.display.clear()
            case 0x1: # jump
                self.pc.set_value(nnn)
            case 0x6: # set
                self.set_register(x, nn)
            case 0x7: # add
                value = self.get_register(x) + nn
                self.set_register(x, value)
            case 0xa: # set I
                self.ir.set_value(nnn)
            case 0xd: # draw
                x_start = self.get_register(x) % self.display.WIDTH
                y_val = self.get_register(y) % self.display.HEIGHT
                self.set_register(0xf, 0)

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
                            self.set_register(0xf, 1)
                        elif bit and not self.display.get_pixel(x_val, y_val):
                            self.display.set_pixel(x_val, y_val, 1)
                        x_val += 1

                    y_val += 1
