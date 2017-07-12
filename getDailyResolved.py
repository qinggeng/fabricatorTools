# -*- coding: utf-8 -*-
import re, sys
dailyReportPath = sys.argv[1]
p = re.compile(ur'(?P<author>^.*) closed (?P<tid>T\d+):(?P<ttitle>.*) as "Resolved".$')
print u"""<html>
<head>
  <meta charset="utf-8">
</head>
<body>
"""
authors = {}
with open(dailyReportPath, 'r') as report:
  for l in report:
    l = l.decode('utf-8')
    m = p.match(l)
    if None != m:
      author = m.group('author')
      if author not in authors:
        authors[author] = set()
      if m.group('tid') not in authors[author]:
        authors[author].add(m.group('tid'))
        print ur'<li><a href="http://192.168.10.240:9080/{t}" target="_blank"><span>{a}</span> <span>{t} {tt}</span></a></li>'.format(a = m.group('author'), t = m.group('tid'), tt = m.group('ttitle'))
print ur"<p>"
for author in authors:
  print ur"{a} 共完成{n}个任务。<br>".format(a = author, n = len(authors[author]))
print ur"</p>"
print """</body>
</html>"""
