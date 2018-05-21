#!/usr/bin/env python
# encoding: utf-8
from vikinlu.util import cms_rpc
from vikinlu.model import IntentQuestion


class NonSense(object):
    def __init__(self):
        self._words = set([u'你好', u'晚安'])
        self._filter_length = 2

    @classmethod
    def get_nonsense(self, domain_id):
        nonsense = NonSense()
        nonsense.init_words(domain_id)
        return nonsense

    def init_words(self, domain_id):
        for obj in IntentQuestion.objects(domain=domain_id):
            if len(obj.question) <= self._filter_length:
                self._words.add(obj.question)

    def detect(self, question):
        if len(question) <= self._filter_length and question not in self._words:
            return True
        return False


class Sensitive(object):
    def __init__(self):
        self._words = []

    @classmethod
    def get_sensitive(self, domain_id):
        sensitive = Sensitive()
        sensitive.init_words(domain_id)
        return sensitive

    def init_words(self, domain_id):
        rst = cms_rpc.get_filterwords(domain_id)
        self._words = rst['words']

    def detect(self, question):
        for word in self._words:
            if word in question:
                return True
        return False
