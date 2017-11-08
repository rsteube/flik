import re
from datetime import datetime
from dateutil.relativedelta import relativedelta, MO, TU, WE, TH, FR, SA, SU


def parse(raw_date):
    weekday = {
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
    elif re.match('\d{4}-w\d{2}', raw_date) is not None:
        fromDate = datetime.strptime(raw_date + '-1', "%Y-W%W-%w").date()
        toDate = fromDate + relativedelta(days=7)
        return fromDate, toDate
    else:
        date = datetime.strptime(raw_date, '%Y-%m-%d')
    toDate = date + relativedelta(days=1)
    return date, toDate


def format(date):
    return date.strftime('%Y-%m-%d')
