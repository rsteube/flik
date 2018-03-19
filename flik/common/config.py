from yaml import safe_load, safe_dump
from . import storage


def load():
    return safe_load(storage.readConfig('config.yaml'))


def reconfigure():
    config = {
        'url': 'https://{}/blueant/services/'.format(
            eval(input('URL (https://${URL}/blueant/services): '))),
        'username': eval(input('Username: '))
    }
    storage.writeConfig(
        'config.yaml', safe_dump(
            config, default_flow_style=False))
    return load()
