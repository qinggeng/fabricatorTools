#-*- coding: utf-8 -*-
import sys, argparse
import pygraphviz
import networkx as nx
from networkx.drawing.nx_agraph import write_dot
from functools import partial
from fab import getFab
from diagnosis.printers import Banner
from diagnosis.debugTools import runcmd
from prettyprint import pp as ppr
from user import getUsers, CacheUsers, UserInfo
from datetime import datetime
from uuid import uuid4

def enumerateDepeneds(taskInfo, fab, visitedPhids, callback = None):
    if taskInfo['phid'] in visitedPhids:
        return
    visitedPhids.add(taskInfo['phid'])
    dependPhids = taskInfo['dependsOnTaskPHIDs']
    if len(dependPhids) == 0:
        return
    deppends = fab.maniphest.query(phids = dependPhids).response
    for deppend in deppends.values():
        if None != callback:
            callback(taskInfo, deppend)
        enumerateDepeneds(deppend, fab, visitedPhids, callback)

def formatTask(t):
    return u"T{id}: {title}".format(id = t['id'], title = t['title'])

def printDepends(t, d):
    print u"{d}->{t}".format(t = formatTask(t), d = formatTask(d))

def getTaskPoint(fab, t):
    try:
        resp = fab.maniphest.search(queryKey = None, constraints={'ids': [int(t['id'])]}).response
        return resp['data'][0]['fields']['points']
    except Exception, e:
        return ""

def getTaskOwner(t):
    fab = getFab()
    ui = UserInfo()
    ownerPHID = t['ownerPHID']
    if None == ownerPHID:
        return u""
    ret = ui.getUsersRealName([ownerPHID])
    if len(ret) == 0:
        return u""
    return ret[0]

def getTaskDeadline(t):
    aux = t["auxiliary"]
    deadline = aux["std:maniphest:bestrun:deadline"]
    if None == deadline:
        return u"TBD"
    return datetime.fromtimestamp(deadline).strftime("%Y年%m月%d日 %H:%M").decode('utf-8')

def makeTaskNode(t):
    labelTemplate = u"""<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
<TR>
    <TD COLSPAN="2">{title}</TD>
</TR>
<TR>
    <TD>负责人</TD><TD>{owner}</TD>
</TR>
<TR>
    <TD>预计截止时间</TD><TD>{deadline}</TD>
</TR>
<TR>
    <TD>预估工时</TD><TD>{points}</TD>
</TR>
</TABLE>>"""
    kwargs = {}
    title = formatTask(t)
    kwargs['title'] = title
    owner = getTaskOwner(t)
    if "" == owner:
        owner = u'<FONT COLOR="#FF0000"><B>未定</B></FONT>'
    kwargs['owner'] = owner
    deadline = getTaskDeadline(t)
    if deadline == "TBD":
        deadline = u'<FONT COLOR="#FF0000"><B>未定</B></FONT>'
    kwargs['deadline'] = deadline
    fab = getFab()
    points = getTaskPoint(fab, t)
    if "" == points or None == points:
        points = u'<FONT COLOR="#FF0000"><B>未定</B></FONT>'
    kwargs['points'] = points
    ret = labelTemplate.format(**kwargs)
    return ret

def addTaskNode(g, t):
    color = "#000000"
    tid = t['id']
    taskNodeDict = {'shape': 'note', 'style':'filled', 'fontname':u'微软雅黑', 'fontsize': '12'}
    if t["auxiliary"]["std:maniphest:bestrun:deadline"] == None:
#        taskNodeDict['fillcolor'] = '#FFFF00'
        taskNodeDict['fillcolor'] = '#FFFFCC'
        pass
    else:
        deadline = datetime.fromtimestamp(t["auxiliary"]["std:maniphest:bestrun:deadline"])
        if deadline < datetime.now():
            taskNodeDict['fillcolor'] = '#FF0000'
            taskNodeDict['fontcolor'] = '#FFFFFF'
        else:
            taskNodeDict['fillcolor'] = '#FFFFFF'
    if t['isClosed'] == True:
        taskNodeDict['fillcolor'] = "#00ff00"
    g.add_node(tid, label = makeTaskNode(t), **taskNodeDict)
    return tid

def drawDependGraph(g, t, d):
    tid = addTaskNode(g, t)
    did = addTaskNode(g, d)
    g.add_edge(did, tid, tooltip=u"T%s -> T%s" % (did, tid))

Banner().addLine('Start Genearte Key Paths').output()
argsParser = argparse.ArgumentParser()
argsParser.add_argument("--tasks", help = u"root tasks")
argsParser.add_argument("--output", help = u"output svg file path")
args = argsParser.parse_args()
dotFileName = str(uuid4()) + ".dot"
svgPath = args.output
#args = argsParser.parse_args("--tasks=228,229,230,231,233,234,235,236".split())
tasks = args.tasks.split(',')
fab = getFab()

g = nx.DiGraph()
#Error: Layout type: "neat" not recognized. Use one of: circo dot fdp neato nop nop1 nop2 osage patchwork sfdp twopi
g.graph['graph'] = {'rankdir':'LR', 'splines':'ortho', 'layout': 'dot', 'nodesep': '0.5'}
graphMaker = partial(drawDependGraph, g)

users = getUsers(fab)
with CacheUsers(users) as cu:
    visitedTasks = set()
    for tif in map(lambda x: fab.maniphest.info(task_id = int(x)).response, tasks):
        enumerateDepeneds(tif, fab, visitedTasks, graphMaker)

write_dot(g, dotFileName)
cmd = 'cat "{dot}" |dot -Gconcentrate=true -Tsvg -o "{svg}"'.format(dot = dotFileName, svg = svgPath)
runcmd(cmd)
#runcmd("cat temp.dot |dot -Gconcentrate=true -Tsvg -o test.svg && open test.svg -a FireFox")
