# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from .ajt_common.addon_config import AddonConfigManager
from .enums import Action, Color


class MorticianConfig(AddonConfigManager):
    @property
    def flag(self) -> Color:
        try:
            return Color[self["flag"].capitalize()]
        except KeyError:
            return Color.default()

    @property
    def action(self) -> Action:
        try:
            return Action[self["action"].capitalize()]
        except KeyError:
            return Action.default()


config = MorticianConfig()
