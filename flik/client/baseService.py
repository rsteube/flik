import getpass
from suds.client import Client
from ..common import config, storage
from ..common.util import sessionID


def client():
    return Client(config.load()['url'] + 'BaseService?wsdl')


def login():
    conf = config.load() or config.reconfigure()
    password = getpass.getpass()

    session = client().service.Login(conf['username'], password)
    storage.writeShare('sessionID', session.sessionID)


def logout():
    client().service.Logout(sessionID())
