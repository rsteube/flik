import argparse
from . import dateparam


def parse():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    add_activities_parser(subparsers)
    add_add_parser(subparsers)
    add_api_parser(subparsers)
    add_copy_parser(subparsers)
    add_move_parser(subparsers)
    add_del_parser(subparsers)
    add_comp_billable_parser(subparsers)
    add_comp_list_parser(subparsers)
    add_completion_parser(subparsers)
    add_list_parser(subparsers)
    add_login_parser(subparsers)
    add_logout_parser(subparsers)
    add_projects_parser(subparsers)
    add_sync_parser(subparsers)
    add_tasks_parser(subparsers)
    add_update_parser(subparsers)

    return vars(parser.parse_args())


def add_activities_parser(subparsers):
    subparsers.add_parser('activities', help='list cached activities')


def add_add_parser(subparsers):
    parser = subparsers.add_parser('add', help='add Worktime')
    parser.add_argument('date', type=dateparam.parse)
    parser.add_argument('project')
    parser.add_argument('task')
    parser.add_argument('activity')
    parser.add_argument(
        'billable', type=lambda x: ['billable', 'non_billable'].index(x) == 0)
    parser.add_argument('duration', type=float)
    parser.add_argument('comment', nargs='+')


def add_api_parser(subparsers):
    parser = subparsers.add_parser('api', help='print api')
    parser.add_argument('service')


def add_copy_parser(subparsers):
    parser = subparsers.add_parser('copy', help='copy worktime')
    parser.add_argument('from_date', type=dateparam.parse)
    parser.add_argument('workTimeID')
    parser.add_argument('to_date', type=dateparam.parse)
    parser.add_argument('duration', type=float)

def add_move_parser(subparsers):
    parser = subparsers.add_parser('move', help='move worktime')
    parser.add_argument('from_date', type=dateparam.parse)
    parser.add_argument('workTimeID')
    parser.add_argument('to_date', type=dateparam.parse)

def add_del_parser(subparsers):
    parser = subparsers.add_parser('del', help='delete Worktime')
    parser.add_argument('date', type=dateparam.parse)
    parser.add_argument('workTimeID')


def add_comp_billable_parser(subparsers):
    parser = subparsers.add_parser(
        'comp_billable', help='zsh completion for billable')
    parser.add_argument('project')


def add_comp_list_parser(subparsers):
    parser = subparsers.add_parser(
        'comp_list', help='zsh completion for tasks')
    parser.add_argument('date', type=dateparam.parse)


def add_completion_parser(subparsers):
    subparsers.add_parser('completion', help='show path to completion')


def add_list_parser(subparsers):
    parser = subparsers.add_parser('list', help='list Worktime')
    parser.add_argument(
        'date', nargs='?', default='today', type=dateparam.parse)


def add_login_parser(subparsers):
    subparsers.add_parser('login', help='login')


def add_logout_parser(subparsers):
    subparsers.add_parser('logout', help='logout')


def add_projects_parser(subparsers):
    subparsers.add_parser('projects', help='list cached projects')


def add_sync_parser(subparsers):
    subparsers.add_parser('sync', help='update caches')


def add_tasks_parser(subparsers):
    parser = subparsers.add_parser('tasks', help='list cached tasks')
    parser.add_argument('project')


def add_update_parser(subparsers):
    parser = subparsers.add_parser('update', help='update Worktime')
    parser.add_argument('date', type=dateparam.parse)
    parser.add_argument('workTimeID')
    parser.add_argument('duration', type=float)
