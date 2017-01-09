from . import storage


def quote(toquote):
    result = toquote
    for character in '& _|()':
        result = result.replace(character, '_')
    return result.lower()


def sessionID():
    return storage.readShare('sessionID')
