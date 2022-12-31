# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from typing import Optional

from .ajt_common.addon_config import AddonConfigManager
from .enums import Color


class MorticianConfig(AddonConfigManager):
    def get_flag_code(self) -> Optional[int]:
        if self['flag'] and (color_code := Color.value_of(self['flag'])) != Color.No.value:
            return color_code
        else:
            return None


config = MorticianConfig()
