import getpass, keyring
from functools import wraps
from zeep import CachingClient as Client
from zeep.exceptions import Fault
from ..common import config, storage
from ..common.util import sessionID
from zeep.transports import Transport


def client():
    transport = Transport()
    transport.session.verify = False
    return Client(config.load()['url'] + 'BaseService.wsdl', transport=transport)


def login():
    username = (config.load() or config.reconfigure())['username']
    password = keyring.get_password('flik', username) or getpass.getpass()

    session = client().create_service('{http://blueant.axis.proventis.net/}BaseBinding', address='https://demosystem.blueant.cloud/services/BaseService').Login(username, password)
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
        except AssertionError as e:
            # temporary workaround until zeep raw_response is not necessary anymore
            login()
            return func(*args, **kwargs)
        except Fault as e:
            if e.message == 'Ihre Sitzung ist ungültig!':
                login()
                return func(*args, **kwargs)
            else:
                raise e
    return __wrapper
