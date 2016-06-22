#-*- coding: utf-8 -*-
import sys, argparse
import pygraphviz
import networkx as nx
from networkx.drawing.nx_agraph import write_dot, to_agraph
from functools import partial
from fab import getFab
from diagnosis.printers import Banner
from diagnosis.debugTools import runcmd
from prettyprint import pp as ppr
from user import getUsers, CacheUsers, UserInfo
from datetime import datetime
from uuid import uuid4
from task import TaskInfoFactory
from dottable import Table, Row
import settings

tf = TaskInfoFactory(fab = getFab())

def enumerateDepeneds(taskInfo, fab, visitedPhids, callback = None):
    if taskInfo['phid'] in visitedPhids:
        return
    visitedPhids.add(taskInfo['phid'])
    dependPhids = taskInfo['dependsOnTaskPHIDs']
    if len(dependPhids) == 0:
        addTaskNode(g, taskInfo)
        return
    deppends = tf.precedings(int(taskInfo['id']))
    for deppend in deppends:
        if None != callback:
            callback(taskInfo, deppend)
        enumerateDepeneds(deppend, fab, visitedPhids, callback)

def formatTask(t):
    return tf.longTitle(int(t['id']))

def printDepends(t, d):
    print u"{d}->{t}".format(t = formatTask(t), d = formatTask(d))

def getTaskPoint(t):
    return tf.points(int(t['id']))

def getTaskOwner(t):
    return tf.owner(int(t['id']))

def getTaskDeadline(t):
    return tf.deadline(int(t['id']))

def getTaskDeadlineTimeStamp(t):
    return tf.deadlineTimestemp(int(t['id']))

def getTaskKickoffTime(t):
    return tf.kickoffDate(int(t['id']))

def titleRowRenderer(task, table):
    rowTemplate = u"""<TD{stateColor}></TD><TD{colspan}{taskLink}>{title}</TD>"""
    stateColor = u""
    colspan = u""
    title = u""
    tasklink = u' HREF="{url}T{tid}"'.format(url = settings.SITE['URL'], tid = task['id'])
    #state color
    maxColCount = reduce(lambda x, y: max(x, y.colCount()), table.rows, 2)
    colspan = u' COLSPAN="%d"' % (maxColCount, )
    #title
    titleDetail = formatTask(task)
    titleColor = u""
    if task['isClosed'] == True:
        titleDetail = u"<S>%s</S>" % (titleDetail, )
        titleColor = ur' COLOR="#888888"'
        stateColor = u' BGCOLOR="#888888"'
    else:
        try:
            deadline = datetime.fromtimestamp(getTaskDeadlineTimeStamp(task))
            if (deadline - datetime.now()).days < 3:
                stateColor = u' BGCOLOR="#FF0000"'
            else:
                stateColor = u' BGCOLOR="#008800"'
        except Exception, e:
            stateColor = u' BGCOLOR="#FF8800"'
    stateColor += u' ROWSPAN="%d"' % len(table.rows)
    titleDetalTemplate = ur'<FONT FACE="微软雅黑"{titleColor}>{titleDetail}</FONT>'
    title = titleDetalTemplate.format(titleColor = titleColor, titleDetail = titleDetail)
    return rowTemplate.format(stateColor = stateColor, title = title, colspan = colspan, taskLink = tasklink)

def ownerRowRenderer(task, table):
    owner = getTaskOwner(task)
    if "" == owner:
        owner = u'<FONT COLOR="#FF0000"><B>未定</B></FONT>'
    return ur"""<TD>负责人</TD><TD>{owner}</TD>""".format(owner = owner)

def deadlineRowRenderer(task, table):
    rowTemplate = ur'<TD>预计截止时间</TD><TD>{deadline}</TD>'
    deadline = u""
    ddate = u""
    remainsStr = u""
    try:
        deadlineDt = datetime.fromtimestamp(getTaskDeadlineTimeStamp(task))
        ddate = deadlineDt.strftime('<FONT FACE="微软雅黑" POINT-SIZE="11">%Y年%m月%d日 %H:%M</FONT>').decode('utf-8')
        remains = deadlineDt - datetime.now()
        if task['isClosed'] == False:
            if remains.total_seconds() > 24 * 60 * 60:
                remainsStr = u'<BR/><FONT COLOR="#000000" FACE="微软雅黑" POINT-SIZE="12">剩余%d天</FONT>' % (remains.days,)
            elif remains.total_seconds() > 60 * 60:
                hours = remains.seconds / 3600
                minutes = (remains.seconds % 3600) / 60
                remainsStr = u"剩余%d小时%d分" % (hours, minutes)
            elif remains.total_seconds() <= 0:
                totalSeconds = -int(remains.total_seconds())
                days = totalSeconds / 86400
                hours = totalSeconds / 3600 - days * 24
                minutes = (totalSeconds % 3600) / 60
                remainsStr = ur'<BR/><FONT COLOR="#FF0000" FACE="微软雅黑" POINT-SIZE="12">超期%d天%d小时%d分</FONT>' % (days, hours, minutes)
        ddate = ur' <BR/> %s <BR/>%s ' % (ddate, remainsStr)
    except Exception, e:
        ddate = ur'<FONT COLOR="#FF0000" FACE="微软雅黑" POINT-SIZE="12">待定</FONT>'
    return rowTemplate.format(deadline = ddate)

