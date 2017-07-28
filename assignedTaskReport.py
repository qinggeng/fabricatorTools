# -*- coding: utf-8 -*-
from datetime import datetime, date, time, timedelta
from fab import getUsers, getUserActivity, getTaskInfo, getTaskTransactions, getFab, getUserTasks
from transaction import ObjectTransactionsGetterBuilder, TransactionFormatter
from pprint import pprint as ppr
from user import CacheUsers, UserInfo
from printers import Banner
from task import TaskInfoFactory
import sys, argparse
fab = getFab()
users = getUsers(fab)
reportDate = datetime.now()
Banner()\
    .addLine(u"Assigned Tasks Report")\
    .addLine("")\
    .addLine(reportDate.strftime("Report Time: %Y-%m-%d %H:%M").decode('utf-8'))\
    .output()
with CacheUsers(users) as cu:
    for user in users:
        tasks = map(lambda x: u"\t[{status}][{priority}] T{id}: {title}".format(id = x['id'], title = x['title'], status = x['status'], priority = x['priority']), filter(lambda x: x['isClosed'] == False, getUserTasks(fab, user)))
        print u"{user} 手上有 {tc}个任务".format(user = user['realName'], tc = len(tasks))
        for task in sorted(tasks, reverse = True):
            print task
