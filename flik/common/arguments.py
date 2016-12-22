import argparse
from . import dateparam

def parse():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # activities
    parser_activities = subparsers.add_parser('activities', help='activities help', description='List cached activities.')

    # add
    parser_add = subparsers.add_parser('add', help='Add new Worktime entry.', description='Add new Worktime entry.')
    parser_add.add_argument('date', metavar='date', type=str, help='the date')
    parser_add.add_argument('project', metavar='project', type=str, help='the project')
    parser_add.add_argument('task', metavar='task', type=str, help='the task')
    parser_add.add_argument('activity', metavar='activity', type=str, help='the activity')
    parser_add.add_argument('billable', metavar='billable', type=str, help='desc billable', choices=['billable', 'non_billable'])
    parser_add.add_argument('duration', metavar='duration', type=float, help='desc duration')
    parser_add.add_argument('comment', metavar='comment', type=str, nargs='+', help='desc duration')

    # api
    parser_api = subparsers.add_parser('api', help='api help', description='Print api.')
    parser_api.add_argument('service', metavar='service', type=str, help='service to print')

    # del
    parser_del = subparsers.add_parser('del', help='del help', description='Delete Worktime entry.')
    parser_del.add_argument('date', metavar='date', type=dateparam.parse, help='the date')
    parser_del.add_argument('workTimeID', metavar='workTimeID', type=str, help='id to delete')
    
    
    parser_update = subparsers.add_parser('update', help='update help', description='Update Worktime entry.')
    parser_update.add_argument('date', metavar='date', type=dateparam.parse, help='the date')
    parser_update.add_argument('workTimeID', metavar='workTimeID', type=str, help='id to delete')
    parser_update.add_argument('duration', metavar='duration', type=float, help='desc duration')


    parser_comp_list = subparsers.add_parser('comp_list', help='comp_list help', description='TODO')
    parser_comp_list.add_argument('date', metavar='date', type=dateparam.parse, help='the date')

    parser_list = subparsers.add_parser('list', help='list help', description='TODO')
    parser_list.add_argument('date', metavar='date', type=dateparam.parse, help='the date')

    parser_login = subparsers.add_parser('login', help='login help', description='TODO')

    parser_logout = subparsers.add_parser('logout', help='logout help', description='TODO')

    parser_projects = subparsers.add_parser('projects', help='projects help', description='TODO')

    parser_sync = subparsers.add_parser('sync', help='sync help', description='TODO')

    parser_tasks = subparsers.add_parser('tasks', help='tasks help', description='TODO')
    parser_tasks.add_argument('project', metavar='project', type=str, help='the project')

    parser_completion = subparsers.add_parser('completion', help='completion help', description='TODO')

    return parser.parse_args()