def kickoffRowRenderer(task, table):
    rowTemplate = ur'<TD>预计开工时间</TD><TD>{kickoff}</TD>'
    try:
        kickoffDate = getTaskKickoffTime(task)
        now = datetime.now()
        if task['isClosed']:
            return rowTemplate.format(kickoff = kickoffDate.strftime("%Y年%m月%d日 %H:%M").decode('utf-8'))
        if (kickoffDate <= now):
            kickoffDate = u'<FONT>{kickoff}</FONT><BR/><FONT COLOR="#FF0000">超期</FONT>'.format(kickoff = kickoffDate.strftime("%Y年%m月%d日 %H:%M").decode('utf-8'))
    except Exception, e:
        kickoffDate = u'<FONT COLOR="#FF0000">未定</FONT>'
    return rowTemplate.format(kickoff = kickoffDate)

def estimateHoursRowRenderer(task, table):
    rowTemplate = u"""<TD>预估工时</TD><TD>{points}</TD>"""
    points = getTaskPoint(task)
    if None == points:
        points = u'<FONT COLOR="#FF0000">未定</FONT>'
    return rowTemplate.format(points = points)
    

def makeTaskLable(t):
    labelTemplate = u"""<
    {labelTable}
    >"""
    table = Table()
    titleRow = Row(t, partial(titleRowRenderer, t, table))
    table.rows.append(titleRow)
    ownerRow = Row(t, partial(ownerRowRenderer, t, table))
    table.rows.append(ownerRow)
    deadlineRow = Row(t, partial(deadlineRowRenderer, t, table))
    table.rows.append(deadlineRow)
    kickoffRow = Row(t, partial(kickoffRowRenderer, t, table))
    table.rows.append(kickoffRow)
    estimateHoursRow = Row(t, partial(estimateHoursRowRenderer, t, table))
    table.rows.append(estimateHoursRow)
    return labelTemplate.format(labelTable = table.render())

def addTaskNode(g, t):
    color = "#000000"
    tid = t['id']
    taskNodeDict = {'shape': 'note', 'style':'filled', 'fontname':u'微软雅黑', 'fontsize': '12', 'fillcolor': '#FFFFCC'}
    g.add_node(tid, label = makeTaskLable(t), **taskNodeDict)
    return tid

def drawDependGraph(g, t, d):
    tid = addTaskNode(g, t)
    did = addTaskNode(g, d)
    g.add_edge(did, tid, tooltip=u"T%s -> T%s" % (did, tid))

Banner().addLine('Start Genearte Key Paths').output()
argsParser = argparse.ArgumentParser()
argsParser.add_argument("--tasks", help = u"root tasks", required = True)
argsParser.add_argument("--output", help = u"output svg file path", required = True)
if len(sys.argv) > 1:
    args = argsParser.parse_args()
else:
#    args = argsParser.parse_args("--tasks=311 --output TSK.svg".split())
#    args = argsParser.parse_args("--tasks=307 --output TSK.svg".split())
    args = argsParser.parse_args("--tasks=228,229,230,231,233,234 --output iPadSurvey.svg".split())
dotFileName = str(uuid4()) + ".dot"
svgPath = args.output
tasks = args.tasks.split(',')
fab = getFab()

g = nx.DiGraph()
#Error: Layout type: "neat" not recognized. Use one of: circo dot fdp neato nop nop1 nop2 osage patchwork sfdp twopi
g.graph['graph'] = {'remincross': 'true', 'rankdir':'LR', 'splines':'ortho', 'layout': 'dot', 'nodesep': '0.5', 'label': u'TSK原型图', 'font-family':u'微软雅黑'}
graphMaker = partial(drawDependGraph, g)

users = getUsers(fab)
with CacheUsers(users) as cu:
    visitedTasks = set()
    for tif in map(lambda x: fab.maniphest.info(task_id = int(x)).response, tasks):
        enumerateDepeneds(tif, fab, visitedTasks, graphMaker)
a = to_agraph(g)
#a.add_subgraph(["144", "290", "226", "98"], rank='same')
#a.add_subgraph(["228", "229", "230", "231", "233"], rank='same')
#a.add_subgraph(["227"], rank='same')
#a.add_subgraph(["234"], rank='same')
#a.add_subgraph(["101", "225", "224", "99", "100", "237", "235", "236"], rank='same')
#write_dot(g, dotFileName)
a.draw(dotFileName, prog='dot')
#cmd = 'cat "{dot}" |dot -Gconcentrate=true -Tsvg -o "{svg}"'.format(dot = dotFileName, svg = svgPath)
cmd = 'cat "{dot}" |dot -Gconcentrate=true -Tsvg -o "{svg}" && open {svg} -a FireFox'.format(dot = dotFileName, svg = svgPath)
runcmd(cmd)
runcmd('rm -f "%s"' % dotFileName)
#runcmd("cat temp.dot |dot -Gconcentrate=true -Tsvg -o test.svg && open test.svg -a FireFox")
