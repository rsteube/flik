from yaml import safe_dump, safe_load
from zeep import CachingClient as Client
from zeep.transports import Transport
from ..common import config, storage, dateparam, util
from ..common.util import quote, sessionID
from .baseService import autologin


def client():
    global service
    if not 'service' in globals():
        transport = util.create_https_transport() 
        service =  Client(config.load()['url'] + '/WorktimeAccountingService.wsdl', transport=transport)
        service = client().create_service('{http://blueant.axis.proventis.net/}WorktimeAccountingBinding', address=config.load()['url']+'/services/WorktimeAccountingService')
    return service


@autologin
def syncProjects():
    projects = {}
    for project in client().getProjects(sessionID()):
        projects[quote(project.name)] = {
                'id': str(project.projectID),
                'billable': project.billable}

    storage.writeShare(
        'projects.yaml', safe_dump(
            projects, default_flow_style=False))


@autologin
def syncTasks():
    tasks = {}
    for projectName, x in list(projects().items()):
        tasks[projectName] = {}
        for task in client().getTasks(sessionID(), x['id']):
            tasks[projectName].update(extractTasks(task))

    storage.writeShare(
        'tasks.yaml', safe_dump(
            tasks, default_flow_style=False))

def extractTasks(task, prefix=''):
    result = {}
    if task.worktimeAllowed:
        result[quote(prefix + task.name)] = str(task.taskID)

    if task.children is not None:
        for subTask in task.children.WorkTimeTask:
            result.update(extractTasks(subTask, task.name + '__'))
    return result


@autologin
def add(date, project, task, activity, billable, duration, comment):
    projectID = projects()[project]['id']
    taskID = tasks()[project][task]
    activityID = activities()[activity]

    comment = ' '.join(comment)
    with client()._client.settings(raw_response=True):
        response = client().editWorktime(
            sessionID=sessionID(),
            date=dateparam.format(date[0]),
            projectID=projectID,
            taskID=taskID,
            activityID=activityID,
            duration=(float(duration) * 60 * 60),
            billable=billable,
            comment=comment,
            workTimeID=None)
        assert response.status_code == 200, 'raw_response is not 200'

@autologin
def copy(from_date, workTimeID, to_date, duration):
    current = client().getWorktime(sessionID(), workTimeID)[0]

    with client()._client.settings(raw_response=True):
        client().editWorktime(
            sessionID=sessionID(),
            date=dateparam.format(to_date[0]),
            projectID=current['projectID'],
            taskID=current['taskID'],
            activityID=current['activityID'],
            duration=(float(duration) * 60 * 60),
            billable=current['billable'],
            comment=current['comment'],
            workTimeID=None)


@autologin
def delete(workTimeID, date):
    client().deleteWorktime(sessionID(), workTimeID)


@autologin
def update(date, workTimeID, duration):
    current = client().getWorktime(sessionID(), workTimeID)[0]
    with client()._client.settings(raw_response=True):
        client().editWorktime(
            sessionID(),
            date=current['date'],
            projectID=current['projectID'],
            comment=current['comment'],
            activityID=current['activityID'],
            taskID=current['taskID'],
            billable=current['billable'],
            workTimeID=workTimeID,
            duration=float(duration) * 60 * 60)

@autologin
def move(from_date, workTimeID, to_date):
    current = client().getWorktime(sessionID(), workTimeID)[0]
    
    with client().settings(raw_response=True):
        client().editWorktime(
            sessionID(),
            date=dateparam.format(to_date[0]),
            projectID=current['projectID'],
            comment=current['comment'],
            activityID=current['activityID'],
            taskID=current['taskID'],
            billable=current['billable'],
            workTimeID=workTimeID,
            duration=float(current['duration']) / 1000)


def activities():
    return safe_load(storage.readShare('activities.yaml'))


def projects():
    return safe_load(storage.readShare('projects.yaml'))


def tasks():
    return safe_load(storage.readShare('tasks.yaml'))
