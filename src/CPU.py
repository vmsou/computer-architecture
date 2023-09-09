from MEM import Memory
from IO import IO    

class CPU:
    """
    Attrs
    -----
    mem : Memory
        Main Memory
    io : IO
        Access to Input and Output
    PC : int
        Program Counter
    A : int
    B : int
    C : int
        Processor registers
    """
    def __init__(self, mem: Memory, io: IO):
        self.PC: int = 0
        self.mem: Memory = mem
        self.io: IO = io
        self.A = self.B = self.C = 0

    def read(self) -> int:
        """ Reads memory with program counter, then increments PC """
        w: int = self.mem.read(self.PC)
        self.PC += 1
        return w

    def program(self) -> None:
        self.A = self.read()
        self.B = self.read()

        self.C = 1
        while self.A <= self.B:
            self.mem.write(self.A, self.C)
            self.io.write(f"> {self.A} = {self.C}\n")
            self.C += 1
            self.A += 1
            
    def run(self, addr: int) -> None:
        """ Runs program from address. """
        self.PC = addr
        self.program()