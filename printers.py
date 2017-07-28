# -*- coding: utf-8 -*-
def vborder(width, ch = u"*"):
    return unicode(reduce(lambda x, y: x + ch, range(width), u""))

def terminalPrinter(*args):
    for arg in args:
        print arg,
    print

class Banner(object):
    def __init__(self, bannerWidth = 60, borderChar = u"*", printFunc = None):
        self.lines = []
        self.bannerWidth = bannerWidth
        self.borderChar = borderChar
        if printFunc == None:
            self.printFunc = terminalPrinter

    def addLine(self, line):
        self.lines.append(unicode(line))
        return self

    def output(self):
        printFunc = self.printFunc
        bc = self.borderChar
        printFunc(vborder(self.bannerWidth, bc))
        printFunc(bc + vborder(self.bannerWidth - 2, ' ') + bc)
        for line in self.lines:
            ln = len(line)
            lpadding = (self.bannerWidth -ln) / 2 - 1
            rpadding = self.bannerWidth - ln - lpadding - 1
            printFunc(bc + vborder(lpadding, u" ") + line + vborder(rpadding - 1, u" ") + bc)
        printFunc(bc + vborder(self.bannerWidth - 2, ' ') + bc)
        printFunc(vborder(self.bannerWidth, bc))

if __name__ == '__main__':
    Banner(borderChar = u"*").addLine('BANNER').addLine(u'AUTHOR: 黄飏鲲').output()

