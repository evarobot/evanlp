#!/usr/bin/env python
# encoding: utf-8
import os
import re
import jieba
from vikinlu.model import IntentQuestion
from vikinlu.util import SYSTEM_DIR

stop_words_file = os.path.join(SYSTEM_DIR, "VikiNLU/data/stopwords.txt")
with open(stop_words_file, "r") as f:
    lines = f.readlines()
    stopwords = set([line.strip() for line in lines])


def remove_stopwords(question):
    rep = {}
    for word in stopwords:
        rep[word.decode('utf8')] = ''
    rep = dict((re.escape(k), v) for k, v in rep.iteritems())
    pattern = re.compile("|".join(rep.keys()))
    q = pattern.sub(lambda m: rep[re.escape(m.group(0))], question)
    return q


def assert_intent_question(domain_id, data):
    intent_questions = IntentQuestion.objects(domain=domain_id)
    label_data = set()
    for db_obj in intent_questions:
        label_data.add((db_obj.treenode, db_obj.label, db_obj.question))
    for tuple_obj in data:
        tuple_obj = (int(tuple_obj.treenode), tuple_obj.label,
                     " ".join(list(jieba.cut(tuple_obj.question,
                                             cut_all=False))))
        assert(tuple_obj in label_data)
