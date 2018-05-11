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
from vikinlu.util import cms_rpc
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
db.clear_intent_question()


def test_sensitive():
    domain = db.Domain.objects.get(name="C")
    sensitive = Sensitive.get_sensitive(str(domain.pk))
    assert(set(sensitive._words) == set([u"共产党", u"毛泽东", u"法轮功"]))
    assert(sensitive.detect(u'共产党万岁') == True)
    assert(sensitive.detect(u'你叫什么') == False)


def test_slot_recognizer():
    domain = db.Domain.objects.get(name="C")
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
    domain = db.Domain.objects.get(name="C")
    service.train(str(domain.pk), ("logistic", "0.1"))
    label_data = cms_rpc.get_tree_label_data(str(domain.pk))
    db.assert_intent_question(str(domain.pk), label_data)


def test_question_generation():
    #  TODO:  move to S-EVECMS
    domain = db.Domain.objects.get(name="C")
    label_data = cms_rpc.get_tree_label_data(str(domain.pk))
    questions = zip(*label_data)[2]
    assert(u'周黑鸭' in questions)
    assert(u'鸭鸭' in questions)
    assert(u'鸭鸭' in questions)
    assert(u'你叫什么呢？' in questions)
    assert(u'鸭鸭怎么走' in questions)


# mock_label_data = set([("treenode_id", "intent", "question"), ('tr', 'lb', 'q')])

def stp_word(stp_dir, question):
    with open(stp_dir, "r") as f:
        lines = f.readlines()
        stopwords = set([line.strip().decode("utf-8") for line in lines])
    segs = jieba.cut(question, cut_all=False)
    final = ""
    for seg in segs:
        if seg not in stopwords:
            final += seg
    return final

def create_mock_label_data():
    path1 = os.path.abspath(os.path.join(os.getcwd(), "../../guangkai.txt"))
    path2 = os.path.abspath(os.path.join(os.getcwd(), "../../VikiNLP/data/stopwords.txt"))
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
        # u_item[2] = stp_word(path2, u_item[2])
        u_item = tuple(u_item)
        mock_label_list.append(u_item)
    mock_label_data = set(mock_label_list)
    return mock_label_data

def create_mock_context(mock_label_data):
    mock_context = {}
    context_list = set([(intent, intent, treenode_id) for treenode_id, intent, question in mock_label_data])
    mock_context["agents"] = list(context_list)


    # print mock_context
    return mock_context

def test_train():

    mock_label_data = create_mock_label_data()
    service = NLUService()
    domain_id = str(db.Domain.objects.get(name="C").pk)
    cms_rpc.get_tree_label_data = mock.Mock(return_value=mock_label_data)
    service.train(domain_id, ("logistic", "0.1"))
    db.assert_intent_question(domain_id, mock_label_data)
    #  TODO:  模型训练


def test_intent():

    mock_label_data = create_mock_label_data()
    mock_context = create_mock_context(mock_label_data)
    domain_id = str(db.Domain.objects.get(name="C").pk)
    intent_object = IntentRecognizer.get_intent_recognizer(domain_id)
    for data in mock_label_data:
        tr, intent, question = data
        try:
            assert(intent == intent_object.strict_classify(mock_context, question)[0])
        except:
            assert(question in [u"存款利息", u"粤通卡", u"信用卡还款"])
        kk = intent_object.fuzzy_classify(mock_context, question)
        print kk
            # print
            # print
            # print intent
            # print ("intent"*5)
            # print question
            # print ("question"*5)
            # print intent_object.strict_classify(mock_context, question)[0]
            # print ("strict"*5)
            # print
            # print
        # assert (intent == intent_object.strict_classify(mock_context, question)[0])
    # mock_fuzzy_result = []
    #  TODO:  <07-05-18, yourname> #

def test_train2():
    domain_id = str(db.Domain.objects.get(name="C").pk)
    service = NLURobot(domain_id)
    service.train("c")





# TODO: casual talk test

if __name__ == '__main__':
    assert(False)
