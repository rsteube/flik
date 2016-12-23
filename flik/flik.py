#!/usr/bin/env python2
from .client import baseService, masterDataService, workTimeAccountingService
from .common import dateparam, arguments, config, storage

import os, sys
from yaml import safe_load, safe_dump
from suds import WebFault

import logging
logging.basicConfig(level=logging.CRITICAL)
#logging.basicConfig(level=logging.DEBUG)

def sessionID():
    return storage.readShare('sessionID')

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

def list(date, dump=True):
    workTimes=workTimeAccountingService.client().service.getPersonalWorktime(
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
        'workTimeAccountingService': workTimeAccountingService.client,
        'masterDataService': masterDataService.client
    }[service]()

def sync():
    workTimeAccountingService.syncProjects()
    workTimeAccountingService.syncTasks()
    masterDataService.syncActivities()

def completion():
    return os.path.dirname(os.path.realpath(__file__)) + '/completion/zsh'

def main():
    if len(sys.argv) == 2 and sys.argv[1] == 'completion':
        print completion()
        exit(0)

    try:
        parsed_args = arguments.parse()

	{
	    'login': baseService.login,
	    'projects': projects,
            'tasks': tasks,
            'list': list,
            'comp_list': comp_list,
            'add': workTimeAccountingService.add,
            'api': api,
            'sync': sync,
            'activities': activities,
            'completion': completion,
            'del': workTimeAccountingService.delete,
            'update': workTimeAccountingService.update,
            'logout': baseService.logout,
            'copy': workTimeAccountingService.copy
	}[sys.argv[1]](**parsed_args)
    except WebFault, e:
        try:
            sys.stderr.write(str(e) + '\n')
        except:
            # suds unicode bug
            print 'SESSION_INVALID'

