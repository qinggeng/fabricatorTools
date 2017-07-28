# -*- coding: utf-8 -*-
from datetime import datetime
import json
searchCriterias = [
{
  'desc': '所有未关闭的任务',
  'args': dict(constraints = {"statuses":["open", "r4v"]}),
},
{
  'desc': '5月31号以后所有任务',
  'args': dict(constraints = {
    "modifiedStart": int(datetime.now().strftime("%s")),
    }),
}
]

if __name__ == "__main__":
  print json.dumps(searchCriterias[0], ensure_ascii = False)
