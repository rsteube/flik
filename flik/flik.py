import os, sys
import logging

logging.basicConfig(level=logging.ERROR)


def sessionID():
    from flik.common import storage
    return storage.readShare('sessionID')


def activities(dump=True):
    from yaml import safe_load
    from flik.common import storage

    activities = safe_load(storage.readShare('activities.yaml'))
    if dump:
        print('\n'.join(list(activities.keys())))
    return activities


def projects(dump=True):
    from yaml import safe_load
    from flik.common import storage

    projects = safe_load(storage.readShare('projects.yaml'))
    if dump:
        print('\n'.join(list(projects.keys())))
    return projects


def tasks(project=None, dump=True):
    from yaml import safe_load
    from flik.common import storage

    tasks = safe_load(storage.readShare('tasks.yaml'))
    if dump:
        #TODO use project index
        print('\n'.join(list(tasks[project].keys())))
    return tasks[project]

def _list(date, dump=True):
    from flik.client import workTimeAccountingService
    from flik.client.baseService import autologin
    from flik.common import dateparam
    
    @autologin
    def __list(date, dump=True):
        workTimes = workTimeAccountingService.client().service.getPersonalWorktime(
            sessionID(),
            fromDate=dateparam.format(date[0]),
            toDate=dateparam.format(date[1]))
    
        entries = {}
        entries_by_date = {}
        dayTime = {}
        for workTime in workTimes:
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
    
            if not workTime.date in list(entries_by_date.keys()):
                entries_by_date[workTime.date] = {}
                dayTime[workTime.date] = 0
            dayTime[workTime.date] += time
    
            entries_by_date[workTime.date][workTimeID] = entries[
                workTimeID] = "{:.2f} {}{}  {:25.25}  {:25.25}  {:.80}".format(
                    time, billable, state, project, task, comment)
        if dump:
            for date, entries_for_date in sorted(entries_by_date.items()):
                print('[%s]' % date.strftime('%Y-%m-%d %a'))
                print('\n'.join(entries_for_date.values()))
                print('-----')
                print(dayTime[date])
                print('')
            if len(list(dayTime.values())) > 1:
                print('=====')
                print(sum(dayTime.values()))
        return entries

    return __list(date, dump)

def comp_billable(project):
    if projects(dump=False)[project]['billable']:
        print('billable')
    print('non_billable')

def comp_list(date):
    entries = _list(date, dump=False)
    for id, entry in list(entries.items()):
        print("{}\:'{:1.160}'".format(id, entry))
    if len(entries) == 1:
        print("none")


def api(service):
    from flik.client import baseService, masterDataService, workTimeAccountingService, humanService, projectsService

    print({
        'baseService': baseService.client,
        'workTimeAccountingService': workTimeAccountingService.client,
        'masterDataService': masterDataService.client,
        'humanService': humanService.client,
        'projectsService': projectsService.client
    }[service]().wsdl.dump())


def sync():
    from flik.client import masterDataService, workTimeAccountingService
    workTimeAccountingService.syncProjects()
    workTimeAccountingService.syncTasks()
    masterDataService.syncActivities()


def completion():
    return os.path.dirname(os.path.realpath(__file__)) + '/completion/zsh'


def main():
    if len(sys.argv) == 2 and sys.argv[1] == 'completion':
        print(completion())
        exit(0)
    
    if len(sys.argv) == 1:
        sys.argv.append('list')

    def _add(**kwargs):
        from flik.client import workTimeAccountingService
        workTimeAccountingService.add(**kwargs)
    
    def _del(**kwargs):
        from flik.client import workTimeAccountingService
        workTimeAccountingService.delete(**kwargs)
    
    def _update(**kwargs):
        from flik.client import workTimeAccountingService
        workTimeAccountingService.update(**kwargs)
    
    def _copy(**kwargs):
        from flik.client import workTimeAccountingService
        workTimeAccountingService.copy(**kwargs)
    
    def _move(**kwargs):
        from flik.client import workTimeAccountingService
        workTimeAccountingService.move(**kwargs)
    
    def _login(**kwargs):
        from flik.client import baseService
        baseService.login(**kwargs)
    
    def _logout(**kwargs):
        from flik.client import baseService
        baseService.logout(**kwargs)


    from flik.common import arguments
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
    except Exception as e:
        if hasattr(e, 'message'):
            logging.error(e.message)
        else:
            logging.error(str(e))

