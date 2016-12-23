from suds.client import Client
from yaml import safe_dump
from ..common import config, storage
from ..common.util import quote, sessionID


def client():
    return Client(config.load()['url'] + 'MasterDataService?wsdl')


def syncActivities():
    raw_activities = client().service.getActivities(sessionID())

    activities = {}
    for activity in raw_activities:
        activities[quote(activity.name)] = str(activity.activityID)
    storage.writeShare(
        'activities.yaml', safe_dump(
            activities, default_flow_style=False))
