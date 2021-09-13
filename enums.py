from enum import Enum, unique, auto
from typing import Generator


@unique
class ConfigEnum(Enum):
    @classmethod
    def default(cls) -> int:
        for item in cls:
            return item.value

    @classmethod
    def value_of(cls, key: str) -> int:
        key = key.capitalize()
        for item in cls:
            if item.name == key:
                return item.value
        return cls.default()

    @classmethod
    def names(cls) -> Generator[str, None, None]:
        return (item.name for item in cls)

    @classmethod
    def valid_name(cls, name: str) -> str:
        return n if (n := name.capitalize()) in cls.names() else cls.default()


class Color(ConfigEnum):
    """ https://github.com/ankidroid/Anki-Android/wiki/Database-Structure#cards """
    No = 0
    Red = 1
    Orange = 2
    Green = 3
    Blue = 4


class Action(ConfigEnum):
    No = auto()
    Bury = auto()
    Suspend = auto()


def main():
    print(Color.value_of('invalid'))
    print(Color.value_of('Red'))
    print('Red' in Color.names())
    print('Magenta' in Color.names())
    print(Action.value_of('invalid'))
    print(Action.value_of('Bury'))


if __name__ == '__main__':
    main()
