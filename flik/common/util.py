import logging
from requests import Session
from zeep.transports import Transport

from . import storage
from . import config


def quote(toquote):
    result = toquote
    for character in '& _|()':
        result = result.replace(character, '_')
    return result


def sessionID():
    return storage.readShare('sessionID')


def create_https_transport():
    """
    Uses given config to create transport for https connections.
    If 'verify-cert' (path to a certificate) is given within the config.yaml it will be used to varify the connection.
    """
    session = Session()

    try:
        session.verify = config.load()['verify-cert']
        # disable warnings
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    except KeyError:
        logging.debug("No 'verify-cert' key found in config. Using build in CA chain.")

    return Transport(session=session)  