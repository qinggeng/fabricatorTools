# -*- coding: utf-8 -*-
import fab
from fab import Singleton, getUsers, getFab

class CachedUserInfo(object):
    def __init__(self, users):
        self.users = {}
        for user in users:
            self.users[user['phid']] = user

    def getUsersField(self, userPHIDs, fieldName):
        try:
            return map(lambda x: self.users[x][fieldName], userPHIDs) 
        except Exception, e:
            return []

    def getUsersRealName(self, userPHIDs):
        return self.getUsersField(userPHIDs, 'realName')

    def allUserIds(self):
        return self.users.keys()

class CacheUsers(object):
    def __init__(self, users):
        self.users = users
        pass
    def __enter__(self):
        self.ui = UserInfo()
        try:
            self.getUsersField = ui.getUsersField
        except Exception, e:
            self.getUsersField = None
        try:
            self.allUserIds = ui.allUserIds
        except Exception, e:
            self.allUserIds = None
        try:
            self.getUsersRealName = ui.getUsersRealName
        except Exception, e:
            self.getUsersRealName = None

        self.cui = CachedUserInfo(self.users)
        self.ui.getUsersField = self.cui.getUsersField
        self.ui.allUserIds = self.cui.allUserIds
        self.ui.getUsersRealName = self.cui.getUsersRealName

    def __exit__(self, d1, d2, d3):
        try:
            self.ui.getUsersField = self.getUsersField
        except Exception, e:
            self.ui.getUsersField = None
        try:
            self.ui.allUserIds = self.allUserIds
        except Exception, e:
            self.ui.allUserIds = None
        try:
            self.getUsersRealName = self.getUsersRealName
        except Exception, e:
            self.ui.getUsersRealName = None

class UserInfo(object):
    __metaclass__ = Singleton
    def __init__(self):
        pass

if __name__ == '__main__':
    fab = getFab()
    users = getUsers(fab)
    with CacheUsers(users) as cu:
        ui = UserInfo()
        print ui.getUsersRealName(ui.allUserIds())
