#!/usr/bin/env python
# encoding: utf-8
from vikinlu.model import IntentQuestion
from vikinlu.util import SYSTEM_DIR
from vikinlu.config import ConfigApps
from vikinlu.util import cms_rpc
import os
import jieba
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
import logging
log = logging.getLogger(__name__)
jieba.dt.tmp_dir = ConfigApps.cache_data_path
jieba.initialize()


class IntentRecognizer(object):
    """"""
    def __init__(self, domain_id):
        self._domain_id = domain_id
        self._feature = None
        self._model = None

    @classmethod
    def get_intent_recognizer(self, domain_id):
        intent = IntentRecognizer(domain_id)
        intent.init_recognizer()
        return intent

    def init_recognizer(self):
        value_words = []
        ret = cms_rpc.get_domain_values(self._domain_id)
        if ret['code'] != 0:
            assert(False)
        for value in ret["values"]:
            if value['name'].startswith('@'):
                continue
            value_words.append(value['name'])
            value_words += value['words']
        value_words = set(value_words)
        #  TODO:  not add word already added in other domain
        for word in value_words:
            jieba.add_word(word, freq=10000)

        stop_words_file = os.path.join(SYSTEM_DIR, "VikiNLP/data/stopwords.txt")
        self.stop_words = self.readfile(stop_words_file).splitlines()

    def strip_stopwords(self, question):
        segs = jieba.cut(question, cut_all=False)
        left_words = []
        for seg in segs:
            if seg not in self.stop_words:
                left_words.append(seg)
        return " ".join(left_words)

    def _load_model(self):
        model_fname = os.path.join(ConfigApps.model_data_path, "{0}_model.txt".format(self._domain_id))
        self._model = self.readbunchobj(model_fname)

        feature_fname = os.path.join(ConfigApps.model_data_path, "{0}_feature.txt".format(self._domain_id))
        feature_set = self.readbunchobj(feature_fname)
        self.features = TfidfVectorizer(
            binary=False,
            decode_error='ignore',
            stop_words=self.stop_words,
            vocabulary=feature_set.vocabulary)

    def strict_classify(self, context, question):
        normalized_question = self.strip_stopwords(question)
        objects = IntentQuestion.objects(domain=self._domain_id, question=normalized_question)
        if not objects:
            log.warning("还未训练")
            return None, 1.0
        if len(objects) > 1:
            for unit in context["agents"]:
                for candicate in objects:
                    tag, intent, id_ = tuple(unit)
                    if candicate.treenode == id_:
                        return candicate.label, 1.0
            log.info("INVALID INTENT!")
            log.debug("candicate intents: {0}".format([obj.label for obj in objects]))
            log.debug("context intents: {0}".format([obj[1] for obj in context["agents"]]))
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
        if self._model is None:
            try:
                self._load_model()
            except Exception as e:
                raise e
                log.error("还未训练")
        #  TODO: 用上下文过滤 #
        x_test = []
        x_test.append(" ".join(jieba.cut(question)))
        x_test = self.features.fit_transform(x_test)

        predicted = self._model.predict(x_test)  # 返回标签
        pre_proba = self._model.predict_proba(x_test)  # 返回概率

        m = predicted[0]
        p = max(pre_proba[0])

        return (m, p)

    def is_casual_talk(self, question):
        return False
