#!/usr/bin/env python
# encoding: utf-8

import logging
import mongoengine
import mock

from vikicommon.log import init_logger
from vikinlu.config import ConfigMongo
from vikinlu.filters import Sensitive
from vikinlu.slot import SlotRecognizer
from vikinlu.service import NLUService
from vikinlu.util import cms_rpc
from vikinlu.intent import IntentRecognizer
import util as db
from evecms.models import (
    Domain,
    Slot
)

init_logger(level="DEBUG", path="./")
log = logging.getLogger(__name__)
dm_robot_id = "12345"

mongoengine.connect(db=ConfigMongo.database,
                    host=ConfigMongo.host,
                    port=ConfigMongo.port)
log.info('连接Mongo开发测试环境[eve数据库]成功!')
db.clear_intent_question()


def test_sensitive():
    domain = Domain.objects.get(name="C")
    sensitive = Sensitive.get_sensitive(str(domain.pk))
    assert(set(sensitive._words) == set([u"共产党", u"毛泽东", u"法轮功"]))
    assert(sensitive.detect(u'共产党万岁') == True)
    assert(sensitive.detect(u'你叫什么') == False)


def test_slot_recognizer():
    domain = Domain.objects.get(name="C")
    slot = SlotRecognizer.get_slot_recognizer(str(domain.pk))
    slots = cms_rpc.get_domain_slots(str(domain.pk))['slots']
    slot_names = [d_slot["name"] for d_slot in slots]
    where_query = [
        u'耐克店怎么走？',
        u'耐克店在哪里？',
    ]
    where_query2 = [
        u'周黑鸭怎么走？',
        u'鸭鸭怎么走？',
        u'周黑鸭在哪里？',
        u'鸭鸭在哪里？',
    ]
    name_query = [
        u'你叫什么名字',
        u'你好，请问你怎么称呼?',
        u'你叫什么呢？'
    ]
    for question in where_query:
        ret = slot.recognize(question, slot_names)
        assert(ret == {u"location": u"耐克"})
    for question in where_query2:
        ret = slot.recognize(question, slot_names)
        assert(ret == {u"location": u"周黑鸭"})
    for question in name_query:
        ret = slot.recognize(question, slot_names)
        assert(ret == {})


def test_nonsense():
    #  TODO:  <03-05-18, yourname> #
    pass


def test_integration_train():
    service = NLUService()
    domain = Domain.objects.get(name="C")
    service.train(str(domain.pk), ("logistic", "0.1"))
    label_data = cms_rpc.get_tree_label_data(str(domain.pk))
    db.assert_intent_question(str(domain.pk), label_data)


def test_question_generation():
    #  TODO:  move to S-EVECMS
    domain = Domain.objects.get(name="C")
    label_data = cms_rpc.get_tree_label_data(str(domain.pk))
    questions = zip(*label_data)[2]
    assert(u'周黑鸭' in questions)
    assert(u'鸭鸭' in questions)
    assert(u'鸭鸭' in questions)
    assert(u'你叫什么呢？' in questions)
    assert(u'鸭鸭怎么走' in questions)


mock_label_data = set([("treenode_id", "intent", "question"), ('tr', 'lb', 'q')])


def atest_train():
    service = NLUService()
    domain_id = "C"
    cms_rpc.get_tree_label_data = mock.Mock(return_value=mock_label_data)
    service.train(domain_id, ("logistic", "0.1"))
    db.assert_intent_question("C", mock_label_data)


def atest_intent():
    domain_id = "C"
    intent = IntentRecognizer.get_intent_recognizer(domain_id)
    mock_context = []
    for data in mock_label_data:
        tr, intent, question = q
        assert(intent == intent.strict_classify(mock_context, question)[0])
    mock_fuzzy_result = []
    for data in mock_fuzyy_result:
        tr, intent, question = q
        assert(intent == intent.fuzzy_classify(mock_context, question)[0])



# TODO: casual talk test

if __name__ == '__main__':
    assert(False)
