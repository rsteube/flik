from os import path, makedirs


def writeFile(filename, content):
    full_path = path.expanduser(filename)
    if not path.exists(path.dirname(full_path)):
        makedirs(path.dirname(full_path))
    with open(full_path, 'w') as out:
        out.write(content)


def readFile(filename):
    full_path = path.expanduser(filename)
    if path.isfile(full_path):
        return open(full_path, 'r').read()
    return ''


def writeConfig(filename, content):
    writeFile('~/.config/flik/' + filename, content)


def readConfig(filename):
    return readFile('~/.config/flik/' + filename)


def writeShare(filename, content):
    writeFile('~/.local/share/flik/' + filename, content)


def readShare(filename):
    return readFile('~/.local/share/flik/' + filename)
