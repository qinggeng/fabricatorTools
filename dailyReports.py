# -*- coding: utf-8 -*-
from phabricator import *
from datetime import datetime, date, time, timedelta
from fab import getUsers, getUserActivity, getTaskInfo, getTaskTransactions
from transaction import ObjectTransactionsGetterBuilder, TransactionDescriber
from pprint import pprint as ppr
from user import CacheUsers
from printers import Banner
#import sys
#import codecs
#sys.stdout = codecs.getwriter('utf8')(sys.stdout)

def getUserActivitiesBetweenDays(near, far, fab, user):
        try:
            activities = getUserActivity(fab, user, 100).values()
        except Exception, e:
            activities = getUserActivity(fab, user, 100)
        activities = filter(lambda x: date.fromtimestamp(x['epoch']) >= far and date.fromtimestamp(x['epoch']) < near, activities)
        activities.sort(cmp = lambda x, y: cmp(y['epoch'], x['epoch']))
        return activities

    

if __name__ == "__main__":
    title= \
u"""
**********************************
*                                *
*     DAILY REPORT GENERATOR     *
*                                *
**********************************
"""
#    print title
    today = date.today()
    yestoday = today - timedelta(days = 1)
    reportDate = yestoday
    while reportDate.weekday() > 4:
        reportDate = reportDate - timedelta(days = 1)
    transactionLoader = ObjectTransactionsGetterBuilder()
    transDescriptor = TransactionDescriber()
    fab = Phabricator()
    users = getUsers(fab)
    Banner()\
        .addLine(u"Phabricator Daily Report")\
        .addLine("")\
        .addLine(reportDate.strftime("Target Date: %Y-%m-%d").decode('utf-8'))\
        .addLine(today.strftime("Report Date: %Y-%m-%d").decode('utf-8'))\
        .output()
    for user in users:
        print u"==============="
        print '   ', user['realName']
        print u"==============="
        with CacheUsers(users):
            try:
                activities = getUserActivitiesBetweenDays(today, yestoday, fab, user)
                for activity in activities:
                    objectId = activity['data'][u'objectPHID']
                    transactionKeys = activity['data'][u'transactionPHIDs']
                    transactions = transactionLoader.getObjectTransactions(fab, objectId)
                    transactions = filter(lambda x: x['transactionPHID'] in transactionKeys, transactions)
                    for tran in transactions:
                        print "Transaction({tranid}) on T{task}:".format(tranid = tran['transactionID'], task = tran['taskID'])
                        print transDescriptor.describe(fab, tran)
            except Exception, e:
                print e

