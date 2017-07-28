#-*- coding: utf-8 -*-
from fab import getFab, getUsers
from user import  getUsers, CacheUsers, UserInfo
from task import TaskInfoFactory, newTask, updateTask
import json
from prettyprint import pp
from settings import PRIORITY_VALUES, STATUS_NAMES
import sys, argparse

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-i', dest = 'src', help = 'task data from json file')
  args = parser.parse_args()
  if args.src == '-':
    #TODO read criteria from stdin
    newTasks = sys.stdin.read().strip()
    newTasks = json.loads(newTasks)
  else:
    newTasks = json.load(open(args.src, 'r'))
  fab = getFab()
  for t in newTasks:
    t['tid'] = unicode(t['tid'])
  users = getUsers(fab)
  with CacheUsers(users) as cu:
    for newTaskRequest in filter(lambda x: len(x['tid']) == 0, newTasks):
      ret = newTask(fab, **newTaskRequest)
    for updateTaskRequest in filter(lambda x: len(x['tid']) != 0, newTasks):
      updateTask(fab, **updateTaskRequest)

