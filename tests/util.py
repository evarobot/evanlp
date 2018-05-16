#!/usr/bin/env python
# encoding: utf-8
import os
import jieba
from vikinlu.model import IntentQuestion
from vikinlu.util import SYSTEM_DIR
from evecms.models import Domain, Slot

stop_words_file = os.path.join(SYSTEM_DIR, "VikiNLP/data/stopwords.txt")
with open(stop_words_file, "r") as f:
    lines = f.readlines()
    stopwords = set([line.strip().decode("utf-8") for line in lines])


def strip_stopwords(question):
    segs = jieba.cut(question, cut_all=False)
    left_words = []
    for seg in segs:
        if seg not in stopwords:
            left_words.append(seg)
    return " ".join(left_words)


def clear_intent_question(domain_name):
    IntentQuestion.objects(domain=domain_name)


def assert_intent_question(domain_id, data):
    intent_questions = IntentQuestion.objects(domain=domain_id)
    label_data = set()
    for db_obj in intent_questions:
        label_data.add((db_obj.treenode, db_obj.label, db_obj.question))
    for tuple_obj in data:
        tuple_obj = (tuple_obj[0], tuple_obj[1], strip_stopwords(tuple_obj[2]))
        assert(tuple_obj in label_data)
