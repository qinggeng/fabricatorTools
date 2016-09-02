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
        

if __name__ == '__main__':
   pif = ProjectInfoFactory()
   from prettyprint import pp
   pp(map(lambda x: x['name'], pif.allProjects()))
   print pif.projectsByName([u"测试用项目"])
"""
老项目维护,
Best Components,
第二阶段,
系统和流程,
Phabricator Maintain,
Best Browser Components,
满意云-20-满意云APP,
统计自动化,
满意云-10-医患关系管理系统,
Bugs,
满意云通用版本V2,
TSK服务端,
Best Tools,
满意云-40-智慧采集（自助机版）,
Best iOS Components,
Team Building,
巡店App,
满意云鼓楼版本,
Best Android Components,
满意云-60-图表接口服务,
研发管理系统和流程,
满意云-50-智慧采集（现场调查版）,
五星TSK,
Best Java Components,
第一阶段,
文档和规范,
满意云,
满意云-70-坐席云,
满意云-30-智慧采集（微信版）,
Study & Research,
满意云-99-推广和技术支持,
第三阶段,
满意云-98-实施运营管理,
TSK客户端
"""
