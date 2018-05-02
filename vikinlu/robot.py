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
    robots = {}

    """"""
    def __init__(self, domain_id, ):
        self.domain_id = domain_id
        log.info("CREATE NLU ROBOT: {0}".format(domain_id))

    def init(self):
        self._nonsense = NonSense.get_nonsense(self.domain_id)
        self._sensitive = Sensitive.get_sensitive(self.domain_id)
        self._slot = SlotRecognizer.get_slot_recognizer(self.domain_id)
        self._intent = IntentRecognizer.get_intent_recognizer(self.domain_id)

    @classmethod
    def get_robot(self, domain_id):
        robot = self.robots.get(domain_id, None)
        if robot:
            return robot
        robot = NLURobot(domain_id)
        robot.init()
        self.robots[domain_id] = robot
        return robot

    def train(self, algorithm):
        log.debug("get_tree_label_data")
        label_data = cms_rpc.get_tree_label_data(self.domain_id)
        log.debug("train with context")
        # save strict model
        for obj in IntentQuestion.objects(domain=self.domain_id):
            obj.delete()
        for td in label_data:
            IntentQuestion(domain=self.domain_id, treenode=td[0], label=td[1], question=td[2]).save()
        # save fuzzy model
        return {
            "code": 0
        }

    def predict(self, dm_robot_id, question):
        # call rpc with dm_robot_id or call with dm robot directly
        dm_robot = dm_robot_id
        context = dm_robot.get_context()
        label, confidence = self._intent_classify(context, question)
        d_slots = {}
        if label and label not in ["sensitive", "casual_talk"]:
            d_slots = self._slot.recognize(question, context["valid_slots"])
            log.debug("SLOTS DETECT to {0}".format(d_slots))
        return {
            "question": question,
            "intent": label,
            "confidence": confidence,
            "slots": d_slots,
        }

    def _intent_classify(self, context, question):
        log.debug("Sensitive detecting.")
        if self._sensitive.detect(question):
            return "sensitive", 1.0
        label, confidence = self._intent.strict_classify(context, question)
        log.info("STRICTLY CLASSIFY to [{0}]".format(label))
        if label:
            return label, confidence
        if self._intent.is_casual_talk(question):
            log.info("BINARY CLASSIFY to [casual_talk]")
            return "casual_talk", 1.0
        if label is None:
            label, confidence = self._intent.fuzzy_classify(context, question)
            log.info("FUZZY CLASSIFY to {0}".format(label))
        return label, confidence
