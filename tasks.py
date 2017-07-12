#-*- coding: utf-8 -*-
from task import TaskInfoFactory
from fab import getAllTasks, getFab

tasks = getAllTasks(getFab())
print ','.join(map(lambda x: x['id'], tasks))
