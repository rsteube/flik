from suds.client import Client
from yaml import safe_dump, safe_load
from ..common import config, storage
from ..common.util import quote, sessionID

def client():
    return Client(config.load()['url'] + 'WorktimeAccountingService?wsdl')

def syncProjects():
    raw_projects = client().service.getProjects(sessionID())
    projects = {}
    for project in raw_projects:
        projects[quote(project.name)] = str(project.projectID)
    storage.writeShare('projects.yaml', safe_dump(projects, default_flow_style=False))


#TODO rewrite without global variable
alltasks = {}
def syncTasks():
    for projectName, projectID in projects().iteritems():
        raw_tasks = client().service.getTasks(sessionID(), projectID)
    
        alltasks[projectName] = {}
        for task in raw_tasks:
            extractTasks(projectName, task)
    storage.writeShare('tasks.yaml', safe_dump(alltasks, default_flow_style=False))
  
def extractTasks(projectName, task, prefix=''):
    if task.worktimeAllowed:
        alltasks[projectName][quote(prefix + task.name)] = str(task.taskID)
  
    if task.children is not None:
        for x, child in task.children:
            if child is not None:
                for x in child:
                    extractTasks(projectName, x, task.name + '__')
 
def projects():
    return safe_load(storage.readShare('projects.yaml'))
