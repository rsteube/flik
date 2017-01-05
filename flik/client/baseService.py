import getpass, keyring
from suds.client import Client
from ..common import config, storage
from ..common.util import sessionID


def client():
    return Client(config.load()['url'] + 'BaseService?wsdl')


def login():
    username = (config.load() or config.reconfigure())['username']
    password = keyring.get_password('flik', username) or getpass.getpass()

    session = client().service.Login(username, password)
    storage.writeShare('sessionID', session.sessionID)
    keyring.set_password('flik', username, password)


def logout():
    keyring.delete_password('flik', config.load()['username'])
    client().service.Logout(sessionID())
