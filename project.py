#-*- coding: utf-8 -*-
from fab import getFab
class ProjectInfoFactory(object):
    def __init__(self, **kwargs):
        fab = kwargs.pop('fab', getFab())
        self.fab = fab

    def allProjects(self, limit = 100):
        fab = self.fab
        projects = fab.project.query(limit = limit).response
        return projects['data'].values()

    def projectsByName(self, names = []):
        fab = self.fab
        try:
            projects = fab.project.query(names = names).response
            return projects['data'].values()
        except Exception, e:
            return []

    def projectNamesByPhids(self, phids):
        fab = self.fab
        try:
            projects = fab.project.query(phids = phids).response['data'].values()
            return map(lambda x: x['name'], projects)
        except Exception, e:
            return []
        

if __name__ == '__main__':
   pif = ProjectInfoFactory()
   from prettyprint import pp
   import json
   print json.dumps(pif.allProjects(), ensure_ascii = False)
