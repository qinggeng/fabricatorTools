# -*- coding: utf-8 -*-
u"""
检查上一个工作日task的变动情况
"""
from fab import getUsers, getUserActivity, getTaskInfo, getTaskTransactions, getFab, getUserTasks
from user import  getUsers, CacheUsers, UserInfo
from task import TaskInfoFactory, newTask
from datetime import datetime, date, timedelta, time
from time import mktime
from utils import getLastWorkday, mktimep
from prettyprint import pp
from functools import partial
from settings import CUSTOM_FIELD_KEYS
from task import TaskInfoFactory

def isCreateAfter(refTime, task):
    u"""只适用于maniphest.search得到的task"""
    return refTime < datetime.fromtimestamp(task['fields']['dateCreated'])

def shouldHaveDeadline(task):
    u"""只适用于maniphest.search得到的task"""
    priorityValue = task['fields']['priority']['value']
    if priorityValue < 70 or priorityValue == 90:
        return True
    return task['fields']['custom.' + CUSTOM_FIELD_KEYS['deadline']] != None

def shouldHavePriority(task):
    u"""只适用于maniphest.search得到的task"""
    priorityValue = task['fields']['priority']['value']
    return priorityValue != 90

def shouldHaveOwner(tf, task):
    u"""只适用于maniphest.search得到的task"""
    return tf.owner(task['id']) != u""

td = date.today()
lastValidDay = td - timedelta(days = 1)
lastValidDay = td

weekdayNames = [
    u"周一",
    u"周二",
    u"周三",
    u"周四",
    u"周五",
    u"周六",
    u"周日",
]

lastWorkday = getLastWorkday(lastValidDay)

updateAfter = datetime(
    lastWorkday.year,
    lastWorkday.month,
    lastWorkday.day,
    9,
    00)

tsp = int(mktime(updateAfter.timetuple()))

fab = getFab()
users = getUsers(fab)
tf = TaskInfoFactory(fab = fab)

resp = fab.maniphest.search(queryKey = None,
        constraints = {'modifiedStart': tsp}).response

tasks = resp['data']

filters = [
    (partial(isCreateAfter, updateAfter), u"新建的项目"),
    (None, u"待验证的项目"),
    (None, u""),
    (None, u""),
    (None, u""),
    (None, u""),
    (None, u""),
    (None, u""),
    (None, u""),
    (None, u""),
    (None, u""),
]

rules = [
    (shouldHavePriority, u"优先级必须确定"),
    (shouldHaveDeadline, u"高优先级任务必须有截止时间"),
    (partial(shouldHaveOwner, tf), u"任务必须有负责人"),
    (None, u"高优先级任务必须有工时"),
    (None, u"必须有所属项目"),
    (None, u"如果父任务有截止时间，任务截止时间不得超出父项目"),
    (None, u"任务应该有描述"),
]

availableRules = filter(lambda x: x[0] != None, rules)

results = []
with CacheUsers(users) as cu:
    ui =UserInfo()
    #for task in filter(filters[0][0], tasks):
    for task in tasks:
        violations = []
        for rule in availableRules:
            if False == rule[0](task):
                violations.append(rule[1])
        if len(violations) > 0:
            tid = task['id']
            results.append({
                'id': tid,
                'title': tf.longTitle(tid),
                'violations': violations,
                'owner': tf.owner(tid),
                'author': tf.author(tid)})
    pp(results)
