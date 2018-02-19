import getpass, keyring
from functools import wraps
from zeep import CachingClient as Client
from zeep.exceptions import Fault
#from suds import WebFault
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


def autologin(func):

    """Retry with login when session expired."""

    @wraps(func)
    def __wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Fault as e:
            if e.message == 'Ihre Sitzung ist ungültig!':
                login()
                return func(*args, **kwargs)
            else:
                raise e
    return __wrapper
