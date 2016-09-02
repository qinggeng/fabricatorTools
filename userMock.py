#-*- coding: utf-8 -*-
import requests, re
import settings
from prettyprint import pp
kSiteUrl = settings.SITE['URL']

patterns = {
    'csrfCapture': re.compile(r'initBehaviors\([^\)]+\)'),
    'csrfValCapture': re.compile(r'"current": *"([^"]+)"')
}
class FabMock(object):
    def __init__(self):
        self.patterns = {
            'csrfCapture': re.compile(r'initBehaviors\([^\)]+\)'),
            'csrfValCapture': re.compile(r'"current": *"([^"]+)"'),
            'phid': re.compile(r'href="/search/rel/task\.has-subtask/(?P<phid>[^/]+)\/"'),
        }
        self.entryPoints = {
            'login': kSiteUrl + 'auth/login/password:self/',
            'editParent': kSiteUrl + 'search/rel/task.has-parent/{taskPhid}/',
            'taskInfo': kSiteUrl + 'T{tid}',
            }

    def login(self, username, password, csrfToken, session):
        entryPoints = self.entryPoints
        formData ={
            "__csrf__"   : csrfToken,
            "__dialog__" : "1",
            "__form__"   : "1",
            "password"   : password,
            "username"   : username,
        }
        return session.post(entryPoints['login'], data = formData)

    def getCsrfValue (self, txt):
        patterns = self.patterns
        m = patterns['csrfCapture'].search(txt)
        if m == None:
            raise Exception("Can not find 'initBehaviors' in tex")
        jstr = m.group(0)
        m = patterns['csrfValCapture'].search(jstr)
        csrfToken = m.group(1)
        return csrfToken

    def getTaskPhid(self, tid, session):
        patterns = self.patterns
        entryPoints = self.entryPoints
        entryPoint = entryPoints['taskInfo'].format(tid = tid)
        resp = session.get(entryPoint)
        m = patterns['phid'].search(resp.text)
        phid = m.group('phid')
        csrfToken = self.getCsrfValue(resp.text)
        return (phid, csrfToken)

    def addTaskParent(self, phid, parent, csrf, session):
        entryPoints = self.entryPoints
        entryPoint = self.entryPoints['editParent'].format(taskPhid = phid)
        paramsTemplate = u"""__ajax__=true&&__csrf__={csrf}&&__csrf__={csrf}&&__dialog__=1&&__form__=1&&__form__=1&&__metablock__=9&&__submit__=true&&__wflow__=true&&phids={parent}"""
        params = paramsTemplate.format(csrf = csrf, parent = parent)
        return session.post(entryPoint, data = params)

    def updateTaskParent(self, phid, oldParentList, newParentList, csrf, session):
        entryPoints = self.entryPoints
        entryPoint = self.entryPoints['editParent'].format(taskPhid = phid)
        paramsTemplate = u"""__ajax__=true&&__csrf__={csrf}&&__csrf__={csrf}&&__dialog__=1&&__form__=1&&__form__=1&&__metablock__=9&&__submit__=true&&__wflow__=true&&initialPHIDs={oldParents}&&phids={newParents}"""
        params = paramsTemplate.format(csrf = csrf, oldParents = oldParentList, newParents = newParentList)
        return session.post(entryPoint, data = params)


if __name__ == '__main__':
    session = requests.Session()
    mock = FabMock()
    resp = session.get(kSiteUrl)
    csrfToken = mock.getCsrfValue(resp.text)
    resp = mock.login(settings.USER['username'], settings.USER['password'], csrfToken, session)
    csrfToken = mock.getCsrfValue(resp.text)
    print csrfToken
    phid, csrfToken = mock.getTaskPhid(16, session)
    print phid
    print csrfToken
    parentid, csrcToken = mock.getTaskPhid(11, session)
    print parentid
    print csrfToken

#    resp = mock.addTaskParent(phid, parentid, csrfToken, session)

#    print resp.text

