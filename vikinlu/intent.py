#!/usr/bin/env python
# encoding: utf-8
from vikinlu.util import cms_rpc
from vikinlu.classifier import QuestionSearch, FuzzyClassifier, BizChatClassifier
import logging
import jieba
log = logging.getLogger(__name__)


class IntentRecognizer(object):
    """"""
    jieba_words = set()

    def __init__(self, domain_id):
        self._domain_id = domain_id
        self._feature = None
        self._strict_classifier = QuestionSearch(domain_id)
        self._biz_classifier = FuzzyClassifier(domain_id, "logistic")
        self._biz_chat_classifier = BizChatClassifier(domain_id, "logistic")

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
        for word in value_words:
            if word not in self.jieba_words:
                self.jieba_words.add(word)
                jieba.add_word(word, freq=10000)

    def train(self, domain_id, label_data):
        self._strict_classifier.train(label_data)
        self._biz_classifier.train(label_data)
        self._biz_chat_classifier.train(label_data)

    def strict_classify(self, context, question):
        objects, confidence = self._strict_classifier.predict(question)
        return self._get_valid_intent(context, objects), confidence

    def fuzzy_classify(self, context, question):
        objects, confidence = self._biz_chat_classifier.predict(question)
        if objects[0].label == 'casual_talk':
            return (objects[0].label, confidence)
        objects, confidence = self._biz_classifier.predict(question)
        label = self._get_valid_intent(context, objects)
        return (label, confidence)

    def _get_valid_intent(self, context, candicates):
        if not candicates:
            return None
        if len(candicates) > 1:
            for unit in context["agents"]:
                for candicate in candicates:
                    tag, intent, id_ = tuple(unit)
                    if candicate.treenode == id_:
                        return candicate.label
            log.info("INVALID INTENT!")
            log.debug("candicate intents: {0}".format([obj.label for obj in candicates]))
            log.debug("context intents: {0}".format([obj[1] for obj in context["agents"]]))
        elif len(candicates) == 1:
            return candicates[0].label
        return None

    def is_casual_talk(self, question):
        return False
