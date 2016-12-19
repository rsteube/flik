#!/usr/bin/env python2
from datetime import datetime
from dateutil.relativedelta import relativedelta, MO, TU, WE, TH, FR, SA, SU

from subprocess import call
from yaml import safe_load, safe_dump
import getpass, os, sys
from suds import WebFault
from suds.client import Client

import logging
logging.basicConfig(level=logging.CRITICAL)
#logging.basicConfig(level=logging.DEBUG)

def quote(str):
    return str.replace('&', '_').replace(' ', '_')

def writeFile(filename, content):
    file=os.path.expanduser(filename)
    if not os.path.exists(os.path.dirname(file)):
	os.makedirs(os.path.dirname(file))

    with open(file, 'w') as out:
	out.write(content)

def readFile(filename):
    file=os.path.expanduser(filename)
    return open(file, 'r').read()

def writeShare(filename, content):
    writeFile('~/.local/share/flik/' + filename, content)

def readShare(filename):
    return readFile('~/.local/share/flik/' + filename)

def baseService():
    return Client(config['url'] + 'BaseService?wsdl')

def masterDataService():
    return Client(config['url'] + 'MasterDataService?wsdl')

def workTimeAccountingService():
    return Client(config['url'] + 'WorktimeAccountingService?wsdl')

def sessionID():
    file=os.path.expanduser('~/.local/share/flik/sessionID')
    with open(file, 'r') as loaded:
	return loaded.read()

def loadProjects():
    raw_projects = workTimeAccountingService().service.getProjects(sessionID())

    projects = {}
    for project in raw_projects:
        projects[quote(project.name)] = str(project.projectID)
    writeShare('projects.yaml', safe_dump(projects, default_flow_style=False))

def loadActivities():
    raw_activities = masterDataService().service.getActivities(sessionID())

    activities = {}
    for activity in raw_activities:
        activities[quote(activity.name)] = str(activity.activityID)
    writeShare('activities.yaml', safe_dump(activities, default_flow_style=False))

#TODO rewrite without global variable
alltasks = {}
def loadTasks():
    for projectName, projectID in projects(dump=False).iteritems():
        raw_tasks = workTimeAccountingService().service.getTasks(sessionID(), projectID)
  
        alltasks[projectName] = {}
        for task in raw_tasks:
            extractTasks(projectName, task)
    writeShare('tasks.yaml', safe_dump(alltasks, default_flow_style=False))
  
def extractTasks(projectName, task, prefix=''):
    if task.worktimeAllowed:
        alltasks[projectName][quote(prefix + task.name)] = str(task.taskID)
  
    if task.children is not None:
        for x, child in task.children:
            if child is not None:
                for x in child:
                    extractTasks(projectName, x, task.name + '__')

def login():
    configFile = os.path.expanduser('~/.config/flik/config.yaml')
    if not os.path.isfile(configFile):
        config['url'] = 'https://' + raw_input('URL (https://${URL}/blueant/services): ') + '/blueant/services/'
        config['username'] = raw_input('Username: ')
        writeFile(configFile, safe_dump(config, default_flow_style=False))

    password = getpass.getpass()
    session=baseService().service.Login(config['username'], password)

    writeShare('sessionID', session.sessionID)

def loadConfig():
    configFile = os.path.expanduser('~/.config/flik/config.yaml')
    if not os.path.isfile(configFile):
        return {}
    return safe_load(readFile(configFile))

def activities(dump=True):
    activities = safe_load(readShare('activities.yaml'))
    if dump:
        print '\n'.join(activities.keys())
    return activities


def projects(dump=True):
    projects = safe_load(readShare('projects.yaml'))
    if dump:
        print '\n'.join(projects.keys())
    return projects

def tasks(project=None, dump=True):
    if project is None:
        if len(sys.argv) < 3:
            return
        project = sys.argv[2]

    tasks = safe_load(readShare('tasks.yaml'))
    if dump:
        #TODO use project index
        print '\n'.join(tasks[project].keys())
    return tasks[project]

