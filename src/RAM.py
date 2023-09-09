from MEM import Memory, InvalidAddress

class RAM(Memory):
    """
    Attrs
    -----
    k : int
        2**k is the number of words
    w : int
        Number of memory 'words'
    words : list[int]
        List of memory 'words'
    """
    def __init__(self, k: int):
        self.k: int = k
        self.w: int = 2 ** k
        self.words: list[int] = [0] * self.w

    def is_addr_valid(self, addr: int) -> bool:
        """ Validates address. """
        return self.w > addr >= 0

    def write(self, addr: int, data: int):
        """ Writes data to address. """
        if not self.is_addr_valid(addr): raise InvalidAddress(addr)
        self.words[addr] = data

    def read(self, addr: int) -> int:
        """ Returns data from address. """
        if not self.is_addr_valid(addr): raise InvalidAddress(addr)
        return self.words[addr]
