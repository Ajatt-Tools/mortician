from typing import Optional, Callable

from aqt import mw

from .enums import Color


def init_config():
    _config = mw.addonManager.getConfig(__name__)

    _config['again_threshold']: int = _config.get('again_threshold', 5)
    _config['timeframe']: int = _config.get('timeframe', 24)
    _config['count_from_daystart']: bool = _config.get('count_from_daystart', False)
    _config['again_notify']: bool = _config.get('again_notify', False)
    _config['tag']: str = _config.get('tag', "potential_leech")
    _config['flag']: str = _config.get('flag', "")
    _config['disable_tooltips']: bool = _config.get('disable_tooltips', False)
    _config['ignore_new_cards']: bool = _config.get('ignore_new_cards', False)

    return _config


config = init_config()


def write_config():
    return mw.addonManager.writeConfig(__name__, config)


def set_config_action(fn: Callable):
    return mw.addonManager.setConfigAction(__name__, fn)


def get_flag_code() -> Optional[int]:
    if config['flag'] and (color_code := Color.value_of(config['flag'])) != Color.No.value:
        return color_code
    else:
        return None
