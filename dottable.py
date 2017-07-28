#-*- coding: utf-8 -*-
from diagnosis.debugTools import runcmd
from prettyprint import pp as ppr
class Table(object):
    def __init__(self):
        self.rows = []
    def render(self):
        tableTamplate = u"""
        <TABLE BORDER = "0" CELLBORDER="1" CELLSPACING="0">
            {rows}
        </TABLE>
        """
        rowStr = u""
        for row in self.rows:
            rowStr += row.render() + u"\n"
        return tableTamplate.format(rows = rowStr)

class Row(object):
    def __init__(self, table, contentRender):
        self.table = table
        self.contentRender = contentRender

    def colCount(self):
        return 2

    def render(self):
        return u"<TR>{rowContent}</TR>".format(rowContent = self.contentRender())

def getTimestamp(dt):
    return (dt - datetime(1970, 1, 1)).total_seconds()

def titleRowRenderer(task, table):
    rowTemplate = u"""<TD{stateColor}></TD><TD{colspan}>{title}</TD>"""
    stateColor = u""
    colspan = u""
    title = u""
    #state color
    maxColCount = reduce(lambda x, y: max(x, y.colCount()), table.rows, 2)
    colspan = u' COLSPAN="%d"' % (maxColCount, )
    #title
    titleDetail = task['title']
    titleColor = u""
    if task['isClosed'] == True:
        titleDetail = u"<S>%s</S>" % (task['title'], )
        titleColor = ur' COLOR="#888888"'
        stateColor = u' BGCOLOR="#888888"'
    else:
        try:
            deadline = datetime.fromtimestamp(task['deadline'])
            if (datetime.today() - deadline).days < 7:
                stateColor = u' BGCOLOR="#FF0000"'
        except Exception, e:
            stateColor = u' BGCOLOR="#FF8800"'
            pass
    if len(stateColor) > 0:
        stateColor += u' ROWSPAN="%d"' % len(table.rows)
    titleDetalTemplate = ur'<FONT FACE="微软雅黑"{titleColor}>{titleDetail}</FONT>'
    title = titleDetalTemplate.format(titleColor = titleColor, titleDetail = titleDetail)
    return rowTemplate.format(stateColor = stateColor, title = title, colspan = colspan)

def deadlineRowRender(task, table):
    rowTemplate = ur'<TD>预计截止时间</TD><TD>{deadline}</TD>'
    deadline = u""
    ddate = u""
    remainsStr = u""
    try:
        deadlineDt = datetime.fromtimestamp(task['deadline'])
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


if __name__ == '__main__':
    from datetime import date, time, datetime, timedelta
    from diagnosis.printers import Banner
    from functools import partial
    Banner().addLine(u"Graphviz Node Table Generator").output()
    testData = {
            'deadline': getTimestamp(datetime.today() - timedelta(days = 1)),
            'deadline': "",
            'deadline': getTimestamp(datetime.today() + timedelta(days = 7)),
            'plan-kick-off-date': getTimestamp(datetime.today() - timedelta(days = 10)),
            'isClosed': True,
            'isClosed': False,
            'title': 'Test Task 1',
            }
    t = Table()
    titleRow = Row(t, partial(titleRowRenderer, testData, t))
    t.rows.append(titleRow)
    deadlineRow = Row(t, partial(deadlineRowRender, testData, t))
    t.rows.append(deadlineRow)
    with open('tableTest.dot','w') as f:
        f.write(u"""
digraph g {{
struct [shape = plaintext, label=<
{nodeTable}>];
}}
    """.format(nodeTable = t.render()).encode('utf-8'))
        f.flush()
        runcmd("cat tableTest.dot | dot -T svg -o tableTest.svg && open tableTest.svg -a FireFox")
