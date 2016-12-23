#!/usr/bin/env python2
from .client import baseService
from .common import dateparam, arguments, config, storage

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

def masterDataService():
    return Client(config.load()['url'] + 'MasterDataService?wsdl')

def workTimeAccountingService():
    return Client(config.load()['url'] + 'WorktimeAccountingService?wsdl')

def sessionID():
    return storage.readShare('sessionID')

def loadProjects():
    raw_projects = workTimeAccountingService().service.getProjects(sessionID())

    projects = {}
    for project in raw_projects:
        projects[quote(project.name)] = str(project.projectID)
    storage.writeShare('projects.yaml', safe_dump(projects, default_flow_style=False))

def loadActivities():
    raw_activities = masterDataService().service.getActivities(sessionID())

    activities = {}
    for activity in raw_activities:
        activities[quote(activity.name)] = str(activity.activityID)
    storage.writeShare('activities.yaml', safe_dump(activities, default_flow_style=False))

#TODO rewrite without global variable
alltasks = {}
def loadTasks():
    for projectName, projectID in projects(dump=False).iteritems():
        raw_tasks = workTimeAccountingService().service.getTasks(sessionID(), projectID)
  
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

def login():
    conf = config.load() or config.reconfigure()
    password = getpass.getpass()
    
    session=baseService.client().service.Login(conf['username'], password)
    storage.writeShare('sessionID', session.sessionID)

def logout():
    baseService.client().service.Logout(sessionID())

def activities(dump=True):
    activities = safe_load(storage.readShare('activities.yaml'))
    if dump:
        print '\n'.join(activities.keys())
    return activities


def projects(dump=True):
    projects = safe_load(storage.readShare('projects.yaml'))
    if dump:
        print u'\n'.join(projects.keys()).encode('utf-8')
    return projects

def tasks(project=None, dump=True):
    tasks = safe_load(storage.readShare('tasks.yaml'))
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
    entries = list(date, dump=False)
    for id, entry in entries.iteritems():
        print "{}\:'{:1.160}'".format(id, entry.encode('utf-8'))
    if len(entries) == 1:
        print "none"


def api(service):
    print {
        'baseService': baseService.client,
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

def completion():
    print os.path.dirname(os.path.realpath(__file__)) + '/completion/zsh'

def main():
    if len(sys.argv) == 2 and sys.argv[1] == 'completion':
        completion()
        exit(0)

    try:
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

