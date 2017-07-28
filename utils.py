# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, date
from time import mktime
from settings import HOLIDAYS, WORKDAYS
def mktimep(timestr, fmt):
    return int(mktime(datetime.strptime(timestr, fmt).timetuple()))

def isValidWorkday(theDay, holidays = HOLIDAYS, workdays = WORKDAYS):
    if theDay in holidays:
        return False
    if theDay in workdays:
        return True
    weekDay = theDay.weekday()
    return weekDay != 5 and weekDay != 6

def getLastWorkday(theDay):
    while False == isValidWorkday(theDay):
        theDay -= timedelta(days = 1)
    return theDay
