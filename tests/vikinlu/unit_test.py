#!/usr/bin/env python
# encoding: utf-8

import logging
import mongoengine
import mock
import copy
from collections import namedtuple
import os

from vikicommon.log import init_logger
from vikinlu.config import ConfigMongo, ConfigLog
from vikinlu.filters import Sensitive
from vikinlu.slot import SlotRecognizer
from vikinlu.robot import NLURobot
from vikinlu.util import cms_gate, PROJECT_DIR
from vikinlu.model import clear_intent_question
import helper

LabelData = namedtuple("LabelData", "label, question, treenode")
init_logger(level="DEBUG", path=ConfigLog.log_path)
log = logging.getLogger(__name__)
dm_robot_id = "12345"

mongoengine.connect(db=ConfigMongo.database,
                    host=ConfigMongo.host,
                    port=ConfigMongo.port)
log.info('连接Mongo开发测试环境[eve数据库]成功!')


def mock_get_slot_values_for_nlu(slot_id):
    data = {
        'code': 0,
        'data': {
            'values': [
                {
                    'name': u'周黑鸭',
                    'words': [u'鸭鸭', u'鸭翅', u'-小鸭鸭', u'-小鸭翅'],
                    'update_time': '2018-03-03'
                },

                {
                    'name': u'耐克',
                    'words': [u'耐克'],
                    'update_time': '2018-03-03'
                }
            ]
        }
    }
    return data


def _create_mock_label_data():
    path1 = os.path.join(PROJECT_DIR, "tests/data/guangkai.txt")
    mock_label_list = list()
    with open(str(path1), "r") as f:
        i = 1
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
        mock_label_list.append(LabelData(treenode=u_item[0],
                                         label=u_item[1],
                                         question=u_item[2]))
    return mock_label_list

mock_label_data = _create_mock_label_data()

cms_gate.get_tree_label_data = mock.Mock(
    return_value=mock_label_data)

cms_gate.get_filter_words = mock.Mock(return_value={
    'code': 0,
    'data': {
        'words': [u"共产党", u"毛泽东", u"法轮功"]
    }
})

cms_gate.get_domain_slots = mock.Mock(return_value={
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

cms_gate.get_slot_values_for_nlu = mock.Mock(
    side_effect=mock_get_slot_values_for_nlu)

cms_gate.get_domain_values = mock.Mock(return_value={
    'code': 0,
    'values': [
        {
            'id': 'id1',
            "name": u'周黑鸭',
            "words": [u'鸭鸭', u'鸭翅', u'-小鸭鸭', u'-小鸭翅'],
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
    context_list = set([(intent, intent, treenode_id) for intent, question, treenode_id in mock_label_data])
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
        u'鸭翅怎么走？',
        u'小鸭鸭怎么走？',
        u'小鸭翅怎么走？',
    ]
    name_query = [
        u'你叫什么名字',
    ]
    for question in where_query:
        ret = slot.recognize(question, ['location'])
        assert(ret == {u"location": u"耐克"})
    for question in where_query2:
        ret = slot.recognize(question, ['location'])
        if u'小鸭鸭' in question or u'小鸭翅' in question:
            assert(ret == {})
        else:
            assert(ret == {u"location": u"周黑鸭"})
    for question in name_query:
        ret = slot.recognize(question, ['location'])
        assert(ret == {})


def test_nonsense():
    #  TODO:  <03-05-18, yourname> #
    pass


class TestClassifier(object):
    nlurobot = None

    def test_train(self):
        clear_intent_question("A")
        domain_id = "A"
        TestClassifier.nlurobot = NLURobot.get_robot(domain_id)
        TestClassifier.nlurobot.train(("logistic", "0.1"))
        helper.assert_intent_question(domain_id, mock_label_data)

    def test_intent(self):
        self.mock_context = _create_mock_context(mock_label_data)
        self.domain_id = "C"
        self.intent = TestClassifier.nlurobot._intent
        for data in mock_label_data:
            predicted_label = self.intent.strict_classify(self.mock_context,
                                                          data.question)[0]
            if predicted_label != data.label:
                # filtered by priority
                assert(predicted_label == '信用卡什么时候还款')
            else:
                assert(predicted_label == data.label)

        # biz_classifier
        count = 0.0
        for data in mock_label_data:
            predicted = self.intent._biz_classifier.predict(data.question)[0][0]
            if predicted.label == data.label:
                count += 1
        log.info(
            "Biz Classify Precise: {0}".format(count / len(mock_label_data)))
        assert(count >= 0.9)

        # biz vs casual_talk
        count = 0.0
        for data in mock_label_data:
            predicted = self.intent._biz_chat_classifier.predict(data.question)[0][0]
            if predicted.label == 'biz':
                count += 1
        log.info("Biz vs. Chat Precise: {0}".format(count/len(mock_label_data)))

        ## fuzytest
        count = 0.0
        for data in mock_label_data:
            predicted_label = self.intent.fuzzy_classify(self.mock_context, data.question)[0]
            if predicted_label == data.label:
                count += 1
        log.info("Total Precise: {0}".format(count/len(mock_label_data)))
        clear_intent_question("C")



if __name__ == '__main__':
    assert(False)
