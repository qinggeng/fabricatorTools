#-*- coding: utf-8 -*-
u"""
# 检索计划当天结束的任务
# 检索用户，对每个用户
# 检索昨天结束的任务
# 对这些任务，有列表：
- 任务编号
- 任务名称
- 任务计划结束时间
- 任务实际结束时间
"""
from datetime import datetime, date, time, timedelta
from fab import getUsers, getUserActivity, getTaskInfo, getTaskTransactions, getFab
from transaction import ObjectTransactionsGetterBuilder, TransactionFormatter
from pprint import pprint as ppr
from user import CacheUsers
from printers import Banner
from task import TaskInfoFactory
import sys, argparse, os.path

def lastDay():
  n = datetime.today()
  n -= timedelta(days = 1)
  return datetime(n.year, n.month, n.day, 0, 0, 0)

if __name__ == '__main__':
  fab = getFab()
  resp = fab.maniphest.search(queryKey = None, constraints = {'modifiedStart': int(lastDay().strftime('%s'))})
  tasks = resp.response['data']
  for task in tasks:
    taskStatus = task['fields']['status']['value']
    if taskStatus == 'resolved':
      print task['id']
  quit()
  users = getUsers(fab)
  with CacheUsers(users):
    for user in users:
      print user
      #resp = fab.maniphest.search(queryKey = None, constraints = {''})
