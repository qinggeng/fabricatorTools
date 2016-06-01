# -*- coding: utf-8 -*-
from fab import getFab
class TaskInfoFactory(object):
    def __init__(self, **kwargs):
        fab = kwargs.pop('fab', getFab())
        self.fab = fab
        self.cachedTasks = {}
        pass
    def info(self, tid):
        if tid in self.cachedTasks:
            return self.cachedTasks[tid]
        return self.remoteInfo(tid)

    def remoteInfo(self, tid):
        fab = self.fab
        resp = fab.maniphest.info(task_id = tid)
        taskInfo = resp.response
        self.cachedTasks[tid] = taskInfo
        return taskInfo
    def longTitle(self, tid):
        return u"T{tid} {title}".format(tid = tid, title = self.info(tid)['title'])

if __name__ == '__main__':
    from pprint import pprint as ppr
    tf = TaskInfoFactory()
    ppr(tf.info(240))
