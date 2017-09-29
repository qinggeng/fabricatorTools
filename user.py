# -*- coding: utf-8 -*-
import fab, settings
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

  def getUserByRealName(self, realName):
    ret = filter(lambda x: x['realName'] == realName, self.users.values())
    if len(ret) != 1:
      raise Exception(u"not found or same real name for '{n}'".format(n = realName))
    return ret[0]

  def phid2realname(self, phid):
    try:
      return self.users[phid]['realName']
    except Exception, e:
      return "Nobody"

  def orderedUsers(self, 
    field = settings.USER_ORDER_FIELD, 
    orders = settings.USER_ORDERS):
    keys = map(lambda x: x[field], orders)
    ret = []
    unordered = self.users.values()[:]
    for key in keys:
      for user in self.users.values():
        if user[field] == key:
          ret.append(user)
          try:
            index = unordered.index(user)
            unordered.pop(index)
          except Exception, e:
            pass
    return ret + unordered
    

class CacheUsers(object):
  def __init__(self, users):
    self.users = users

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
    self.ui.getUserByRealName = self.cui.getUserByRealName
    self.ui.orderedUsers = self.cui.orderedUsers
    self.ui.phid2realname = self.cui.phid2realname

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
  import json
  fab = getFab()
  users = getUsers(fab)
  print json.dumps(users, ensure_ascii = False)
