#!/usr/bin/env python
# encoding: utf-8
from vikinlu.model import IntentQuestion, IntentModel
from vikinlu.util import SYSTEM_DIR
from vikinlu.config import ConfigApps
import os
import jieba
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer

class IntentRecognizer(object):
    """"""
    def __init__(self, domain_id):
        self._domain_id = domain_id

    @classmethod
    def get_intent_recognizer(self, domain_id):
        intent = IntentRecognizer(domain_id)
        intent._load_model()
        return intent

    def _load_model(self):
        pass

    def strict_classify(self, context, question):
        try:
            objects = IntentQuestion.objects(domain=self._domain_id, question=question)
        except IntentQuestion.DoesNotExist:
            return None, 1.0
        if len(objects) > 1:
            for unit in context["agents"]:
                for candicate in objects:
                    tag, intent, id_ = tuple(unit)
                    if candicate.treenode == id_:
                        return candicate.label, 1.0
        elif len(objects) == 1:
            return objects[0].label, 1.0
        return None, 1.0

    def readfile(self, path):
        # fp = open(path, "r", encoding='utf-8')
        fp = open(path, "r")
        content = fp.read()
        fp.close()
        return content

    def readbunchobj(self, path):
        file_obj = open(path, "rb")
        bunch = pickle.load(file_obj)
        file_obj.close()
        return bunch

    def fuzzy_classify(self, context, question):
        feature_fname = os.path.join(ConfigApps.temp_data_path, "{0}_feature.txt".format(self._domain_id))
        train_set = self.readbunchobj(feature_fname)
        stop_words_file = os.path.join(SYSTEM_DIR, "VikiNLP/data/stopwords.txt")
        stpwrdlst = self.readfile(stop_words_file).splitlines()
        count_vec = TfidfVectorizer(
            binary=False,
            decode_error='ignore',
            stop_words=stpwrdlst,
            vocabulary=train_set.vocabulary)
        x_test = []
        x_test.append(" ".join(jieba.cut(question)))
        x_test = count_vec.fit_transform(x_test)

        model_fname = os.path.join(ConfigApps.temp_data_path, "{0}_model.txt".format(self._domain_id))
        clf = self.readbunchobj(model_fname)
        predicted = clf.predict(x_test)  # 返回标签
        pre_proba = clf.predict_proba(x_test)  # 返回概率

        m = predicted[0]
        p = max(pre_proba[0])

        return (m, p)

    def is_casual_talk(self, question):
        return False
