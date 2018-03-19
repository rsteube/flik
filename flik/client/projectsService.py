from zeep import CachingClient as Client
from ..common import config


def client():
    return Client(config.load()['url'] + 'ProjectsService?wsdl')
