# -*- coding: utf-8 -*-
def vborder(width, ch = u"*"):
    return unicode(reduce(lambda x, y: x + ch, range(width), u""))

class Banner(object):
    def __init__(self, bannerWidth = 60, borderChar = u"*"):
        self.lines = []
        self.bannerWidth = bannerWidth
        self.borderChar = borderChar

    def addLine(self, line):
        self.lines.append(unicode(line))
        return self

    def output(self):
        bc = self.borderChar
        print vborder(self.bannerWidth, bc)
        print bc + vborder(self.bannerWidth - 2, ' ') + bc
        for line in self.lines:
            ln = len(line)
            lpadding = (self.bannerWidth -ln) / 2 - 1
            rpadding = self.bannerWidth - ln - lpadding - 1
            print bc + vborder(lpadding, u" ") + line + vborder(rpadding - 1, u" ") + bc
        print bc + vborder(self.bannerWidth - 2, ' ') + bc
        print vborder(self.bannerWidth, bc)

if __name__ == '__main__':
    Banner(borderChar = u"*").addLine('BANNER').addLine(u'AUTHOR: 黄飏鲲').output()

