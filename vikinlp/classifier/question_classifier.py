#!/usr/bin/env python
# encoding: utf-8
import jieba
import os
import logging
from sklearn import metrics
from vikinlp.config import ConfigApps
from vikinlp import io
from vikinlp.util import PROJECT_DIR
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cross_validation import train_test_split
from sklearn.linear_model import LogisticRegression

log = logging.getLogger(__name__)
jieba.dt.tmp_dir = ConfigApps.cache_data_path
jieba.initialize()


#  TODO: remove readfile #
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
    def __init__(self):
        self._test_size = 0.2

    @classmethod
    def get_classifier(self, algorithm):
        if algorithm == "logistic":
            return LogisticRegressionClassifier()

    def train(self, label_data):
        raise NotImplementedError

    def predict(self, question):
        raise NotImplementedError

    def model_statistics(self, xtest, ytest, model):
        log.info("*" * 30)
        multi_score = "%.2f" % model.score(xtest, ytest)
        log.info("Model Precise: {0}".format(multi_score))
        ypredicted = model.predict(xtest)
        matrix = metrics.confusion_matrix(ytest, ypredicted)
        log.info(matrix)
        report = metrics.precision_recall_fscore_support(ytest, ypredicted)
        labels = sorted(set(ytest))
        class_precise = dict(zip(
            labels, map(lambda x: "%.2f" % round(x, 2), report[0])))
        return {
            'class_precise': class_precise,
            'total_precise': multi_score
        }


class LogisticRegressionClassifier(QuestionClassfier):
    def __init__(self):
        super(LogisticRegressionClassifier, self).__init__()
        self.model = None

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
        summary = self.model_statistics(x_test2, y_test, self.model)

        # save model
        self.feature, self.model = self._train(x, y)
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
        assert(self.model and "model not trained")
        x_test = " ".join(jieba.cut(question))
        x_test = self.features.transform([x_test])
        label = self.model.predict(x_test)[0]  # 返回标签
        pre_proba = self.model.predict_proba(x_test)  # 返回概率
        confidence = max(pre_proba[0])
        return label, confidence

    def save_model(self, fname):
        try:
            model_fname = fname + "_model.txt"
            io.save(self.model, model_fname)
            log.debug("Save model to {0}".format(model_fname))

            feature_fname = fname + "_feature.txt"
            io.save(self.feature, feature_fname)
            log.debug("Save feature to {0}".format(feature_fname))
        except Exception as e:
            log.error(e)
            return False
        return True

    def load_model(self, fname):
        try:
            model_fname = fname + "_model.txt"
            self.model = io.load(model_fname)
            log.debug("Load model from {0}".format(model_fname))

            feature_fname = fname + "_feature.txt"
            self.features = io.load(feature_fname)
            log.debug("Load features from {0}".format(feature_fname))
        except Exception as e:
            log.error(e)
            return False
        return True
