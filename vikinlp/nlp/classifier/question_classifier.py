#!/usr/bin/env python
# encoding: utf-8
import jieba
import os
import logging
import pickle
from sklearn import metrics, preprocessing
from vikinlp.config import ConfigApps
from vikinlp.util import PROJECT_DIR
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cross_validation import train_test_split
from sklearn.linear_model import LogisticRegression

log = logging.getLogger(__name__)
jieba.dt.tmp_dir = ConfigApps.cache_data_path
jieba.initialize()


def readfile(path):
    # fp = open(path, "r", encoding='utf-8')
    fp = open(path, "r")
    content = fp.read()
    fp.close()
    return content


stop_words_file = os.path.join(PROJECT_DIR, "data/stopwords.txt")
stop_words = readfile(stop_words_file).splitlines()


def strip_stopwords(question):
    segs = jieba.cut(question, cut_all=False)
    left_words = []
    for seg in segs:
        if seg not in stop_words:
            left_words.append(seg)
    return " ".join(left_words)


class QuestionClassfier(object):
    """"""
    def __init__(self, identifier):
        self.identifier = identifier
        self._test_size = 0.2

    @classmethod
    def get_classifier(self, identifier, algorithm):
        if algorithm == "logistic":
            return LogisticRegressionClassifier(identifier)

    def readbunchobj(self, path):
        file_obj = open(path, "rb")
        bunch = pickle.load(file_obj)
        file_obj.close()
        return bunch

    def train(self, label_data):
        raise NotImplementedError

    def predict(self, question):
        raise NotImplementedError

    def model_statistics(self, xtest, ytest, model, identifier):
        log.info("*" * 30)
        multi_score = "%.2f" % model.score(xtest, ytest)
        log.info("Model {0} Precise: {1}".format(identifier, multi_score))
        ypredicted = model.predict(xtest)
        matrix = metrics.confusion_matrix(ytest, ypredicted)
        log.info(matrix)
        report = metrics.precision_recall_fscore_support(ytest, ypredicted)
        labels = sorted(set(ytest))
        class_precise = dict(zip(
            labels,map(lambda x: "%.2f" % round(x,2), report[0])))
        return {
            'class_precise': class_precise,
            'total_precise': multi_score
        }


class LogisticRegressionClassifier(QuestionClassfier):
    def __init__(self, identifier):
        super(LogisticRegressionClassifier, self).__init__(identifier)
        try:
            self._load_model()
        except IOError:
            self.model = None
            log.warning("模型还未训练")

    def train(self, label_data):
        data = zip(*label_data)
        y = data[0]
        x = data[1]
        x = [' '.join(jieba.cut(question)) for question in x]

        # summary
        #  TODO: 每个类别20% #
        x_train, x_test, y_train, y_test = train_test_split(
            x, y, test_size=self._test_size)
        feature_data, model_data = self._train(x_train, y_train)
        x_test2 = self.features.transform(x_test)
        summary = self.model_statistics(
            x_test2, y_test, self.model, self.identifier)

        # save model
        feature_data, model_data = self._train(x, y)
        model_fname = os.path.join(ConfigApps.model_data_path,
                                   "{0}_model.txt".format(self.identifier))
        with open(model_fname, "wb") as f:
            pickle.dump(model_data, f)
            log.debug("Save model from {0}".format(model_fname))
        feature_fname = os.path.join(ConfigApps.model_data_path,
                                     "{0}_feature.txt".format(self.identifier))
        with open(feature_fname, "wb") as f:
            pickle.dump(feature_data, f)
            log.debug("Save feature from {0}".format(feature_data))
        return summary

    def _train(self, x_train, y_train):
        stop_words_file = os.path.join(PROJECT_DIR, "data/stopwords.txt")
        stpwrdlst = readfile(stop_words_file).splitlines()
        # tf-idf
        count_vec = TfidfVectorizer(
            binary=False,
            decode_error='ignore',
            stop_words=stpwrdlst)

        x_train = count_vec.fit_transform(x_train)
        # model
        clf = LogisticRegression()
        clf.fit(x_train, y_train)
        self.features = count_vec
        self.model = clf
        return count_vec, clf

    def predict(self, question):
        assert(self.model)
        x_test = " ".join(jieba.cut(question))
        x_test = self.features.transform([x_test])
        label = self.model.predict(x_test)[0]  # 返回标签
        pre_proba = self.model.predict_proba(x_test)  # 返回概率
        confidence = max(pre_proba[0])
        return label, confidence

    def _load_model(self):
        model_fname = os.path.join(ConfigApps.model_data_path,
                                   "{0}_model.txt".format(self.identifier))
        self.model = self.readbunchobj(model_fname)
        log.debug("Load model from {0}".format(model_fname))
        feature_fname = os.path.join(ConfigApps.model_data_path,
                                     "{0}_feature.txt".format(self.identifier))
        self.features = self.readbunchobj(feature_fname)
        log.debug("Load features from {0}".format(model_fname))
