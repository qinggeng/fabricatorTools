# -*- coding: utf-8 -*-
from fab import getFab
from user import UserInfo
from datetime import datetime
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

    def cacheTasks(self, tids):
        #TODO implement me
        pass

    def deadline(self, tid):
        t = self.info(tid)
        aux = t["auxiliary"]
        deadline = aux["std:maniphest:bestrun:deadline"]
        if None == deadline:
            return u"TBD"
        return datetime.fromtimestamp(deadline).strftime("%Y年%m月%d日 %H:%M").decode('utf-8')

    def deadlineTimestemp(self, tid):
        t = self.info(tid)
        aux = t["auxiliary"]
        deadline = aux["std:maniphest:bestrun:deadline"]
        return float(deadline)

    def kickoffDate(self, tid):
        t = self.info(tid)
        aux = t["auxiliary"]
        kickoff = aux["std:maniphest:bestrun:plan:kickoff"]
        return datetime.fromtimestamp(kickoff)

    def points(self, tid):
        try:
            if tid in self.cachedTasks:
                if 'points' in self.cachedTasks[tid]:
                    return self.cachedTasks[tid]['points']
            fab = self.fab
            resp = fab.maniphest.search(queryKey=None, constraints={'ids':[int(tid)]}).response
            ret = resp['data'][0]['fields']['points']
            if tid in self.cachedTasks:
                self.cachedTasks[tid]['points'] = ret
            return ret
        except Exception, e:
            return ""

    def precedings(self, tid):
        tif = self.info(tid)
        dependPhids = tif['dependsOnTaskPHIDs']
        return self.infoFromPHIDs(dependPhids)
        pass

    def infoFromPHID(self, phid):
        return self.infoFromPHIDs([phid])

    def infoFromPHIDs(self, phids):
        fab = self.fab
        resp = fab.maniphest.query(phids = phids).response
        ret = resp.values()
        for tif in ret:
            tid = tif['id']
            self.cachedTasks[tid] = tif
        return ret
    
    def owner(self, tid):
        tif = self.info(tid)
        ui = UserInfo()
        ownerPHID = tif['ownerPHID']
        if None == ownerPHID:
            return u""
        ret = ui.getUsersRealName([ownerPHID])
        if len(ret) == 0:
            return u""
        return ret[0]

class TaskTableFactory(object):
    def __init__(self, taskInfo, **kwargs):
        self.fab = kwargs.pop('fab', getFab())

if __name__ == '__main__':
    from pprint import pprint as ppr
    from user import  getUsers, CacheUsers
    fab = getFab()
    users = getUsers(fab)
    with CacheUsers(users) as cu:
        tf = TaskInfoFactory()
        print tf.deadline(234)
