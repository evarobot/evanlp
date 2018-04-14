#!/usr/bin/env python
# encoding: utf-8

import logging
import mongoengine
import mock

from vikicommon.log import init_logger
init_logger(level="DEBUG", path="./")

from vikinlu.config import ConfigMongoTest
from vikinlu.filters import Sensitive
from vikinlu.slot import SlotRecognizer
from vikinlu.service import NLUService
from vikinlu.util import dm_rpc, cms_rpc
import util as db
from evecms.models import (
    Domain,
    Slot
)

log = logging.getLogger(__name__)

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
    slot_ids = [d_slot["id"] for d_slot in slots]
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
        ret = slot.recognize(question, slot_ids)
        assert(ret == {u"location": u"耐克"})
    for question in where_query2:
        ret = slot.recognize(question, slot_ids)
        assert(ret == {u"location": u"周黑鸭"})
    for question in name_query:
        ret = slot.recognize(question, slot_ids)
        assert(ret == {})


def test_train():
    db.clear_intent_question()
    mock_data = {
        'name.query': [
            u'你叫什么名字',
            u'你好，请问你怎么称呼?',
            u'你叫什么呢？'
        ],
        'where.query': [
            u'耐克店怎么走？',
            u'耐克店在哪里？',
            u'周黑鸭怎么走？',
            u'鸭鸭怎么走？',
            u'周黑鸭在哪里？',
            u'鸭鸭在哪里？',

        ]
    }
    dm_rpc.get_label_data = mock.Mock(return_value=mock_data)
    service = NLUService()
    domain = Domain.objects.get(name="C")
    service.train(str(domain.pk), ("logistic", "0.1"))
    db.assert_intent_question(str(domain.pk), mock_data)
    #  TODO: check fuzzy train result #


def test_predict():
    service = NLUService()
    domain = Domain.objects.get(name="C")
    robot = NLUService.robots[str(domain.pk)]
    slot_ids = [str(slot.pk) for slot in Slot.objects()]
    robot._get_sub_slots = mock.Mock(return_value=slot_ids)

    name_query = {
        'name.query': [
            u'你叫什么名字',
            u'你好，请问你怎么称呼?',
            u'你叫什么呢？'
        ]
    }
    for label, questions in name_query.iteritems():
        for question in questions:
            log.debug(question + "-" * 30)
            ret = service.predict(str(domain.pk), question)
            assert(ret["intent"] == "name.query")
            assert(ret["question"] == question)
            assert(ret["confidence"] == 1.0)
            assert(ret["slots"] == {})

    where_query = {
        'where.query': [
            u'耐克店怎么走？',
            u'耐克店在哪里？',
        ]
    }
    for label, questions in where_query.iteritems():
        for question in questions:
            log.debug(question + "-" * 30)
            ret = service.predict(str(domain.pk), question)
            assert(ret["intent"] == "where.query")
            assert(ret["question"] == question)
            assert(ret["confidence"] == 1.0)
            assert(ret["slots"] == {u"location": u"耐克"})

    where_query2 = {
        'where.query': [
            u'周黑鸭怎么走？',
            u'鸭鸭怎么走？',
            u'周黑鸭在哪里？',
            u'鸭鸭在哪里？',
        ]
    }
    for label, questions in where_query2.iteritems():
        for question in questions:
            log.debug(question + "-" * 30)
            ret = service.predict(str(domain.pk), question)
            assert(ret["intent"] == "where.query")
            assert(ret["question"] == question)
            assert(ret["confidence"] == 1.0)
            assert(ret["slots"] == {u"location": u"周黑鸭"})

    #  TODO: mock robot._intent.strict_classify, check fuzzy classify
    # TODO: casual talk test
