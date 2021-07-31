import functools

from aqt import mw


def init_config():
    _config = mw.addonManager.getConfig(__name__)

    _config['again_threshold']: int = _config.get('again_threshold', 5)
    _config['timeframe']: int = _config.get('timeframe', 24)
    _config['count_from_daystart']: bool = _config.get('count_from_daystart', False)
    _config['again_notify']: bool = _config.get('again_notify', False)
    _config['tag']: str = _config.get('tag', "potential_leech")
    _config['flag']: str = _config.get('flag', "")
    _config['disable_tooltips']: bool = _config.get('disable_tooltips', False)
    _config['no_bury']: bool = _config.get('no_bury', False)
    _config['ignore_new_cards']: bool = _config.get('ignore_new_cards', False)

    return _config


config = init_config()
write_config = functools.partial(mw.addonManager.writeConfig, module=__name__, conf=config)
