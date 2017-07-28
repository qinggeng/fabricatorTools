# -*- coding: utf-8 -*-
import fab
from fab import Singleton, getTaskInfo, getTaskTransactions
from user import UserInfo
from pprint import pprint as ppr
from printers import Banner

class ObjectTransactionsGetterBuilder(object):
  __metaclass__ = Singleton
  def __init__(self):
    self.getters = {}
    pass

  def addGetter(self, objectType, getter):
    self.getters[objectType] = getter

  def getObjectTransactions(self, fab, objPHID):
    objInfo = fab.phid.query(phids = [objPHID]).response[objPHID]
    ppr(objInfo)
    objType = objInfo['type']
    if objType in self.getters:
      return self.getters[objType](fab, objPHID)
    raise Exception("unknown object type: %s" % objType)

def transactionGetter(objectType):
  def transactionGetter_decorator(func):
    builder = ObjectTransactionsGetterBuilder()
    builder.addGetter(objectType, func)
    return func
  return transactionGetter_decorator

@transactionGetter("TASK")
def getTaskTransactionsByTaskPHID(fab, objectID):
  task = getTaskInfo(fab, objectID)
  task_id = task['id']
  return getTaskTransactions(fab, task_id)[0]

@transactionGetter("MOCK")
def getTaskTransactionsByTaskPHID(fab, objectID):
  task = getTaskInfo(fab, objectID)
  task_id = task['id']
  return getTaskTransactions(fab, task_id)[0]

#constants
kTransactionTypeStatus = 'status'
kTransactionTypeReassign = 'reassign'
kTransactionTypeSubscribe = 'core:subscribers'
kTransactionTypeTitle = 'title'
kTransactionTypeCustomField = 'core:customfield'
kTransactionTypeEditPolicy = 'core:edit-policy'
kTransactionTypeViewPolicy = 'core:view-policy'
kTransactionTypeCreate = 'core:create'
kTransactionTypeUnblock = 'unblock'
kTransactionTypeComment = 'core:comment'
kTransactionTypeCustomfield = 'core:customfield'
kTransactionTypeColumn = 'core:columns'
kTransactionTypeDescription = 'description'
kTransactionTypeEdge = 'core:edge'
kTransactionTypePriority = 'priority'
kTransactionTypeMergedFrom = 'mergedfrom'
kTransactionTypeMergedInto = 'mergedinto'
kTransactionTypeTitle = 'title'

class TransactionFormatter(object):
  __metaclass__ = Singleton
  def __init__(self):
    self.describers = {}
    pass
  def addFormatter(self, transactionType, destType, describer):
    key = transactionType + "=>" + destType
    self.describers[key] = describer

  def format(self, fab, transaction, destType = 'text'):
    key = transaction['transactionType'] + '=>' + destType
    if key in self.describers:
      return self.describers[key](fab, transaction)
    Banner().addLine('INDESCRIBALE TRANSACTION').output()
    ppr(transaction)
    raise Exception("undescribale transaction, type=" + transaction['transactionType'])

def transactionFormatter(transactionType, destType):
  def transactionFormatterRegister(func):
    describer = TransactionFormatter()
    describer.addFormatter(transactionType, destType, func)
  return transactionFormatterRegister

@transactionFormatter(kTransactionTypeStatus, "text")
def formatStausTransactionToText(fab, transaction):
  oldVal = transaction['oldValue']
  newVal = transaction['newValue']
  return u"状态变更：" + oldVal + " => " + newVal

@transactionFormatter(kTransactionTypeSubscribe, "text")
def formatSubscribeTransactionToText(fab, transaction):
  oldVal = transaction['oldValue']
  newVal = transaction['newValue']
  oldVal = UserInfo().getUsersRealName(oldVal)
  newVal = UserInfo().getUsersRealName(newVal)
  if type(oldVal) == list:
    oldVal = reduce(lambda x, y: x + u' ' + y, oldVal, u"")
  if type(newVal) == list:
    newVal = reduce(lambda x, y: x + u' ' + y, newVal, u"")
  return u"cc：" + oldVal + u" => " + newVal

