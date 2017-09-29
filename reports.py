# -*- coding: utf-8 -*-
import itertools
from user import getUsers, CacheUsers, UserInfo
from search import searchFab
from prettyprint import pp
import settings
import datetime

reports = u"""
个人未结束的任务
个人未结束的任务，按照优先级分组
个人未结束的任务，按照项目分组
个人当天要完成的任务
个人本周内要完成的任务
"""

def groupby_deadline(tasks):
  sortFunc = lambda x, y: cmp(x['fields']["custom.bestrun:deadline"], y['fields']["custom.bestrun:deadline"])
  tz = settings.CLIENT_TZ
  def keyFunc(x):
    epoch = x['fields']["custom.bestrun:deadline"]
    if None == epoch:
      return u'未定'
    # dt = datetime.datetime.strptime(str(epoch), '%s')
    dt = datetime.datetime.fromtimestamp(epoch)
    now = datetime.datetime.now()
    dt = tz.fromutc(dt)
    now = tz.fromutc(now)
    days = (dt.date() - now.date()).days
#     if x['id'] == 383:
#         pp(x)
#         print dt
#         print now
#         print days
#         quit()
    if days < 0:
      return u'超期'
    if days == 0:
      return u'今天'
    friday = dt.date() + datetime.timedelta(days = min(0, (5 - dt.isoweekday())))
    if dt.date() <= friday:
      return u'本周'
    if days <= 7:
      return u'一周内'
    if days <= 31:
      return u'一个月内'
    return u'其他'
  return itertools.groupby(sorted(tasks, sortFunc), keyFunc)


def groupby_owners(tasks):
  sortFunc = lambda x, y: cmp(x['fields']['ownerPHID'], y['fields']['ownerPHID'])
  keyFunc = lambda x: x['fields']['ownerPHID']
  return itertools.groupby(sorted(tasks, sortFunc), keyFunc)

def groupby_priority(tasks):
  sortFunc = \
    lambda x, y: \
      cmp(x['fields']['priority']['value'], y['fields']['priority']['value'])
  keyFunc = lambda x: x['fields']['priority']['name']
  return itertools.groupby(sorted(tasks, sortFunc, reverse = True), keyFunc)

def walkGroups(arr, groups):
  if len(groups) == 0:
    return
  groupby = groups[0]['groupby']
  func = groups[0]['callback']
  for k, g in groupby(arr):
    g = list(g)
    if False == func(k, g):
      return False
    if False == walkGroups(g, groups[1:]):
      return False
  return True


if __name__ == '__main__':
  from search_criterias import searchCriterias
  from fab import getFab
  fab = getFab()
  users = getUsers(fab)
  with CacheUsers(users):
    ui = UserInfo()
    def printOwner(k, g):
      if None == k:
        k = u'无负责人'
      else:
        k = ui.phid2realname(k)
      print k, len(g)
      return True
    def printPriority(k, g):
      print '  ',
      print k, len(g)
      return True
    def printDeadline(k, g):
      print '    ',
      print k, len(g)
      for t in g:
        print '      ',
        print u'T{id}: {t}'.format(id = t['id'], t = t['fields']['name'])
      return True
    groups = [
      {'groupby': groupby_owners, 'callback': printOwner},
      {'groupby': groupby_priority, 'callback': printPriority},
      {'groupby': groupby_deadline, 'callback': printDeadline},
    ]
    tasks = searchFab(fab, searchCriterias[0], True)
    walkGroups(tasks, groups)
