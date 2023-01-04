# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import enum
from typing import Iterable


@enum.unique
class ConfigEnum(enum.Enum):
    @classmethod
    def default(cls) -> enum.Enum:
        return next(item for item in cls)

    @classmethod
    def value_of(cls, name: str) -> int:
        name = name.capitalize()
        for item in cls:
            if item.name == name:
                return item.value
        return cls.default().value

    @classmethod
    def names(cls) -> Iterable[str]:
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
    No = enum.auto()
    Bury = enum.auto()
    Suspend = enum.auto()


def main():
    print("Action['Bury']", Action['Bury'])
    print("Color.value_of('invalid')", Color.value_of('invalid'))
    print("Color.value_of('Red')", Color.value_of('Red'))
    print("'Red' in Color.names()", 'Red' in Color.names())
    print("'Magenta' in Color.names()", 'Magenta' in Color.names())
    print("Action.value_of('invalid')", Action.value_of('invalid'))
    print("Action.value_of('Bury')", Action.value_of('Bury'))
    print('Action.Bury.name', Action.Bury.name)


if __name__ == '__main__':
    main()
