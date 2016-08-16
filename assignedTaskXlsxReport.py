# -*- coding: utf-8 -*-
from datetime import datetime, date, time, timedelta
from fab import getUsers, getUserActivity, getTaskInfo, getTaskTransactions, getFab, getUserTasks
from transaction import ObjectTransactionsGetterBuilder, TransactionFormatter
from pprint import pprint as ppr
from user import CacheUsers, UserInfo
from printers import Banner
from task import TaskInfoFactory
import sys, argparse
import xlsxwriter as xw

argsParser = argparse.ArgumentParser()

argsParser.add_argument("-o", help = u"output xlsx filename", default = "assigned.xlsx")

args = argsParser.parse_args()

fab = getFab()
users = getUsers(fab)
tf = TaskInfoFactory(fab = fab)
reportDate = datetime.now()

def getRemainsTime(tid):
    return tf.remainsTimeDesription(tid, datetime.now())
columns = [
    (u'标题', tf.longTitle),
    (u'负责人', tf.owner),
    (u'截止时间', tf.deadline),
    (u'剩余时间', getRemainsTime),
    (u'状态', tf.status),
    (u'优先级', tf.priority),
    (u'预估工时', tf.points),
    (u"发起人", tf.author),
]
wb = xw.Workbook(args.o)
ws = wb.add_worksheet()
ws.name = u'详细列表'
row = 1
titleFormat = wb.add_format({
    'bold': True, 
    'align': 'center',
    'valign': 'vcenter',
    })
for column, col in zip(columns, range(len(columns))):
    ws.write(0, col, column[0], titleFormat)

summarize = [];
with CacheUsers(users) as cu:
    for user in users:
        print user['realName']
        tasks = getUserTasks(fab, user)
        tasks = filter(lambda x: x['isClosed'] != True, tasks)
        summarize.append(u"{name}手上有{c}个task".format(name = user['realName'], c = len(tasks)))
        for task in tasks:
            #print 'T' + task['id']
            for column, col in zip(columns, range(len(columns))):
                func = column[1]
                #print column[0], ',',
                ws.write(row, col, func(int(task['id'])))
            row += 1
    summarize.append(u'报告生成时间:{rt}'.format(rt = reportDate.strftime("%Y年%m月%d日 %H:%M").decode('utf-8')))
    for summ in summarize:
        ws.write(row, 0, summ)
        row += 1
    wb.close()
