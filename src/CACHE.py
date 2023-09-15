from abc import ABC, abstractmethod
import math

from MEM import Memory, InvalidAddress
from RAM import RAM


class Cache(Memory, ABC):
    """
    Attrs
    -----
    w : int
        Number of memory 'words'
    ram : RAM
        Direct access to Random Access Memory
    """
    def __init__(self, w: int, ram: RAM):
        self.w: int = w
        self.ram: RAM = ram


    @abstractmethod
    def is_cache_hit(self, addr: int) -> bool: ...


class SimpleCache(Cache):
    """
    Attrs
    -----
    w : int
        Number of total memory 'words'
    ram : RAM
        Direct access to Random Access Memory
    starting_addr: int
        Index of starting memory block
    modified: bool
        Flag that indicates whether cache was modified
    """
    def __init__(self, w: int, ram: RAM):
        super().__init__(w, ram)

        self.words: list[int] = [0] * self.w
        self.starting_addr: int = 0
        self.modified: bool = False

    def is_cache_hit(self, addr: int) -> bool:
        """ Checks whether address is within cache block """
        if not self.ram.is_addr_valid(addr): raise InvalidAddress(addr)
        return self.starting_addr <= addr < (self.starting_addr + self.w)

    def copy_cache_to_ram(self):
        """ Saves cache to RAM """
        if not self.modified: return
        for value, addr in enumerate(self.words, start=self.starting_addr):
            self.ram.write(addr, value)
        self.modified = False

    def copy_ram_to_cache(self, addr):
        """ Copies RAM to cache """
        i = 0
        self.starting_addr = addr
        for addr in range(addr, addr + self.w):
            if not self.ram.is_addr_valid(addr): break
            value: int = self.ram.read(addr)
            self.words[i] = value
            i += 1

    def write(self, addr: int, data: int):
        """ 
        Writes data to cache
        If miss: Saves cache to RAM and updates cache to match RAM (for new address)
        """
        if not self.is_cache_hit(addr):
            print("CACHE (Write) Miss:", addr)
            self.copy_cache_to_ram()
            self.copy_ram_to_cache(addr)
        else:
            print("CACHE (Write) Hit:", addr)
        self.words[addr - self.starting_addr] = data
        self.modified = True

    def read(self, addr: int) -> int:
        """ 
        Reads data from memory
        If cache miss: copies cache to RAM and updates cache to match RAM (for new address)
        """
        if not self.is_cache_hit(addr): 
            print("CACHE (Read) Miss:", addr)
            self.copy_cache_to_ram()
            self.copy_ram_to_cache(addr)
        else:
            print("CACHE: (Read) Hit:", addr)
        return self.words[addr - self.starting_addr]
    

class BlockAddress:
    """
    Attrs
    -----
    w: int
        Position inside cache line
    r: int
        Position of cache line
    t: int
        Tag of cache line. Identifies which block cache line is from
    k : int 
        Number of memory 'words' of each block
    m : int
        Number of blocks (cache lines)
    s: int
        Number of main memory's block (t + r)

    """
    def __init__(self, t: int, r: int, w: int, k: int, m: int):
        self.t: int = t
        self.r: int = r
        self.w: int = w

        self.k: int = k
        self.m: int = m

        t, r, w = repr(self).split()
        self.s = int(t + r, 2)

    def __repr__(self) -> str:
        """ Represents as binary numbers """
        # b_bits = math.log2(blocos da ram / linhas da cache)
        w_bits: int = int(math.log2(self.k))
        r_bits: int = int(math.log2(self.m))
        # t_bits: int = total_bits - w_bits - r_bits

        t = bin(self.t)[2:]
        r = bin(self.r)[2:]
        w = bin(self.w)[2:]

        # t = "0" * (t_bits - len(t)) + t
        r = "0" * (r_bits - len(r)) + r
        w = "0" * (w_bits - len(w)) + w

        return f"{t} {r} {w}"

    def __str__(self) -> str:
        """ Represents as separated integers """
        return f"{self.t} {self.r} {self.w}"
    
    def __int__(self) -> int:
        return int(repr(self).replace(" ", ""), 2)
    
    @property
    def start_addr(self) -> int:
        return self.s * self.k
    
    @property
    def end_addr(self) -> int:
        return self.start_addr + self.k

    @classmethod
    def from_bits(cls, addr: int, k: int, m: int) -> 'BlockAddress':
        last_n_bits = lambda num, n: num & ((1 << n) - 1)
        
        size = 1 if addr == 0 else int(math.log2(addr) + 1)

        w_bits = int(math.log2(k))
        r_bits: int = int(math.log2(m))
        t_bits = size - w_bits - r_bits
        s_bits = t_bits + r_bits
   
        s = addr >> (size - s_bits)
        t = s >> (s_bits - t_bits)
        r = last_n_bits(s, r_bits)
        w = last_n_bits(addr, w_bits)
        return BlockAddress(t, r, w, k, m)
    
    @classmethod
    def from_bin(cls, b: str, k: int, m: int) -> 'BlockAddress':
        return BlockAddress.from_bits(int(bin(b), 2), k, m)

