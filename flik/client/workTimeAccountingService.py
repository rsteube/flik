from suds.client import Client
from yaml import safe_dump, safe_load
from ..common import config, storage
from ..common.util import quote, sessionID

def client():
    return Client(config.load()['url'] + 'WorktimeAccountingService?wsdl')

def syncProjects():
    projects = {}
    for project in client().service.getProjects(sessionID()):
        projects[quote(project.name)] = str(project.projectID)
    
    storage.writeShare('projects.yaml', safe_dump(projects, default_flow_style=False))

def syncTasks():
    tasks={}
    for projectName, projectID in projects().iteritems():
        tasks[projectName] = {}
        for task in client().service.getTasks(sessionID(), projectID):
            tasks[projectName].update(extractTasks(task))
    
    storage.writeShare('tasks.yaml', safe_dump(tasks, default_flow_style=False))
  
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
 
def projects():
    return safe_load(storage.readShare('projects.yaml'))
