#-*- coding: utf-8 -*-
from fab import getFab, getUsers
from user import  getUsers, CacheUsers, UserInfo
from task import TaskInfoFactory, newTask, updateTask
import json
from prettyprint import pp
from settings import PRIORITY_VALUES, STATUS_NAMES
import sys

tasksJson = '/Users/hyk/workspace/workbench/2016-09-05/tasks.json'
tasksJson = './tasks.json'

if len(sys.argv) > 1:
    tasksJson = sys.argv[1]
newTasks = json.load(open(tasksJson, 'r'))
fab = getFab()
users = getUsers(fab)
with CacheUsers(users) as cu:
    for newTaskRequest in filter(lambda x: len(x['tid']) == 0, newTasks):
        ret = newTask(fab, **newTaskRequest)
    for updateTaskRequest in filter(lambda x: len(x['tid']) != 0, newTasks):
        updateTask(fab, **updateTaskRequest)
quit()

taskPHID = "PHID-TASK-zhtn37zjohgxgvptdjgh"

with CacheUsers(users) as cu:
    ui = UserInfo()
    fab.maniphest.update(
        id = "3",
        priority = PRIORITY_VALUES["Unbreak Now!"],
        status = STATUS_NAMES["Open"],
        ownerPHID = None)
