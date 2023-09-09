from abc import ABC, abstractmethod


class Memory(ABC):
    @abstractmethod
    def write(self, addr: int, data: int): ...

    @abstractmethod
    def read(self, addr: int): ...


class InvalidAddress(Exception):
    def __init__(self, addr: int):
        self.addr: int = addr

    def __str__(self) -> str:
        return f"Invalid Address: {self.addr}"
