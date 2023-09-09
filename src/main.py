import sys
from CACHE import SimpleCache, DirectMappedCache, BlockAddress
from CPU import CPU
from IO import IO
from RAM import RAM
from MEM import InvalidAddress

def test() -> None:
    ram = RAM(4)
    cache = DirectMappedCache(2**4, 2, ram)

    start: int = 1
    ram.write(start, 118)
    ram.write(start+1, 130)
    print(ram.words)

    print("READ:", start, cache.read(start))
    print("READ:", start+1, cache.read(start+1))
    print()

    for num, line in enumerate(cache.lines):
        print(f"{bin(num)[2:]} {None if line.tag is None else bin(line.tag)[2:]}: {line.words}")


def test2() -> None:
    ram = RAM(5)
    cache = DirectMappedCache(8, 2, ram)
    
    cache.read(10)
    cache.read(11)

    print()
    for num, line in enumerate(cache.lines):
        print(f"{bin(num)[2:]} {None if line.tag is None else bin(line.tag)[2:]}: {line.words}")

def main() -> None:
    io = IO(sys.stdin, sys.stdout)
    ram = RAM(22)
    cache = DirectMappedCache(4 * 2**10, 64, ram)
    cpu = CPU(cache, io)

    start: int = 0
    ram.write(start, 118)
    ram.write(start+1, 130)

    try:
        print("Program 1")
        ram.write(start, 118)
        ram.write(start + 1, 130)
        cpu.run(start)

        print("\nProgram 2")
        cache.write(start, 4155)
        cache.write(start + 1, 4165)
        cpu.run(start)
    except InvalidAddress as e:
        print(e)


if __name__ == "__main__":
    main()
    # test()