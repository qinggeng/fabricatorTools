#-*- coding: utf-8 -*-
import settings
import json
configs = {
  'priority': map(lambda x: {'val': x[1], 'display': x[0]}, settings.PRIORITY_VALUES.items()),
  'severity': map(lambda x: {'val': x[0], 'display': x[1]}, settings.SEVERITY_NAMES.items()),
  'status': map(lambda x: {'val': x[1], 'display': x[0]}, settings.STATUS_NAMES.items()),
}
print json.dumps(configs, ensure_ascii = False)

