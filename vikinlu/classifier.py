#!/usr/bin/env python
# encoding: utf-8
import logging
import os
import jieba
from collections import namedtuple
from vikinlp.nlp.classifier.question_classifier import QuestionClassfier
from vikinlu.util import SYSTEM_DIR
from vikinlu.model import IntentQuestion, IntentTreeNode

log = logging.getLogger(__name__)

LabelData = namedtuple('LabelData', 'label, question, treenode')


def readfile(path):
    # fp = open(path, "r", encoding='utf-8')
    fp = open(path, "r")
    content = fp.read()
    fp.close()
    return content


stop_words_file = os.path.join(SYSTEM_DIR, "VikiNLP/data/stopwords.txt")
stop_words = readfile(stop_words_file).splitlines()


def strip_stopwords(question):
    segs = jieba.cut(question, cut_all=False)
    left_words = []
    for seg in segs:
        if seg not in stop_words:
            left_words.append(seg)
    return " ".join(left_words)


class QuestionSearch(object):
    def __init__(self, domain_id):
        self.domain_id = domain_id

    def predict(self, question):
        normalized_question = strip_stopwords(question)
        objects = IntentQuestion.objects(domain=self.domain_id, question=normalized_question)
        return objects, 1

    def train(self, label_data):
        IntentQuestion.objects(domain=self.domain_id).delete()
        IntentTreeNode.objects(domain=self.domain_id).delete()

        db_questions = []
        db_label_treenodes = []
        label_treenode = set()
        for td in label_data:
            normalized_question = strip_stopwords(td.question)
            db_questions.append(IntentQuestion(domain=self.domain_id, treenode=td.treenode,
                                label=td.label, question=normalized_question))
            label_treenode.add((td.label, td.treenode))
        for label, treenode in label_treenode:
            db_label_treenodes.append(IntentTreeNode(domain=self.domain_id,
                                                     treenode=treenode, label=label))
        IntentQuestion.objects.insert(db_questions)
        IntentTreeNode.objects.insert(db_label_treenodes)
        IntentTreeNode(domain=self.domain_id, treenode="", label="biz").save()
        IntentTreeNode(domain=self.domain_id, treenode="", label="casual_talk").save()


class FuzzyClassifier(object):
    def __init__(self, domain_id, algorithm):
        self._domain_id = domain_id
        self._classifier = QuestionClassfier.get_classifier(domain_id + "_biz", algorithm)

    def train(self, label_data):
        # save fuzzy model
        return self._classifier.train(label_data)

    def predict(self, question):
        label, confidence = self._classifier.predict(question)
        objects = IntentTreeNode.objects(domain=self._domain_id, label=label)
        return objects, confidence


class BizChatClassifier(FuzzyClassifier):
    chat_label_data = []

    def __init__(self, domain_id, algorithm):
        super(BizChatClassifier, self).__init__(domain_id, algorithm)
        self._classifier = QuestionClassfier.get_classifier(domain_id + "_bizchat", algorithm)

    def train(self, label_data):
        biz_chat_data = []
        for data in label_data:
            biz_chat_data.append(LabelData(label="biz", question=data.question,
                                           treenode=data.treenode))
        if self.chat_label_data == []:
            self._load_chat_label_data()

        biz_chat_data += self.chat_label_data
        return super(BizChatClassifier, self).train(biz_chat_data)

    def _load_chat_label_data(self):
        chat_file = os.path.join(SYSTEM_DIR, "VikiNLP/data/casual_talk.txt")
        with open(chat_file, "r") as f:
            for line in f.readlines():
                question = line.rstrip('\n')
                self.chat_label_data.append(LabelData(label="casual_talk",
                                                      question=question,
                                                      treenode=None))
