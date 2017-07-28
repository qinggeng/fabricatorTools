#-*- coding: utf-8 -*-
from task import TaskInfoFactory
from fab import getFab
from user import getUsers, CacheUsers, UserInfo

import sys, argparse
from diagnosis.printers import Banner
from diagnosis.debugTools import runcmd
from prettyprint import pp as ppr

argsParser = argparse.ArgumentParser()

argsParser.add_argument("--config", help = u"config file", default = "__default__")

args = argsParser.parse_args()

if args.config == "__default__":
    from t2csettings import config
    pass
else:
    pass

fab = getFab()
tf = TaskInfoFactory(fab = fab)
users = getUsers(fab)
columns = [
    (u"标题", tf.longTitle),
    (u"已关闭", tf.isClosed),
    (u"状态", tf.status),
    (u"发起人", tf.author),
    (u"负责人", tf.owner),
    (u"最后修改时间", tf.lastModified),
    (u"计划开始日期", tf.kickoffDate),
    (u"预估工时", tf.points),
    (u"计划截止日期", tf.deadline),
]
with CacheUsers(users) as cu:
    for target in config['exports']:
        title = target['title']
        with open(title+'.csv', 'w') as f:
            tasks = target['tasks']
            f.write(u', '.join(map(lambda x: x[0], columns)).encode('utf-8'))
            f.write('\n')
            for tid in tasks:
                f.write(u', '.join(map(lambda x: unicode(x[1](tid)), columns)).encode('utf-8'))
                f.write('\n')
            f.flush()
            runcmd("cat %s.csv" % title)
