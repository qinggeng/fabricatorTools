# -*- coding: utf-8 -*-
from datetime import datetime
from fab import getFab
import fileinput
import argparse, sys, json
from search_criterias import searchCriterias
from prettyprint import pp

def searchFab(fab, criteria, searchAll = False):
  if True == searchAll:
    criteria['args']['limit'] = 100
    allTasks = []
    result = fab.maniphest.search(**criteria['args'])
    resp = result.data
    ids = map(lambda x: x['id'], resp)
    allTasks += resp
    while result.cursor['after'] != None:
      criteria['args']['after'] = result.cursor['after']
      result = fab.maniphest.search(**criteria['args'])
      resp = result.data
      ids = map(lambda x: x['id'], resp)
      allTasks += resp
    return allTasks

  resp = fab.maniphest.search(**criteria['args']).data
  return resp

if __name__ == '__main__':
  fab = getFab()
  #TODO search by deadline, kickoffs
  criteria = searchCriterias[0]
  parser = argparse.ArgumentParser()
  parser.add_argument('-i', dest = 'src', help = 'search criteria from file')
  parser.add_argument('--all', help = 'search all results', action = 'store_true')
  args = parser.parse_args()
  if args.src == '-':
    #TODO read criteria from stdin
    searchArgs = sys.stdin.read()
    try:
      searchArgs = json.loads(searchArgs)
      criteria['args'] = searchArgs
    except Exception, e:
      print e
      quit()
  resp = searchFab(fab, criteria, args.all)
  print ','.join(map(lambda x: str(x['id']), resp))
