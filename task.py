# -*- coding: utf-8 -*-
from fab import getFab
from user import UserInfo
#from datetime import datetime
from datetime import datetime, date, time, timedelta
import settings
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
        deadline = aux["std:maniphest:" + settings.CUSTOM_FIELD_KEYS['deadline']]
        if None == deadline:
            return u"TBD"
        return datetime.fromtimestamp(deadline).strftime("%Y年%m月%d日 %H:%M").decode('utf-8')

    def author(self, tid):
        tif = self.info(tid)
        ui = UserInfo()
        ownerPHID = tif['authorPHID']
        if None == ownerPHID:
            return u""
        ret = ui.getUsersRealName([ownerPHID])
        if len(ret) == 0:
            return u""
        return ret[0]
        return 

    def deadlineTimestemp(self, tid):
        t = self.info(tid)
        aux = t["auxiliary"]
        deadline = aux["std:maniphest:" + settings.CUSTOM_FIELD_KEYS['deadline']]
        return float(deadline)

    def kickoffDate(self, tid):
        t = self.info(tid)
        aux = t["auxiliary"]
        kickoff = aux["std:maniphest:" + settings.CUSTOM_FIELD_KEYS['plans-to-kickoff']]
        if None == kickoff:
            return u"TBD"
        return datetime.fromtimestamp(kickoff)


    def lastModified(self, tid):
        t = self.info(tid)
        return datetime.fromtimestamp(float(t['dateModified']))

    def isClosed(self, tid):
        t = self.info(tid)
        return t['isClosed']

    def status(self, tid):
        t = self.info(tid)
        return t['status']

    def priority(self, tid):
        t = self.info(tid)
        return t['priority']
        

    def points(self, tid):
        try:
            if tid in self.cachedTasks:
                if 'points' in self.cachedTasks[tid]:
                    return self.cachedTasks[tid]['points']
            fab = self.fab
            resp = fab.maniphest.search(queryKey=None, constraints={'ids':[int(tid)]}).response
            ret = resp['data'][0]['fields']['points']
            if None == ret:
                ret = ""
            if tid in self.cachedTasks:
                self.cachedTasks[tid]['points'] = ret
            return ret
        except Exception, e:
            return ""

    def precedings(self, tid):
        tif = self.info(tid)
        dependPhids = tif['dependsOnTaskPHIDs']
        if len(dependPhids) == 0:
            return []
        return self.infoFromPHIDs(dependPhids)
        pass

    def precedingTitles(self, tid):
        infos = self.precedings(tid)
        titles = map(lambda x: self.longTitle(x['id']), infos)
        return titles

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

    def isOverdue(self, tid, refTime):
        try:
            dt = self.deadlineTimestemp(tid)
            deadTime = datetime.fromtimestamp(dt)
            remains = deadTime - refTime
            return remains.total_seconds() <= 0
        except Exception, e:
            pass
        return False

    def remainsTimeDesription(self, tid, refTime):
        try:
            dt = self.deadlineTimestemp(tid)
            deadTime = datetime.fromtimestamp(dt)
            remains = deadTime - refTime
            if remains.total_seconds() > 24 * 60 * 60:
                remainsStr = u'剩余%d天' % (remains.days,)
            elif remains.total_seconds() > 60 * 60:
                hours = remains.seconds / 3600
                minutes = (remains.seconds % 3600) / 60
                remainsStr = u"剩余%d小时%d分" % (hours, minutes)
            elif remains.total_seconds() <= 0:
                totalSeconds = -int(remains.total_seconds())
                days = totalSeconds / 86400
                hours = totalSeconds / 3600 - days * 24
                minutes = (totalSeconds % 3600) / 60
                remainsStr = ur'超期%d天%d小时%d分' % (days, hours, minutes)
            return remainsStr
            pass
        except Exception, e:
            pass
        return u''

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
