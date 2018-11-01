#!/usr/bin/env python
# encoding: utf-8
import logging
import os
import pandas

from collections import namedtuple
from vikinlu.config import ConfigData
from vikinlp.classifier.question_classifier import QuestionClassfier
from vikinlu.util import PROJECT_DIR
from vikinlu.model import IntentQuestion, IntentTreeNode

log = logging.getLogger(__name__)


LabelData = namedtuple('LabelData', 'label, question, treenode')


stopwords = []
with open(os.path.join(PROJECT_DIR, "data/stopwords.txt")) as fp:
    for line in fp.readlines():
        stopwords.append(line[:-1])


def remove_stopwords(question):
    words = []
    for w in question:
        if w not in stopwords:
            words.append(w)
    return ''.join(words)


class QuestionSearch(object):
    """
    Classify question by Database searching.
    """
    def __init__(self, domain_id):
        self.domain_id = domain_id

    def predict(self, question):
        """ Normalize question and classify it by database searching.

        Parameters
        ----------
        question : str, question asked by user.

        Returns
        -------
        tuple ([IntentQuestion], float) : Return candicate agents list and
                                          the label confidence.

        """
        normalized_question = remove_stopwords(question)
        objects = IntentQuestion.objects(domain=self.domain_id,
                                         question=normalized_question)
        return objects, 1

    def train(self, label_data):
        """ Save labeld question to database for strict classify.

        Parameters
        ----------
        label_data : [(label, question, treenode), ..], labeld question

        """
        assert(label_data)
        IntentQuestion.objects(domain=self.domain_id).delete()
        IntentTreeNode.objects(domain=self.domain_id).delete()
        db_questions = []
        db_label_treenodes = []
        label_treenode = set()
        for td in label_data:
            td = LabelData(label=td[0], question=td[1], treenode=td[2])
            normalized_question = remove_stopwords(td.question)
            db_questions.append(
                IntentQuestion(domain=self.domain_id, treenode=td.treenode,
                               label=td.label, question=normalized_question))
            label_treenode.add((td.label, td.treenode))
        for label, treenode in label_treenode:
            db_label_treenodes.append(
                IntentTreeNode(domain=self.domain_id,
                               treenode=treenode, label=label))
        IntentQuestion.objects.insert(db_questions)
        IntentTreeNode.objects.insert(db_label_treenodes)
        IntentTreeNode(domain=self.domain_id, treenode=0, label="biz").save()
        IntentTreeNode(domain=self.domain_id, treenode=0,
                       label="casual_talk").save()


class FuzzyClassifier(object):
    def __init__(self, domain_id, algorithm):
        self._domain_id = domain_id
        self._identifier = str(domain_id + "_biz")
        self._classifier = QuestionClassfier.get_classifier(algorithm)
        model_fname = os.path.join(ConfigData.model_data_path,
                                   self._identifier)
        if not self._classifier.load_model(model_fname):
            log.warning("Model has not been trained.")

    def train(self, label_data):
        """ Train model with algorithm and save model to file.

        Parameters
        ----------
        label_data : [(label, question, treenode), ..], labeld question

        """
        # save fuzzy model
        tmp = zip(*label_data)
        tmp = list(tmp)
        y = tmp[0]
        x = tmp[1]
        self._classifier.data = pandas.DataFrame({"Feature": x,
                                                  "Label": y})
        self._classifier.split_data("Feature", "Label", 0.3, 0.5)
        summary = self._classifier.train(x=self._classifier.x_train,
                                         y=self._classifier.y_train)

        model_fname = os.path.join(ConfigData.model_data_path,
                                   self._identifier)
        self._classifier.save_model(model_fname)
        # self._classifier.load_model(model_fname)
        # summary = self._classifier.evaluation(self._classifier.x_valid,
        #                                       self._classifier.y_valid)
        return summary

    def predict(self, question):
        """ Classify question with algorithm model.

        Parameters
        ----------
        question : str, Question inputted by user.

        Returns
        -------
        tuple ([IntentQuestion], float) : Return candicate agents list and
                                          the label confidence.

        """
        label, confidence = self._classifier.predict(question)
        objects = IntentTreeNode.objects(domain=self._domain_id, label=label)
        return objects, confidence


class BizChatClassifier(FuzzyClassifier):
    """
    Classify question to business and casual talk.
    """
    chat_label_data = []

    def __init__(self, domain_id, algorithm):
        super(BizChatClassifier, self).__init__(domain_id, algorithm)
        self._domain_id = domain_id
        self._identifier = str(domain_id + "casual")
        self._classifier = QuestionClassfier.get_classifier(algorithm)
        model_fname = os.path.join(ConfigData.model_data_path,
                                   self._identifier)
        if not self._classifier.load_model(model_fname):
            log.warning("Model has not been trained.")

    def train(self, label_data):
        biz_chat_data = []
        for data in label_data:
            biz_chat_data.append(LabelData(label=data[0], question=data[1],
                                           treenode=data[2]))
        if self.chat_label_data == []:
            self._load_chat_label_data()

        biz_chat_data += self.chat_label_data
        model_fname = os.path.join(ConfigData.model_data_path,
                                   self._identifier)
        summary = super(BizChatClassifier, self).train(biz_chat_data)
        self._classifier.save_model(model_fname)
        return summary

    def _load_chat_label_data(self):
        chat_file = os.path.join(PROJECT_DIR, "data/casual_talk.txt")
        with open(chat_file, "r") as f:
            for line in f.readlines():
                question = line.rstrip('\n')
                self.chat_label_data.append(LabelData(label="casual_talk",
                                                      question=question,
                                                      treenode=None))
