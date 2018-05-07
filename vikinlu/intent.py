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

    def strict_classify(self, context, question):
        try:
            objects = IntentQuestion.objects(domain=self._domain_id, question=question)
        except IntentQuestion.DoesNotExist:
            return None, 1.0
        if len(objects) > 1:
            for candicate in objects:
                for unit in context["agents"]:
                    tag, intent, id_ = tuple(unit)
                    if candicate.treenode == id_:
                        return candicate.label, 1.0
        elif len(objects) == 1:
            return objects[0].label, 1.0
        return None, 1.0

    def fuzzy_classify(self, context, question):
        return None, 1.0

    def is_casual_talk(self, question):
        return False
