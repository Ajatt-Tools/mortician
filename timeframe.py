# -*- coding: utf-8 -*-

# Mortician add-on for Anki 2.1
# Copyright (C) 2021  Ren Tatsumoto. <tatsu at autistici.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Any modifications to this file must keep this entire header intact.

class TimeFrame:
    def __init__(self, hours: float = 0, seconds: float = 0, milliseconds: float = 0):
        self._milliseconds = milliseconds + self.seconds_to_milliseconds(seconds) + self.hours_to_milliseconds(hours)

    @classmethod
    def seconds_to_milliseconds(cls, seconds: float) -> float:
        return seconds * 1000

    @classmethod
    def hours_to_milliseconds(cls, hours: float) -> float:
        return cls.seconds_to_milliseconds(hours * 60 * 60)

    @classmethod
    def milliseconds_to_hours(cls, milliseconds: float) -> float:
        return milliseconds / 1000.0 / 3600.0

    def __sub__(self, other: 'TimeFrame') -> 'TimeFrame':
        return TimeFrame(milliseconds=self._milliseconds - other._milliseconds)

    def __add__(self, other: 'TimeFrame') -> 'TimeFrame':
        return TimeFrame(milliseconds=self._milliseconds + other._milliseconds)

    def milliseconds(self) -> int:
        return int(self._milliseconds)

    def hours(self) -> int:
        return int(self.milliseconds_to_hours(self._milliseconds))
