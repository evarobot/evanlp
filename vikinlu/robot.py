#!/usr/bin/env python
# encoding: utf-8
import logging
from pprint import pformat

from vikinlu.intent import IntentRecognizer
from vikinlu.filters import NonSense, Sensitive
from vikinlu.slot import SlotRecognizer
from vikinlu.model import IntentQuestion
from vikinlu.util import cms_rpc


log = logging.getLogger(__name__)


class NLURobot(object):
    """"""
    def __init__(self, domain_id):
        self.domain_id = domain_id

    def init(self):
        self._nonsense = NonSense.get_nonsense(self.domain_id)
        self._sensitive = Sensitive.get_sensitive(self.domain_id)
        self._slot = SlotRecognizer.get_slot_recognizer(self.domain_id)
        self._intent = IntentRecognizer.get_intent_recognizer(self.domain_id)
        self._biztree = self._load_biztree()

    @classmethod
    def get_robot(self, domain_id):
        robot = NLURobot(domain_id)
        robot.init()
        return robot

    def train(self, algorithm):
        log.debug("get_tree_label_data")
        label_data = cms_rpc.get_tree_label_data(self.domain_id)
        log.debug("train with context")
        # save strict model
        for td in label_data:
            IntentQuestion(domain=self.domain_id, treenode=td[0], label=td[1], question=td[2]).save()
        # save fuzzy model

    def _load_biztree(self):
        pass


    def predict(self, question):
        log.debug("Sensitive detecting.")
        if self._sensitive.detect(question):
            return {
                "question": question,
                "intent": "sensitive",
                "confidence": 1.0,
                "slots": {}
            }
        log.debug("Do strictly classify.")
        label, confidence = self._intent.strict_classify(question)

        log.debug("Do casual vs. none casual classify.")
        if not label and self._intent.is_casual_talk(question):
            return {
                "question": question,
                "intent": "casual_talk",
                "confidence": 1.0,
                "slots": {}
            }

        if label is None:
            label, confidence = self._intent.fuzzy_classify(question)

        log.debug("Do slot recognize")
        slot_names = self._get_sub_slots()
        d_slots = self._slot.recognize(question, slot_names)
        return {
            "question": question,
            "intent": label,
            "confidence": confidence,
            "slots": d_slots,
        }


    def _get_sub_slots(self, focus_node):
        pass
