#!/usr/bin/env python
# encoding: utf-8
"""
测试问题扩增和算法
"""

import re
import itertools
import logging

from evanlp.gate import data_gate
from evanlp.config import ConfigLog
from vikicommon.log import init_logger
log = logging.getLogger(__name__)
init_logger(level="DEBUG", path=ConfigLog.log_path)


def synonym_extends(question_str, slot_dict):
    patten = re.compile('[<|>]')
    question_str = patten.sub("/", question_str)
    for i, j in slot_dict.items():
        question_str = question_str.replace(i, ",".join(j))
    question_list = question_str.split("/")
    final_list = [[i.split(",")][0] for i in question_list if i]
    data1 = tuple(final_list)

    ret = (list(itertools.product(*(data1))))
    return ["".join(i) for i in ret]


def expand_slot(d_values):
    pattern = []
    for name, words in d_values.iteritems():
        pattern.append(name)
    return pattern


def expand_questions(domain_name):
    label_templates = data_gate.get_label_data(domain_name)['label_data']

    domains = data_gate.get_all_domains('ALL')['domains']
    domain_name_id = {}
    for domain in domains:
        domain_name_id[domain['name']] = domain['id']

    intents = data_gate.get_domain_intents(domain_name_id[domain_name])['intents']
    label_data = {}
    for intent in intents:
        if intent['name'] in ['casual_talk', 'nonsense']:
            continue
        templates = label_templates[intent['name']]
        ret = data_gate.get_intent_slots(intent['id'])
        d_slots = ret['slots']
        slot_words = {}
        for slot, d_values in d_slots.iteritems():
            # 扩充槽值
            slot_words[slot] = expand_slot(d_values)
        if slot_words:
            questions = []
            for t in templates:
                # 替换问题模板
                ret = synonym_extends(t, slot_words)
                questions.extend(ret)
        else:
            questions = templates
        label_data[intent['name']] = questions

    l_label_data = []
    for label, questions in label_data.iteritems():
        for q in questions:
            l_label_data.append((label, q))

    return label_data, l_label_data


def test_algorithm():
    from evanlp.nlp.classifier.question_classifier import LogisticRegressionClassifier
    label_data, l_label_data  = expand_questions(u"宝洁")
    model = LogisticRegressionClassifier("test")
    model.train(l_label_data)


if __name__ == '__main__':
    test_algorithm()
