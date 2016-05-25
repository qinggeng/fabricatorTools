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
        objType = objInfo['type']
        if objType in self.getters:
            return self.getters[objType](fab, objPHID)
        return None

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
kTransactionTypeEdge = 'core:edge'
kTransactionTypePriority = 'priority'

class TransactionDescriber(object):
    __metaclass__ = Singleton
    def __init__(self):
        self.describers = {}
        pass
    def addDescriber(self, transactionType, destType, describer):
        key = transactionType + "=>" + destType
        self.describers[key] = describer

    def describe(self, fab, transaction, destType = 'text'):
        key = transaction['transactionType'] + '=>' + destType
        if key in self.describers:
            return self.describers[key](fab, transaction)
        Banner().addLine('INDESCRIBALE TRANSACTION').output()
        ppr(transaction)
        raise Exception("undescribale transaction, type=" + transaction['transactionType'])

def transactionDescriber(transactionType, destType):
    def transactionDescriberRegister(func):
        describer = TransactionDescriber()
        describer.addDescriber(transactionType, destType, func)
    return transactionDescriberRegister

@transactionDescriber(kTransactionTypeStatus, "text")
def describeStausTransactionToText(fab, transaction):
    oldVal = transaction['oldValue']
    newVal = transaction['newValue']
    return u"状态变更：" + oldVal + " => " + newVal

@transactionDescriber(kTransactionTypeSubscribe, "text")
def descriptSubscribeTransactionToText(fab, transaction):
    oldVal = transaction['oldValue']
    newVal = transaction['newValue']
    oldVal = UserInfo().getUsersRealName(oldVal)
    newVal = UserInfo().getUsersRealName(newVal)
    if type(oldVal) == list:
        oldVal = reduce(lambda x, y: x + u' ' + y, oldVal, u"")
    if type(newVal) == list:
        newVal = reduce(lambda x, y: x + u' ' + y, newVal, u"")
    return u"cc：" + oldVal + u" => " + newVal

@transactionDescriber(kTransactionTypeReassign, "text")
def descriptReassignTransactionToText(fab, transaction):
    oldVal = transaction['oldValue']
    newVal = transaction['newValue']
    oldVal = UserInfo().getUsersRealName([oldVal])
    newVal = UserInfo().getUsersRealName([newVal])
    if type(oldVal) == list:
        oldVal = reduce(lambda x, y: x + ' ' + y, oldVal, u"")
    if type(newVal) == list:
        newVal = reduce(lambda x, y: x + ' ' + y, newVal, u"")
    return u"任务分配：" + oldVal + u" => " + newVal

@transactionDescriber(kTransactionTypeEditPolicy, "text")
def dscribeEditPolicyTransactionToText(fab, transaction):
    oldVal = transaction['oldValue']
    newVal = transaction['newValue']
    return u"修改编辑策略：" + unicode(oldVal) + " => " + newVal

@transactionDescriber(kTransactionTypeViewPolicy, "text")
def dscribeViewPolicyTransactionToText(fab, transaction):
    oldVal = transaction['oldValue']
    newVal = transaction['newValue']
    return u"修改查看策略：" + unicode(oldVal) + " => " + newVal

@transactionDescriber(kTransactionTypeCreate, "text")
def dscribeCreateTransactionToText(fab, transaction):
    return u"创建对象：" + transaction['transactionPHID']

@transactionDescriber(kTransactionTypeUnblock, "text")
def dscribeCreateTransactionToText(fab, transaction):
    return u"编辑任务的依赖项：" + transaction['taskID']

@transactionDescriber(kTransactionTypeComment, "text")
def dscribeCreateTransactionToText(fab, transaction):
    return u"发表评论：" + transaction['comments'].split('\n')[0]

@transactionDescriber(kTransactionTypePriority, "text")
def dscribePriorityTransactionToText(fab, transaction):
    oldVal = transaction['oldValue']
    newVal = transaction['newValue']
    return u"修改优先级：" + unicode(oldVal) + " => " + unicode(newVal)

@transactionDescriber(kTransactionTypeEdge, "text")
def dscribeEdgeTransactionToText(fab, transaction):
    oldVal = transaction['oldValue']
    newVal = transaction['newValue']
    return u"修改所属项目：" + unicode(oldVal) + " => " + unicode(newVal)