def del_entry():
    if len(sys.argv) < 4:
            exit(1)
    workTimeAccountingService().service.deleteWorktime(sessionID(), sys.argv[3])

def update_entry():
    if len(sys.argv) < 5:
            exit(1)
    workTimeID=sys.argv[3]
    duration=(float(sys.argv[4])*60*60)

    current=workTimeAccountingService().service.getWorktime(sessionID(), workTimeID)[0]
    workTimeAccountingService().service.editWorktime(
            sessionID(),
            date=current['date'],
            projectID=current['projectID'],
            comment=current['comment'],
            activityID=current['activityID'],
            taskID=current['taskID'],
            billable=current['billable'],
            workTimeID=workTimeID,
            duration=duration)


def list(dump=True):
    date = convertDate(sys.argv[2] if len(sys.argv) > 2 else 'today')

    workTimes=workTimeAccountingService().service.getPersonalWorktime(
            sessionID(),
            fromDate=formatDate(date),
            toDate=formatDate(date + relativedelta(days=1)))

    entries={}
    dayTime=0
    for time in workTimes:
        #print time.date
        project = time.projectName
        task = time.taskName
        workTimeID = time.workTimeID
        comment = time.comment
        time = (float(time.duration) / (1000*60*60))%24
        dayTime+=time
        entries[workTimeID] = u"{:.2f}    {:25.25}    {:25.25}    {:50.50}".format(  time, project  , task, comment)
    if dump:
        print '[%s]' % date
        print '\n'.join(entries.values())
        print '----'
        print dayTime
    return entries

def comp_list():
    for id, entry in list(dump=False).iteritems():
        print "{}\:'{:1.160}'".format(id, entry.encode('utf-8'))

def api():
    print {
        'baseService': baseService,
        'workTimeAccountingService': workTimeAccountingService,
        'masterDataService': masterDataService
    }[sys.argv[2]]()

def convertDate(raw_date):
    try:
        weekday={
                'monday': MO(-1),        
                'tuesday': TU(-1),        
                'wednesday': WE(-1),        
                'thursday': TH(-1),        
                'friday': FR(-1),        
                'saturday': SA(-1),        
                'sunday': SU(-1),        
            }
        if raw_date == 'today':
            date = datetime.now().date()
        elif raw_date == 'yesterday':
            date = datetime.now().date() - relativedelta(days=1)
        elif raw_date in weekday:
            date = datetime.now().date() + relativedelta(weekday=weekday[raw_date])
        else:
            date = datetime.strptime(raw_date, '%Y-%m-%d')
        return date
    except:
        exit(1)

def formatDate(date):
    return date.strftime('%Y-%m-%d')

def sync():
    loadProjects()
    loadTasks()
    loadActivities()

def add_entry():
    date=convertDate(sys.argv[2])
    projectID=projects(dump=False)[sys.argv[3]]
    taskID=tasks(project=sys.argv[3], dump=False)[sys.argv[4]]

    print float(sys.argv[5])

    time=(float(sys.argv[5])*60*60)

    print date
    print projectID
    print taskID
    print time

    print workTimeAccountingService().service.editWorktime(
            sessionID=sessionID(),
            date=formatDate(date),
            projectID=projectID,
            taskID=taskID,
            activityID='9982047',
            duration=time,
            comment='test',
            billable=False,
            workTimeID=None)

def completion():
    print os.path.dirname(os.path.realpath(__file__)) + '/completion/zsh'

def main():
    try:
        global config
        config = {}
        config=loadConfig()

        if len(sys.argv) < 2:
	    print 'fail'
        else:
	    {
		'login': login,
		'projects': projects,
                'tasks': tasks,
                'list': list,
                'comp_list': comp_list,
                'add': add_entry,
                'api': api,
                'sync': sync,
                'activities': activities,
                'completion': completion,
                'del': del_entry,
                'update': update_entry
		}[sys.argv[1]]()
    except WebFault, e:
        sys.stderr.write(str(e) + '\n')

if __name__ == "__main__":
    main()
