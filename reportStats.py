# -*- coding: utf-8 -*-
from datetime import datetime
from fab import getFab
from prettyprint import pp
from user import getUsers, CacheUsers, UserInfo
fab = getFab()
#TODO search by deadline, kickoffs

def reportStatus(taskTrans, status, ui):
  r4vByAuthors = {}
  for tid in taskTrans:
    trans = taskTrans[tid]
    for t in filter(lambda x: x['transactionType'] == 'status' and x['newValue'] == status, trans):
      author = ui.phid2realname(t['authorPHID'])
      if author not in r4vByAuthors:
        r4vByAuthors[author] = set()
      r4vByAuthors[author].add(tid)
  print status + ':'
  for a in r4vByAuthors:
    print a, len(r4vByAuthors[a])

searchCriterias = [
{
  'desc': '5月31号以后所有任务',
  'args': dict(constraints = {
    #"projects": ["儿童脑适能"], 
    #"statuses":["open", "r4v"],
    "modifiedStart": int(datetime.strptime('2017-05-31 00:00', '%Y-%m-%d %H:%M').strftime("%s")),
    }),
}
]
criteria = searchCriterias[0]
resp = fab.maniphest.search(**criteria['args']).data
resp = fab.maniphest.gettasktransactions(ids = map(lambda x: x['id'], resp)).response
users = getUsers(fab)
with CacheUsers(users):
  ui = UserInfo()
  reportStatus(resp, 'r4v', ui)
  reportStatus(resp, 'resolved', ui)
