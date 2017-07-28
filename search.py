# -*- coding: utf-8 -*-
from datetime import datetime
from fab import getFab
import fileinput
import argparse, sys, json
from search_criterias import searchCriterias
fab = getFab()
#TODO search by deadline, kickoffs
criteria = searchCriterias[0]
parser = argparse.ArgumentParser()
parser.add_argument('-i', dest = 'src', help = 'search criteria from file')
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
resp = fab.maniphest.search(**criteria['args']).data
print ','.join(map(lambda x: str(x['id']), resp))
