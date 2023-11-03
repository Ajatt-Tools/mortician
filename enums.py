# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import enum
from collections.abc import Iterable


@enum.unique
class ConfigEnum(enum.Enum):
    @classmethod
    def default(cls):
        return next(item for item in cls)

    @classmethod
    def names(cls) -> Iterable[str]:
        return (item.name for item in cls)


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
    print("Color(1)", Color(1))
    print("'Red' in Color.names()", 'Red' in Color.names())
    print("'Magenta' in Color.names()", 'Magenta' in Color.names())
    print('Action.Bury.name', Action.Bury.name)


if __name__ == '__main__':
    main()
