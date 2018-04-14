#!/usr/bin/env python
# encoding: utf-8
from vikinlu.model import IntentQuestion


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

    def strict_classify(self, question):
        try:
            ret = IntentQuestion.objects.get(domain=self._domain_id, question=question)
        except IntentQuestion.DoesNotExisit:
            return None
        return ret.label, 1.0

    def fuzzy_classify(self, question):
        pass

    def is_casual_talk(self, question):
        return False
