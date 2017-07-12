#-*- coding: utf-8 -*-
from fab import getFab, getUsers
from user import  getUsers, CacheUsers, UserInfo
from task import TaskInfoFactory, newTask, updateTask
import json
from prettyprint import pp
from settings import PRIORITY_VALUES, STATUS_NAMES
import sys

def exportJson(ids):
    tf = TaskInfoFactory()
    ret = []
    for tid in ids:
        row = {
            'tid': tid,
            #'parent': tf.parent(tid),
            'parent': u", ".join(tf.precedingTIDs(tid)),
            'task': tf.title(tid),
            'assigned': tf.owner(tid),
            'status': tf.status(tid),
            'priority': tf.priority(tid),
            'points': tf.points(tid),
            'description': tf.description(tid),
            'tags': u", ".join(tf.projects(tid)),
            #'subscribers':tf.subscribers(tid),
            'severity': tf.severity(tid),
            'deadline': tf.deadline(tid),
            'kickoff': tf.kickoffDate(tid),
            'author': tf.author(tid),
            #'isKeyTask': tf.isKeyTask(tid),
        }
        ret.append(row)
    return json.dumps(ret, ensure_ascii = False)


if __name__ == '__main__':
    try:
        idsArg = sys.argv[1]
    except Exception, e:
        idsArg = "1011, 1012, 1023"
    ids = map(lambda x: int(x), idsArg.split(','))
    fab = getFab()
    users = getUsers(fab)
    with CacheUsers(users) as cu:
        ui = UserInfo()
        print exportJson(ids)
        