@transactionFormatter(kTransactionTypeReassign, "text")
def formatReassignTransactionToText(fab, transaction):
  oldVal = transaction['oldValue']
  newVal = transaction['newValue']
  if oldVal != None:
    oldVal = UserInfo().getUsersRealName([oldVal])
  else:
    oldVal = u''
  if newVal != None:
    newVal = UserInfo().getUsersRealName([newVal])
  else:
    newVal = u''
  if type(oldVal) == list:
    oldVal = reduce(lambda x, y: x + ' ' + y, oldVal, u"")
  if type(newVal) == list:
    newVal = reduce(lambda x, y: x + ' ' + y, newVal, u"")
  return u"任务分配：" + oldVal + u" => " + newVal

@transactionFormatter(kTransactionTypeEditPolicy, "text")
def formatEditPolicyTransactionToText(fab, transaction):
  oldVal = transaction['oldValue']
  newVal = transaction['newValue']
  return u"修改编辑策略：" + unicode(oldVal) + " => " + newVal

@transactionFormatter(kTransactionTypeViewPolicy, "text")
def formatViewPolicyTransactionToText(fab, transaction):
  oldVal = transaction['oldValue']
  newVal = transaction['newValue']
  return u"修改查看策略：" + unicode(oldVal) + " => " + newVal

@transactionFormatter(kTransactionTypeCreate, "text")
def formatCreateTransactionToText(fab, transaction):
  return u"创建对象：" + transaction['transactionPHID']

@transactionFormatter(kTransactionTypeUnblock, "text")
def formatCreateTransactionToText(fab, transaction):
  return u"编辑任务的依赖项：" + transaction['taskID']

@transactionFormatter(kTransactionTypeComment, "text")
def formatCreateTransactionToText(fab, transaction):
  return u"发表评论：" + transaction['comments'].split('\n')[0]

@transactionFormatter(kTransactionTypePriority, "text")
def formatPriorityTransactionToText(fab, transaction):
  oldVal = transaction['oldValue']
  newVal = transaction['newValue']
  return u"修改优先级：" + unicode(oldVal) + " => " + unicode(newVal)

@transactionFormatter(kTransactionTypeEdge, "text")
def formatEdgeTransactionToText(fab, transaction):
  oldVal = transaction['oldValue']
  newVal = transaction['newValue']
  return u"修改所属项目：" + unicode(oldVal) + " => " + unicode(newVal)

@transactionFormatter(kTransactionTypeMergedFrom, "text")
def formatMergedFromTransactionToText(fab, transaction):
  newVal = transaction['newValue']
  return u"合并T%s" % newVal.keys()[0]

@transactionFormatter(kTransactionTypeMergedInto, "text")
def formatMergedIntoTransactionToText(fab, transaction):
  newVal = transaction['newValue']
  return u"将TASK合并到 %s" % newVal

@transactionFormatter(kTransactionTypeDescription, "text")
def formatCreateTransactionToText(fab, transaction):
  return u"修改任务描述：" + transaction['newValue'].split('\n')[0]

@transactionFormatter(kTransactionTypeTitle, "text")
def formatCreateTransactionToText(fab, transaction):
  oldVal = transaction['oldValue']
  newVal = transaction['newValue']
  return u"修改任务描述：%s => %s" % (oldVal, newVal) 

@transactionFormatter(kTransactionTypeColumn, "text")
def formatColumnTransactionToText(fab, transaction):
  newVal = transaction['newValue'][0]
  columnPHID = newVal[u"columnPHID"]
  colInfo = fab.phid.query(phids=[columnPHID]).response
  return u"将任务移动到“%s”列" % colInfo.values()[0]['fullName']

@transactionFormatter(kTransactionTypeCustomfield, "text")
def formatCustomFieldTransactionToText(fab, transaction):
  return u"修改自定义属性"
