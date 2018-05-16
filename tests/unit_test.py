#!/usr/bin/env python
# encoding: utf-8

import logging
import mongoengine
import mock
import copy
import jieba
import os

from vikicommon.log import init_logger
from vikinlu.config import ConfigMongo
from vikinlu.filters import Sensitive
from vikinlu.slot import SlotRecognizer
from vikinlu.service import NLUService
from vikinlu.util import cms_rpc, PROJECT_DIR, SYSTEM_DIR
from vikinlu.intent import IntentRecognizer
import util as db

from vikinlu.robot import NLURobot

init_logger(level="DEBUG", path="./")
log = logging.getLogger(__name__)
dm_robot_id = "12345"

mongoengine.connect(db=ConfigMongo.database,
                    host=ConfigMongo.host,
                    port=ConfigMongo.port)
log.info('连接Mongo开发测试环境[eve数据库]成功!')
db.clear_intent_question("C")

def mock_get_value(value_id):
    data = {
        'id1': {
            'code': 0,
            'name': u'周黑鸭',
            'words': [u'鸭鸭']
        },
        'id2': {
            'code': 0,
            'name': u'耐克',
            'words': [u'鸭鸭']
        }
    }
    return data[value_id]


def _create_mock_label_data():
    path1 = os.path.join(PROJECT_DIR, "tests/data/guangkai.txt")
    with open(str(path1), "r") as f:
        i = 1
        mock_label_list = list()
        item_copy = f.readline().strip().split("$@")
        lines = f.readlines()
    for line in lines:
        item = line.strip().split("$@")
        if item[0] == item_copy[0]:
            pass
        else:
            i += 1
        item_copy = copy.deepcopy(item)
        item.insert(0, str(i))
        u_item = map(lambda x:x.decode("utf-8"),item)
        u_item = tuple(u_item)
        mock_label_list.append(u_item)
    mock_label_data = set(mock_label_list)
    return mock_label_data
mock_label_data = _create_mock_label_data()

cms_rpc.get_tree_label_data = mock.Mock(return_value=mock_label_data)

cms_rpc.get_filterwords = mock.Mock(return_value={
    'code': 0,
    'words': [u"共产党", u"毛泽东", u"法轮功"]
})

cms_rpc.get_domain_slots = mock.Mock(return_value={
    'code': 0,
    'slots': [
        {
            'name': 'location',
            'id': 'slot_id',
            'values': {
                'id1': u'周黑鸭',
                'id2': u'耐克'
            }
        }
    ]
})

cms_rpc.get_value = mock.Mock(side_effect=mock_get_value)

cms_rpc.get_domain_values = mock.Mock(return_value={
    'code': 0,
    'values': [
        {
            'id': 'id1',
            "name": u'周黑鸭',
            "words": [u'鸭鸭'],
        },
        {
            'id': 'id2',
            "name": u'耐克',
            "words": [],
        }
    ]
})


def _create_mock_context(mock_label_data):
    mock_context = {}
    context_list = set([(intent, intent, treenode_id) for treenode_id, intent, question in mock_label_data])
    mock_context["agents"] = list(context_list)
    return mock_context



def test_sensitive():
    domain_id = "C"
    sensitive = Sensitive.get_sensitive(domain_id)
    assert(set(sensitive._words) == set([u"共产党", u"毛泽东", u"法轮功"]))
    assert(sensitive.detect(u'共产党万岁') == True)
    assert(sensitive.detect(u'你叫什么') == False)


def test_slot_recognizer():
    domain_id = "C"
    slot = SlotRecognizer.get_slot_recognizer(domain_id)
    where_query = [
        u'耐克店怎么走？',
    ]
    where_query2 = [
        u'周黑鸭怎么走？',
        u'鸭鸭怎么走？',
    ]
    name_query = [
        u'你叫什么名字',
    ]
    for question in where_query:
        ret = slot.recognize(question, ['location'])
        assert(ret == {u"location": u"耐克"})
    for question in where_query2:
        ret = slot.recognize(question, ['location'])
        assert(ret == {u"location": u"周黑鸭"})
    for question in name_query:
        ret = slot.recognize(question, ['location'])
        assert(ret == {})


def test_nonsense():
    #  TODO:  <03-05-18, yourname> #
    pass

def atest_train():
    service = NLUService()
    domain_id = "C"
    service.train(domain_id, ("logistic", "0.1"))
    db.assert_intent_question(domain_id, mock_label_data)


def test_intent():
    mock_context = _create_mock_context(mock_label_data)
    domain_id = "C"
    intent_object = IntentRecognizer.get_intent_recognizer(domain_id)
    for data in mock_label_data:
        tr, intent, question = data
        label = intent_object.strict_classify(mock_context, question)[0]
        try:
            label = intent_object.strict_classify(mock_context, question)[0]
            assert(intent == label)
        except:
            print "***", label
        print intent_object.fuzzy_classify(mock_context, question)






# TODO: casual talk test

if __name__ == '__main__':
    assert(False)
