import typing

class IO:
    def __init__(self, input: typing.IO, output: typing.IO):
        self.input: typing.IO = input
        self.output: typing.IO = output

    def write(self, msg: str) -> None:
        self.output.write(msg)
