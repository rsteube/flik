from suds.client import Client
from yaml import safe_dump, safe_load
from ..common import config, storage, dateparam
from ..common.util import quote, sessionID


def client():
    return Client(config.load()['url'] + 'WorktimeAccountingService?wsdl')


def syncProjects():
    projects = {}
    for project in client().service.getProjects(sessionID()):
        projects[quote(project.name)] = str(project.projectID)

    storage.writeShare(
        'projects.yaml', safe_dump(
            projects, default_flow_style=False))


def syncTasks():
    tasks = {}
    for projectName, projectID in projects().iteritems():
        tasks[projectName] = {}
        for task in client().service.getTasks(sessionID(), projectID):
            tasks[projectName].update(extractTasks(task))

    storage.writeShare(
        'tasks.yaml', safe_dump(
            tasks, default_flow_style=False))


def extractTasks(task, prefix=''):
    result = {}
    if task.worktimeAllowed:
        result[quote(prefix + task.name)] = str(task.taskID)

    if task.children is not None:
        for x, child in task.children:
            if child is not None:
                for x in child:
                    result.update(extractTasks(x, task.name + '__'))
    return result


def add(date, project, task, activity, billable, duration, comment):
    projectID = projects()[project.decode('utf-8')]
    taskID = tasks()[project.decode('utf-8')][task.decode('utf-8')]
    activityID = activities()[activity]

    comment = ' '.join(comment).decode('utf-8')

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


def copy(from_date, workTimeID, to_date, duration):
    current = client().service.getWorktime(sessionID(), workTimeID)[0]

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


def delete(workTimeID, date):
    client().service.deleteWorktime(sessionID(), workTimeID)


def update(date, workTimeID, duration):
    current = client().service.getWorktime(sessionID(), workTimeID)[0]
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


def activities():
    return safe_load(storage.readShare('activities.yaml'))


def projects():
    return safe_load(storage.readShare('projects.yaml'))


def tasks():
    return safe_load(storage.readShare('tasks.yaml'))
