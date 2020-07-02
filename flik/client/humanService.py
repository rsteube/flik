from zeep import CachingClient as Client
from ..common import config, util


def client():
    transport = util.create_https_transport
    return Client(config.load()['url'] + '/HumanService.wsdl', transport=transport)
