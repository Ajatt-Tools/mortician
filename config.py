# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from .ajt_common.addon_config import AddonConfigManager
from .enums import Color, Action


class MorticianConfig(AddonConfigManager):
    @property
    def flag(self) -> Color:
        if (name := self['flag'].capitalize()) in Color.names():
            return Color[name]
        else:
            return Color.default()

    @property
    def action(self) -> Action:
        if (name := self['action'].capitalize()) in Action.names():
            return Action[name]
        else:
            return Action.default()


config = MorticianConfig()
