from zeep import CachingClient as Client
from yaml import safe_dump, safe_load
from ..common import config, storage, dateparam
from ..common.util import quote, sessionID
from .baseService import autologin


def client():
    global service
    if not 'service' in globals():
        service =  Client(config.load()['url'] + 'WorktimeAccountingService?wsdl')
    return service


@autologin
def syncProjects():
    projects = {}
    for project in client().service.getProjects(sessionID()):
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
        for task in client().service.getTasks(sessionID(), x['id']):
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
    with client().options(raw_response=True):
        client().service.editWorktime(
            sessionID=sessionID(),
            date=dateparam.format(date[0]),
            projectID=projectID,
            taskID=taskID,
            activityID=activityID,
            duration=(float(duration) * 60 * 60),
            billable=billable,
            comment=comment,
            workTimeID=None)


@autologin
def copy(from_date, workTimeID, to_date, duration):
    current = client().service.getWorktime(sessionID(), workTimeID)[0]

    with client().options(raw_response=True):
        client().service.editWorktime(
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
    client().service.deleteWorktime(sessionID(), workTimeID)


@autologin
def update(date, workTimeID, duration):
    current = client().service.getWorktime(sessionID(), workTimeID)[0]
    with client().options(raw_response=True):
        client().service.editWorktime(
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
    current = client().service.getWorktime(sessionID(), workTimeID)[0]
    
    with client().options(raw_response=True):
        client().service.editWorktime(
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
