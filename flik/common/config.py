from os import path
from yaml import safe_load, safe_dump

configFile = path.expanduser('~/.config/flik/config.yaml')

def load():
    if not path.isfile(configFile):
        return {}
    return safe_load(file(configFile, 'r'))

def reconfigure():
    config = {
            'url': 'https://{}/blueant/services/'.format(raw_input('URL (https://${URL}/blueant/services): ')),
            'username': raw_input('Username: ')
            }
    safe_dump(config, file(configFile, 'w'), default_flow_style=False)
    return load()

