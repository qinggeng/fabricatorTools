# -*- coding: utf-8 -*-
from datetime import datetime, date, time, timedelta
from fab import getUsers, getUserActivity, getTaskInfo, getTaskTransactions, getFab
from transaction import ObjectTransactionsGetterBuilder, TransactionFormatter
from pprint import pprint as ppr
from user import CacheUsers
from printers import Banner
from task import TaskInfoFactory
import sys, argparse, os.path
#import codecs
#sys.stdout = codecs.getwriter('utf8')(sys.stdout)

class Logger(object):
  def __init__(self, filename= None, tee = True):
    self.terminal = sys.stdout
    if None != filename:
      self.log = open(filename, "w")
    else:
      self.log = None
    self.tee = tee

  def write(self, message):
    if type(message) == unicode:
      message = message.encode('utf-8')
    if True == self.tee:
      self.terminal.write(message)
    if None != self.log:
      self.log.write(message)


def getUserActivitiesBetweenDays(near, far, fab, user):
  resp = getUserActivity(fab, user, 100)
  try:
    activities = resp.values()
  except Exception, e:
    activities = getUserActivity(fab, user, 100)
  activities.sort(lambda x, y: cmp(y['epoch'], x['epoch']))
  activities = filter(lambda x: date.fromtimestamp(x['epoch']) >= far and date.fromtimestamp(x['epoch']) < near, activities)
  return activities

class DailyReportFactory(object):
  def __init__(self, fab = None):
    if fab == None:
      fab = getFab()
    self.fab = fab
  def getReport(self, reportDate = None, beginDate = None, endDate = None, users = None):
    fab = self.fab
    if reportDate == None:
      today = date.today()
      reportDate = today
    else:
      today = reportDate
    if users == None:
      users = getUsers(fab)
    if beginDate == None:
      yestoday = today - timedelta(days = 1)
    else:
      yestoday = beginDate

    targetDate = yestoday
    while targetDate.weekday() > 4:
      targetDate = targetDate - timedelta(days = 1)
    Banner()\
      .addLine(u"Phabricator Daily Report")\
      .addLine("")\
      .addLine(targetDate.strftime("Target Date: %Y-%m-%d").decode('utf-8'))\
      .addLine(reportDate.strftime("Report Date: %Y-%m-%d").decode('utf-8'))\
      .output()
    #TODO ioc loader and descriptor?
    transactionLoader = ObjectTransactionsGetterBuilder()
    transFormatter = TransactionFormatter()
    taskInfoProvider = TaskInfoFactory(fab = fab)
    for user in users:
      print u"==============="
      print '   ', user['realName']
      print u"==============="
      with CacheUsers(users):
        try:
          activities = getUserActivitiesBetweenDays(today, targetDate, fab, user)
          for activity in activities:
            print activity['text']
            continue
            objectId = activity['data'][u'objectPHID']
            transactionKeys = activity['data'][u'transactionPHIDs']
            try:
              transactions = transactionLoader.getObjectTransactions(fab, objectId)
            except Exception, e:
              print "transcation on unknow object: %s" % (objectId, )
              transactions = []
            transactions = filter(lambda x: x['transactionPHID'] in transactionKeys, transactions)
            for tran in transactions:
              print u"Transaction({tranid}) on \"{task}\":".format(tranid = tran['transactionID'], task = taskInfoProvider.longTitle(int(tran['taskID']))) 
              print transFormatter.format(fab, tran)
        except Exception, e:
          print e
    pass



if __name__ == "__main__":
  argParser = argparse.ArgumentParser()
  argParser.add_argument("--from", help = u"from date, can be date or days like \"-1\"", default = u"-1")
  argParser.add_argument("--to", help = u"to date", default = u"yestoday")
  argParser.add_argument("-o", help = "output folder", default = "-")
  args = argParser.parse_args()
  if args.to == u'yestoday':
    endDate = date.today() - timedelta(days = 1)
  try:
    endDate = datetime.strptime(args.to, '%Y-%m-%d').date()
    daySpan = timedelta(days = int(getattr(args, 'from')))
    beginDate = endDate - daySpan
  except Exception, e:
    beginDate = endDate - timedelta(days = 1)
    pass
  if args.o == '-':
    DailyReportFactory().getReport(beginDate = endDate, endDate = beginDate)
  else:
    reportFileName = os.path.join(args.o, "DailyReport[{date}][{begin}_{end}].remarkup".format(date = datetime.now().strftime("%Y-%m-%d"), begin = beginDate, end = endDate))
    try:
      sys.stdout = Logger(filename = reportFileName, tee = False)
      DailyReportFactory().getReport(beginDate = endDate, endDate = beginDate)
    except:
      pass
