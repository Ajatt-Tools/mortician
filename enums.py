from enum import Enum, unique, auto
from typing import Generator


@unique
class ConfigEnum(Enum):
    @classmethod
    def default(cls) -> Enum:
        for item in cls:
            return item

    @classmethod
    def value_of(cls, name: str) -> int:
        name = name.capitalize()
        for item in cls:
            if item.name == name:
                return item.value
        return cls.default().value

    @classmethod
    def names(cls) -> Generator[str, None, None]:
        return (item.name for item in cls)

    @classmethod
    def valid_name(cls, name: str) -> str:
        return n if (n := name.capitalize()) in cls.names() else cls.default().name


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
    print("Color.value_of('invalid')", Color.value_of('invalid'))
    print("Color.value_of('Red')", Color.value_of('Red'))
    print("'Red' in Color.names()", 'Red' in Color.names())
    print("'Magenta' in Color.names()", 'Magenta' in Color.names())
    print("Action.value_of('invalid')", Action.value_of('invalid'))
    print("Action.value_of('Bury')", Action.value_of('Bury'))
    print('Action.Bury.name', Action.Bury.name)


if __name__ == '__main__':
    main()
