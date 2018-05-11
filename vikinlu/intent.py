#!/usr/bin/env python
# encoding: utf-8
import logging
from vikinlu.model import IntentQuestion
from evecms.models import *
log = logging.getLogger(__name__)


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
        log.debug("candicate intents: {0}".format([obj.label for obj in objects]))
        log.debug("context intents: {0}".format([obj[1] for obj in context["agents"]]))
        if len(objects) > 1:
            for unit in context["agents"]:
                for candicate in objects:
                    tag, intent, id_ = tuple(unit)
                    if candicate.label == intent and question == "保湿":
                        log.info("context_treenode%s, train_treenode: %s" % (id_, candicate.treenode))
                        node = TreeNode.objects.with_id(id_)
                        log.info(node.tag)
                    if candicate.treenode == id_:
                        return candicate.label, 1.0
        elif len(objects) == 1:
            return objects[0].label, 1.0
        return None, 1.0

    def fuzzy_classify(self, context, question):
        return None, 1.0

    def is_casual_talk(self, question):
        return False