class CacheLine:
    """
    Attrs
    -----
    tag : int
        Identifies main memory being stored
    k : int
        Cache line size (Number of 'words')
    words : list[int]
        List of words
    """

    def __init__(self, tag: int, k: int):
        self.tag: int = tag
        self.modif: bool = False
        self.k = k
        self.words: list[int] = [0] * self.k


class DirectMappedCache(Cache):
    """
    Attrs
    -----
    w : int
        Number of total memory 'words'
    k : int
        Number of memory 'words' of each block
    m : int
        Number of cache lines (w / k)
    
    ram: RAM
        Direct access to Random Access Memory
    lines: list[CacheLine]
        Cache Lines
    """

    def __init__(self, w: int, k: int, ram: RAM):
        super().__init__(w, ram)
        self.k: int = k
        self.m: int = int(self.w / self.k)

        # total address bits = log2 ram.w (MAR)
        self.lines: list[CacheLine] = [CacheLine(None, k) for i in range(self.m)]

    def is_cache_hit(self, addr: int) -> bool:
        """ Checks whether address is within cache lines """
        block_addr: BlockAddress = BlockAddress.from_bits(addr, self.k, self.m)
        line_num: int = block_addr.r
        #print("BLOCK NUM:", block_addr.s)
        #print("LINE NUM:", line_num)
        if line_num >= len(self.lines):
            return False
        # print(block_addr.t, "==", self.lines[block_addr.t].tag)
        return block_addr.t == self.lines[line_num].tag

    def copy_cache_line_to_ram(self, block_addr: BlockAddress) -> None:
        """ If cache line is modified, copies line to main memory. """
        line_num: int = block_addr.r
        line: CacheLine = self.lines[line_num]
        if not line.modif: return

        old_block = BlockAddress(line.tag, block_addr.r, 0, self.k, self.m)
        print(f"L{block_addr.r}->[{old_block.start_addr}..{old_block.end_addr - 1}] | ", end='')
        
        start_addr: int = block_addr.start_addr
        for i in range(self.k):
            word = line.words[i]
            self.ram.write(start_addr + i, word)
    
        line.modif = False

    def copy_ram_line_to_cache(self, block_addr: BlockAddress):
        """ Reserves cache line for block. """
        line_num: int = block_addr.r
        line: CacheLine = self.lines[line_num]
        line.tag = block_addr.t
        start_addr: int = block_addr.start_addr

        for i in range(self.k):
            line.words[i] = self.ram.read(start_addr + i)

        print(f"[{start_addr}..{block_addr.end_addr - 1}]->L{block_addr.r}")

    def read(self, addr: int) -> int:
        block_addr = BlockAddress.from_bits(addr, self.k, self.m)
        if not self.is_cache_hit(addr):
            print(f"MISS: {addr} ", end='')
            self.copy_cache_line_to_ram(block_addr)
            self.copy_ram_line_to_cache(block_addr)
        
        line: CacheLine = self.lines[block_addr.r]
        return line.words[block_addr.w]

    def write(self, addr: int, data: int) -> None:
        block_addr = BlockAddress.from_bits(addr, self.k, self.m)
        
        if not self.is_cache_hit(addr):
            print(f"MISS: {addr} ", end='')
            self.copy_cache_line_to_ram(block_addr)
            self.copy_ram_line_to_cache(block_addr)
        else:
            # print("WRITE HIT:", repr(block_addr), f"({int(block_addr)})")
            ...
        
        line: CacheLine = self.lines[block_addr.r]
        line.modif = True
        line.words[block_addr.w] = data

def main() -> None:
    X = 10_560_325
    K = 32
    cache_total_capacity = 4096
    M = int(cache_total_capacity / 32)

    block_addr = BlockAddress.from_bits(X, K, M)
    print(block_addr)
    print(repr(block_addr))
    print(int(block_addr))

    start = X - (X % K)
    end = start + K - 1

    print("1.", block_addr.w)
    print("2.", block_addr.r)
    print("3.", block_addr.t)
    print(f"4. {start}-{end}")

if __name__ == "__main__":
    main()
