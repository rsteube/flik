#!/usr/bin/env python2
from .common import dateparam, arguments

from subprocess import call
from yaml import safe_load, safe_dump
import getpass, os, sys
from suds import WebFault
from suds.client import Client

import logging
logging.basicConfig(level=logging.CRITICAL)
#logging.basicConfig(level=logging.DEBUG)

def quote(toquote):
    result = toquote
    for character in '& _|':
        result = result.replace(character, '_')
    return result

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

def logout():
    baseService().service.Logout(sessionID())

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
        print u'\n'.join(projects.keys()).encode('utf-8')
    return projects

def tasks(project=None, dump=True):
    tasks = safe_load(readShare('tasks.yaml'))
    if dump:
        #TODO use project index
        print u'\n'.join(tasks[project.decode('utf-8')].keys()).encode('utf-8')
    return tasks[project.decode('utf-8')]

def del_entry(workTimeID, date='ignored'):
    workTimeAccountingService().service.deleteWorktime(sessionID(), workTimeID)

def update_entry(date, workTimeID, duration):
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
            duration=float(duration)*60*60)


def list(date, dump=True):
    workTimes=workTimeAccountingService().service.getPersonalWorktime(
            sessionID(),
            fromDate=dateparam.format(date[0]),
            toDate=dateparam.format(date[1]))

    entries={}
    entries_by_date={}
    dayTime={}
    for workTime in workTimes:
        #print time.date
        project = workTime.projectName
        task = workTime.taskName
        workTimeID = workTime.workTimeID
        comment = workTime.comment
        billable = '$' if workTime.billable else ' '
        time = (float(workTime.duration) / (1000*60*60))%24
        state = {0: ' ', # open
                 1: 'L', # locked
                 2: 'X', # rejected?
                 }[workTime.state]

        if not workTime.date in entries_by_date.keys():
            entries_by_date[workTime.date]={}
            dayTime[workTime.date]=0
        dayTime[workTime.date]+=time
        
        entries_by_date[workTime.date][workTimeID] = entries[workTimeID] = u"{:.2f} {}{}  {:25.25}  {:25.25}  {:80.80}".format(time, billable, state, project, task, comment)
    if dump:
        for date, entries_for_date in sorted(entries_by_date.iteritems()):
            print '[%s]' % date.strftime('%Y-%m-%d %a')
            print '\n'.join(entries_for_date.values())
            print '-----'
            print dayTime[date]
            print ''
        if len(dayTime.values()) > 1:
            print '====='
            print sum(dayTime.values())
    return entries

def comp_list(date):
    for id, entry in list(date, dump=False).iteritems():
        print "{}\:'{:1.160}'".format(id, entry.encode('utf-8'))

def api(service):
    print {
        'baseService': baseService,
        'workTimeAccountingService': workTimeAccountingService,
        'masterDataService': masterDataService
    }[service]()

def sync():
    loadProjects()
    loadTasks()
    loadActivities()

def copy_entry(from_date, workTimeID, to_date, duration):
    current=workTimeAccountingService().service.getWorktime(sessionID(),workTimeID)[0]
    
    workTimeAccountingService().service.editWorktime(
            sessionID=sessionID(),
            date=dateparam.format(to_date[0]),
            projectID=current['projectID'],
            taskID=current['taskID'],
            activityID=current['activityID'],
            duration=(float(duration)*60*60),
            billable=current['billable'],
            comment=current['comment'],
            workTimeID=None)


def add_entry(date, project, task, activity, billable, duration, comment):
    projectID=projects(dump=False)[project.decode('utf-8')]
    taskID=tasks(project=project.decode('utf-8'), dump=False)[task.decode('utf-8')]

    activityID=activities(dump=False)[activity]
    billable={'billable': True,
              'non_billable': False
              }[billable]
    comment=' '.join(comment).decode('utf-8')

    workTimeAccountingService().service.editWorktime(
            sessionID=sessionID(),
            date=dateparam.format(date[0]),
            projectID=projectID,
            taskID=taskID,
            activityID=activityID,
            duration=(float(duration)*60*60),
            billable=billable,
            comment=comment,
            workTimeID=None)

    print {'project': project, 'task': task, 'activity': activity, 'billable': billable, 'comment': comment}

def completion():
    print os.path.dirname(os.path.realpath(__file__)) + '/completion/zsh'

def main():
    try:
        global config
        config = {}
        config=loadConfig()

        parsed_args = arguments.parse()

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
            'update': update_entry,
            'logout': logout,
            'copy': copy_entry
	}[sys.argv[1]](**parsed_args)
    except WebFault, e:
        try:
            sys.stderr.write(str(e) + '\n')
        except:
            # suds unicode bug
            print 'SESSION_INVALID'

