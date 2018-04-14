#!/usr/bin/env python
# encoding: utf-8
import logging
from pprint import pformat

from vikinlu.intent import IntentRecognizer
from vikinlu.filters import NonSense, Sensitive
from vikinlu.slot import SlotRecognizer
from vikinlu.model import IntentQuestion
from vikinlu.util import dm_rpc


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
        label_data = dm_rpc.get_label_data(self.domain_id)
        self._train_without_context(self.domain_id, algorithm, label_data)
        # self._train_with_context()

    def _load_biztree(self):
        pass

    def _train_without_context(self, domain_id, algorithm, label_data):
        # save strict model
        for label, questions in label_data.iteritems():
            for q in questions:
                IntentQuestion(domain=domain_id, label=label, question=q).save()
        # save fuzzy model

    def _train_with_context(self, biztree):
        # save strict model
        # save fuzzy model
        pass

    def predict(self, question):
        if self._sensitive.detect(question):
            return {
                "question": question,
                "intent": "sensitive",
                "confidence": 1.0,
                "slots": {}
            }
        if self._in_context():
            log.debug("上下文识别")
            ret = self._do_context_nlu(question)
        else:
            log.debug("非上下文识别")
            ret = self._do_none_context_nlu(question)
        return ret

    def _in_context(self):
        return False

    def _do_context_nlu(self, question):
        pass

    def _get_sub_slots(self, focus_node):
        pass

    def _do_none_context_nlu(self, question):
        label, confidence = self._intent.strict_classify(question)
        if not label and self._intent.is_casual_talk(question):
            return {
                "question": question,
                "intent": "casual_talk",
                "confidence": 1.0,
                "slots": {}
            }
        if not label:
            label, confidence = self._intent.fuzzy_classify(question)
        slot_ids = self._get_sub_slots()
        d_slots = self._slot.recognize(question, slot_ids)
        return {
            "question": question,
            "intent": label,
            "confidence": confidence,
            "slots": d_slots,
        }
