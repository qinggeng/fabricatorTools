# -*- coding: utf-8 -*-
import phabricator
from phabricator import *
from pprint import pprint as ppr
import sys
import settings
"""
日志写文件的实现：
# 默认写到脚本所在的目录下
# 默认文件名为DailyReport.[日报日期].remarkup
# 第一个参数为日报文件名
## - 时为stdout
"""
def ks(feature, obj):
  ppr(type(obj))
  ppr(filter(lambda x: x.find(feature) != -1, dir(obj)))

def getProject(fab):
  ret = fab.project.query()
  projects = ret['data']
  return projects

def getFab(apiEntry = settings.API_ENTRY, token = settings.API_TOKEN):
  return Phabricator(host = apiEntry, token = token)

def getUsers(fab):
  ret = fab.user.query()
  return ret.response

def getUserTasks(fab, user):
  userId = user['phid']
  tasks = fab.maniphest.query(ownerPHIDs = [userId]).response
  tasks = map(lambda x: tasks[x], tasks)
  return tasks

def getUserActivity(fab, user, limit = 100):
  userId = user['phid']
  return fab.feed.query(filterPHIDs = [userId], limit = limit, view = "text").response

def getAllTasks(fab):
  tasks = fab.maniphest.query(ids = [1]).response
  firstTask = map(lambda x: tasks[x], tasks)[0]
  tasks = fab.maniphest.query(limit = 1).response
  lastTask = map(lambda x: tasks[x], tasks)[0]
  taskCount = int(lastTask['id'])
  offsets = range(0, taskCount, 100)
  allTasks = []
  for offset in offsets:
    tasks = fab.maniphest.query(limit = 100, offset = offset).response
    allTasks += map(lambda x: tasks[x], tasks)
  return allTasks

def getTaskInfo(fab, phid):
  return fab.maniphest.query(phids = [phid]).response.values()[0]

def getTaskTransactions(fab, task_id):
  return fab.maniphest.gettasktransactions(ids = [task_id]).response.values()

class Singleton(type):
  _instances = {}
  def __call__(cls, *args, **kwargs):
    if cls not in cls._instances:
      cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
    return cls._instances[cls]

if __name__ == '__main__':
  fab = getFab(apiEntry = settings.API_ENTRY, token = settings.API_TOKEN)
  tasks = getAllTasks(fab)
  taskIds = map(lambda x: x['id'], tasks)
  #transactions = fab.maniphest.gettasktransactions(ids = taskIds[1:2]).response
  transactions = fab.maniphest.gettasktransactions(ids = ['1']).response
  transactions = reduce(lambda x, y: x + transactions[y], transactions, [])
  ppr(transactions[0].keys())
  ppr(transactions)
  transactions = map(lambda x: (x['transactionPHID'], x['transactionType']), transactions)
  ppr(transactions)
  quit()
  users = getUsers(fab)
  for user in users:
    print user['realName']
    userId = user['phid']
    tasks = fab.maniphest.query(ownerPHIDs = [userId]).response
    tasks = map(lambda x: tasks[x], tasks)
    for task in filter(lambda x: x['isClosed'] == False, tasks):
      ppr(task)
      quit()
      print task['objectName'], task['title'], task['priority']
    #ppr(getUserActivity(fab, user))
#=======
#import requests, json, phabricator, datetime
#from prettyprint import pp as ppr
#import settings
#apiToken = settings.API_TOKEN
#
#fab = phabricator.Phabricator(
#	host = settings.API_ENTRY, 
#	token = apiToken, 
#	)
#
#transactions = fab.maniphest.gettasktransactions(ids=["1"]).response
#ppr(transactions)
#quit()
#
#firstTask =  fab.maniphest.query(ids=[1]).response.values()[0]
#createDate = datetime.datetime.fromtimestamp(int(firstTask["dateCreated"]))
#print createDate
#
#quit()
#resp = requests.post("http://192.168.0.121:8100/api/conduit.getcertificate", data = {"api.token": "api-3o74h37rwikuran7gc7fjvvnwivl"})
#print resp.text
#resp = requests.post("http://192.168.0.121:8100/api/user.whoami", data = {"api.token": "api-3o74h37rwikuran7gc7fjvvnwivl"})
#print resp.text
