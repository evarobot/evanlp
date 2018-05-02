#!/usr/bin/env python
# encoding: utf-8

import logging
import mongoengine
import mock

from vikicommon.log import init_logger
from vikinlu.config import ConfigMongoTest
from vikinlu.filters import Sensitive
from vikinlu.slot import SlotRecognizer
from vikinlu.service import NLUService
from vikinlu.util import cms_rpc
import util as db
from evecms.models import (
    Domain,
    Slot
)

init_logger(level="DEBUG", path="./")
log = logging.getLogger(__name__)
dm_robot_id = "12345"

mongoengine.connect(db=ConfigMongoTest.database,
                    host=ConfigMongoTest.host,
                    port=ConfigMongoTest.port)
log.info('连接Mongo开发测试环境[eve_test数据库]成功!')


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


def test_integration_train():
    service = NLUService()
    domain = Domain.objects.get(name="C")
    service.train(str(domain.pk), ("logistic", "0.1"))
    label_data = cms_rpc.get_tree_label_data(str(domain.pk))
    questions = zip(*label_data)[2]
    assert(u'周黑鸭' in questions)
    assert(u'鸭鸭' in questions)
    assert(u'鸭鸭' in questions)
    assert(u'你叫什么呢？' in questions)
    assert(u'鸭鸭怎么走？' in questions)
    db.assert_intent_question(str(domain.pk), label_data)
    #  TODO: check fuzzy train result #


def atest_predict():
    service = NLUService()
    domain = Domain.objects.get(name="C")
    robot = NLUService.robots[str(domain.pk)]
    slot_names = [slot.name for slot in Slot.objects()]
    robot._get_sub_slots = mock.Mock(return_value=slot_names)

    name_query = {
        'name.query': [
            u'你叫什么呢？'
        ]
    }
    for label, questions in name_query.iteritems():
        for question in questions:
            ret = service.predict(dm_robot_id, str(domain.pk), question)
            assert(ret["intent"] == "name.query")
            assert(ret["question"] == question)
            assert(ret["confidence"] == 1.0)
            assert(ret["slots"] == {})

    location_query = {
        'location.query': [
            u'耐克怎么走？',
            u'耐克在哪里？',
        ]
    }
    for label, questions in location_query.iteritems():
        for question in questions:
            ret = service.predict(dm_robot_id, str(domain.pk), question)
            assert(ret["intent"] == "location.query")
            assert(ret["question"] == question)
            assert(ret["confidence"] == 1.0)
            assert(ret["slots"] == {u"location": u"耐克"})

    location_query2 = {
        'location.query': [
            u'周黑鸭怎么走？',
            u'鸭鸭怎么走？',
        ]
    }
    for label, questions in location_query2.iteritems():
        for question in questions:
            ret = service.predict(dm_robot_id, str(domain.pk), question)
            assert(ret["intent"] == "location.query")
            assert(ret["question"] == question)
            assert(ret["confidence"] == 1.0)
            assert(ret["slots"] == {u"location": u"周黑鸭"})

    #  TODO: mock robot._intent.strict_classify, check fuzzy classify
    # TODO: casual talk test

if __name__ == '__main__':
    assert(False)
