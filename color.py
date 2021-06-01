from enum import Enum
from typing import Generator


class Color(Enum):
    No = 0
    Red = 1
    Orange = 2
    Green = 3
    Blue = 4

    @classmethod
    def num_of(cls, color: str) -> int:
        for item in cls:
            if item.name == color:
                return item.value
        return cls.No.value

    @classmethod
    def colors(cls) -> Generator[str, None, None]:
        return (item.name for item in cls)
