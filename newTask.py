#-*- coding: utf-8 -*-
from fab import getFab, getUsers
from user import  getUsers, CacheUsers, UserInfo
from task import TaskInfoFactory, newTask
import json
from prettyprint import pp
from settings import PRIORITY_VALUES, STATUS_NAMES
import sys
tasksJson = '/Users/hyk/workspace/workbench/2016-09-02/tasks.json'

if len(sys.argv) > 1:
    tasksJson = sys.argv[1]
newTasks = json.load(open(tasksJson, 'r'))
fab = getFab()
users = getUsers(fab)
with CacheUsers(users) as cu:
    for newTaskRequest in newTasks:
        ret = newTask(fab, **newTaskRequest)
        print ret
quit()

taskPHID = "PHID-TASK-zhtn37zjohgxgvptdjgh"

with CacheUsers(users) as cu:
    ui = UserInfo()
    fab.maniphest.update(
        id = "3",
        priority = PRIORITY_VALUES["Unbreak Now!"],
        status = STATUS_NAMES["Open"],
        ownerPHID = None)
    tf = TaskInfoFactory()
    tif = tf.info(3)
    pp(tif)
