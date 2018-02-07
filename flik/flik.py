#!/usr/bin/env python2
import os, sys
import logging

logging.basicConfig(level=logging.CRITICAL)

def sessionID():
    from .common import storage
    return storage.readShare('sessionID')


def activities(dump=True):
    from yaml import safe_load
    from .common import storage

    activities = safe_load(storage.readShare('activities.yaml'))
    if dump:
        print '\n'.join(activities.keys())
    return activities


def projects(dump=True):
    from yaml import safe_load
    from .common import storage

    projects = safe_load(storage.readShare('projects.yaml'))
    if dump:
        print u'\n'.join(projects.keys()).encode('utf-8')
    return projects


def tasks(project=None, dump=True):
    from yaml import safe_load
    from .common import storage

    tasks = safe_load(storage.readShare('tasks.yaml'))
    if dump:
        #TODO use project index
        print u'\n'.join(tasks[project.decode('utf-8')].keys()).encode('utf-8')
    return tasks[project.decode('utf-8')]

def _list(date, dump=True):
    from .client import workTimeAccountingService
    from .client.baseService import autologin
    from .common import dateparam
    
    @autologin
    def __list(date, dump=True):
        date=dateparam.fix(date)
        workTimes = workTimeAccountingService.client().service.getPersonalWorktime(
            sessionID(),
            fromDate=dateparam.format(date[0]),
            toDate=dateparam.format(date[1]))
    
        entries = {}
        entries_by_date = {}
        dayTime = {}
        for workTime in workTimes:
            #print time.date
            project = workTime.projectName
            task = workTime.taskName
            workTimeID = workTime.workTimeID
            comment = workTime.comment
            billable = '$' if workTime.billable else ' '
            time = (float(workTime.duration) / (1000 * 60 * 60)) % 24
            state = {
                0: ' ',  # open
                1: 'L',  # locked
                2: 'X',  # rejected?
            }[workTime.state]
    
            if not workTime.date in entries_by_date.keys():
                entries_by_date[workTime.date] = {}
                dayTime[workTime.date] = 0
            dayTime[workTime.date] += time
    
            entries_by_date[workTime.date][workTimeID] = entries[
                workTimeID] = u"{:.2f} {}{}  {:25.25}  {:25.25}  {:80.80}".format(
                    time, billable, state, project, task, comment)
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

    return __list(date, dump)

def comp_billable(project):
    if projects(dump=False)[project.decode('utf-8')]['billable']:
        print 'billable'
    print 'non_billable'

def comp_list(date):
    entries = _list(date, dump=False)
    for id, entry in entries.iteritems():
        print "{}\:'{:1.160}'".format(id, entry.encode('utf-8'))
    if len(entries) == 1:
        print "none"


def api(service):
    from .client import baseService, masterDataService, workTimeAccountingService, humanService, projectsService

    print {
        'baseService': baseService.client,
        'workTimeAccountingService': workTimeAccountingService.client,
        'masterDataService': masterDataService.client,
        'humanService': humanService.client,
        'projectsService': projectsService.client
    }[service]()


def sync():
    from .client import masterDataService, workTimeAccountingService
    workTimeAccountingService.syncProjects()
    workTimeAccountingService.syncTasks()
    masterDataService.syncActivities()


def completion():
    return os.path.dirname(os.path.realpath(__file__)) + '/completion/zsh'


def main():
    if len(sys.argv) == 2 and sys.argv[1] == 'completion':
        print completion()
        exit(0)

    def _add(**kwargs):
        from .client import workTimeAccountingService
        workTimeAccountingService.add(**kwargs)
    
    def _del(**kwargs):
        from .client import workTimeAccountingService
        workTimeAccountingService.delete(**kwargs)
    
    def _update(**kwargs):
        from .client import workTimeAccountingService
        workTimeAccountingService.update(**kwargs)
    
    def _copy(**kwargs):
        from .client import workTimeAccountingService
        workTimeAccountingService.copy(**kwargs)
    
    def _move(**kwargs):
        from .client import workTimeAccountingService
        workTimeAccountingService.move(**kwargs)
    
    def _login(**kwargs):
        from .client import baseService
        baseService.login(**kwargs)
    
    def _logout(**kwargs):
        from .client import baseService
        baseService.logout(**kwargs)


    from .common import arguments
    try:
        parsed_args = arguments.parse()

        {
            'login': _login,
            'projects': projects,
            'tasks': tasks,
            'list': _list,
            'comp_billable': comp_billable,
            'comp_list': comp_list,
            'add': _add,
            'api': api,
            'sync': sync,
            'activities': activities,
            'completion': completion,
            'del': _del,
            'update': _update,
            'logout': _logout,
            'copy': _copy,
            'move': _move
        }[sys.argv[1]](**parsed_args)
#    except WebFault as e:
#        try:
#            sys.stderr.write(str(e) + '\n')
#        except:
#            # suds unicode bug
#            print 'SESSION_INVALID'
    except BaseException as e:
        sys.stderr.write(str(e) + '\n')
