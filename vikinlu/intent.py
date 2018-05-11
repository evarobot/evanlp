#!/usr/bin/env python
# encoding: utf-8
from vikinlu.model import IntentQuestion
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
            for k in objects:
                print k.label
            print("&"*30)
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
        root_path = os.getcwd()
        space_path = root_path + "/multi_trainspace1.txt"
        train_set = self.readbunchobj(space_path)
        stop_words_file = os.path.abspath(os.path.join(os.getcwd(), "../../VikiNLP/data/stopwords.txt"))
        stpwrdlst = self.readfile(stop_words_file).splitlines()
        count_vec = TfidfVectorizer(
            binary=False,
            decode_error='ignore',
            stop_words=stpwrdlst,
            vocabulary=train_set.vocabulary)
        x_test = []
        x_test.append(" ".join(jieba.cut(question)))
        x_test = count_vec.fit_transform(x_test)
        fr = open(root_path + '/domain_multi_train.txt', 'rb')
        clf = pickle.load(fr)
        predicted = clf.predict(x_test)  # 返回标签
        pre_proba = clf.predict_proba(x_test)  # 返回概率

        fr.close()

        m = predicted[0]
        p = max(pre_proba[0])

        return (m, p)

    def is_casual_talk(self, question):
        return False
