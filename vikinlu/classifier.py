#!/usr/bin/env python
# encoding: utf-8
import os
import jieba
import pickle
from collections import namedtuple
from sklearn.feature_extraction.text import TfidfVectorizer
from vikinlu.util import SYSTEM_DIR
from vikinlu.config import ConfigApps
from sklearn.cross_validation import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.datasets.base import Bunch
from random import shuffle
import logging
log = logging.getLogger(__name__)
jieba.dt.tmp_dir = ConfigApps.cache_data_path
jieba.initialize()

LabelData = namedtuple('LabelData', 'label, question, treenode')

test_size = 0.2


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


class QuestionClassifier(object):
    """"""
    def __init__(self, identifier):
        self.identifier = identifier

    def train(self, question):
        raise NotImplementedError

    def predict(self, question):
        raise NotImplementedError

    @classmethod
    def get_classifier(cls, domain_id, identifier):
        if identifier == "mongodb":
            return QuestionSearch(domain_id, identifier)
        elif identifier == "logistic":
            return QuestionLogisticRegression(domain_id, identifier)
        elif identifier == "biz_chat":
            return BizChatClassifier(domain_id, identifier)


from vikinlu.model import IntentQuestion, IntentTreeNode
class QuestionSearch(QuestionClassifier):
    def __init__(self, domain_id, identifier):
        super(QuestionSearch, self).__init__(identifier)
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


class QuestionLogisticRegression(QuestionClassifier):
    def __init__(self, domain_id, identifier):
        super(QuestionLogisticRegression, self).__init__(identifier)
        self._model = None
        self.domain_id = domain_id

    def train(self, label_data):
        # save fuzzy model
        shuffle(label_data)
        x = zip(*label_data)[1]
        y = zip(*label_data)[0]
        z = zip(*label_data)[1]
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=test_size)
        stop_words_file = os.path.join(SYSTEM_DIR, "VikiNLP/data/stopwords.txt")
        stpwrdlst = readfile(stop_words_file).splitlines()
        # tf-idf
        count_vec = TfidfVectorizer(
            binary=False,
            decode_error='ignore',
            stop_words=stpwrdlst)
        tfidfspace = Bunch(
            target_names=z,
            labels=y,
            tdm=[],
            vocabulary={}
        )
        x_train = count_vec.fit_transform(x_train)
        x_test = count_vec.transform(x_test)
        tfidfspace.tdm = x_train
        tfidfspace.vocabulary = count_vec.vocabulary_
        feature_fname = os.path.join(ConfigApps.model_data_path,
                                     "{0}_{1}_feature.txt".format(self.domain_id, self.identifier))
        with open(feature_fname, "wb") as f:
            pickle.dump(tfidfspace, f)

        # model
        clf = LogisticRegression()
        clf.fit(x_train, y_train)
        model_fname = os.path.join(ConfigApps.model_data_path,
                                   "{0}_{1}_model.txt".format(self.domain_id, self.identifier))
        with open(model_fname, "wb") as f:
            pickle.dump(clf, f)
        multi_score = clf.score(x_test, y_test)
        log.info("*" * 30)
        log.info("Model {0} Precise: {1}".format(self.identifier, multi_score))
        log.info("*" * 30)

    def predict(self, question):
        if self._model is None:
            try:
                self._load_model()
            except Exception as e:
                raise e
                log.error("还未训练")
        x_test = []
        x_test.append(" ".join(jieba.cut(question)))
        x_test = self.features.fit_transform(x_test)

        predicted = self._model.predict(x_test)  # 返回标签
        objects = IntentTreeNode.objects(domain=self.domain_id, label=predicted[0])
        pre_proba = self._model.predict_proba(x_test)  # 返回概率
        confidence = max(pre_proba[0])
        return objects, confidence

    def _load_model(self):
        model_fname = os.path.join(ConfigApps.model_data_path,
                                   "{0}_{1}_model.txt".format(self.domain_id, self.identifier))
        self._model = self.readbunchobj(model_fname)
        feature_fname = os.path.join(ConfigApps.model_data_path,
                                     "{0}_{1}_feature.txt".format(self.domain_id, self.identifier))
        feature_set = self.readbunchobj(feature_fname)
        self.features = TfidfVectorizer(
            binary=False,
            decode_error='ignore',
            stop_words=stop_words,
            vocabulary=feature_set.vocabulary)

    def readbunchobj(self, path):
        file_obj = open(path, "rb")
        bunch = pickle.load(file_obj)
        file_obj.close()
        return bunch


class BizChatClassifier(QuestionLogisticRegression):
    chat_label_data = []

    def __init__(self, domain_id, identifier="biz_chat"):
        super(BizChatClassifier, self).__init__(domain_id, identifier)

    def train(self, label_data):
        biz_chat_data = []
        for data in label_data:
            biz_chat_data.append(LabelData(label="biz", question=data.question,
                                           treenode=data.treenode))
        if self.chat_label_data == []:
            self._load_chat_label_data()

        biz_chat_data += self.chat_label_data
        super(BizChatClassifier, self).train(biz_chat_data)

    def _load_chat_label_data(self):
        chat_file = os.path.join(SYSTEM_DIR, "VikiNLP/data/casual_talk.txt")
        with open(chat_file, "r") as f:
            for line in f.readlines():
                question = line.rstrip('\n')
                self.chat_label_data.append(LabelData(label="casual_talk",
                                                      question=question,
                                                      treenode=None))
