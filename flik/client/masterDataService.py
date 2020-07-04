from zeep import CachingClient as Client
from yaml import safe_dump
from ..common import config, storage, util
from ..common.util import quote, sessionID
from .baseService import autologin


def client():
    transport = util.create_https_transport() 
    return Client(config.load()['url'] + '/MasterDataService.wsdl', transport=transport).create_service('{http://blueant.axis.proventis.net/}MasterDataBinding', address=config.load()['url']+'/services/MasterDataService')


@autologin
def syncActivities():
    raw_activities = client().getActivities(
            sessionID=sessionID(),
            defaultvalue=False)

    activities = {}
    for activity in [x for x in raw_activities if x.active]:
        activities[quote(activity.name)] = str(activity.activityID)
    storage.writeShare(
        'activities.yaml', safe_dump(
            activities, default_flow_style=False))
