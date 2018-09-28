#!/usr/bin/env python
# encoding: utf-8
import logging

from vikinlu.classifier import BizChatClassifier
from vikinlu.intent import IntentRecognizer
from vikinlu.filters import NonSense, Sensitive
from vikinlu.slot import SlotRecognizer
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

    def reset_robot(self):
        robot = NLURobot(self.domain_id)
        robot.init()
        self.robots[self.domain_id] = robot

    def train(self, algorithm):
        """ Fetch labeld data of project from database, and train questions to
        algorithm model.

        Parameters
        ----------
        algorithm : str, Algorithm name.

        Returns
        -------
        {
            "intents": [

                "label": 意图标识,

                "count": 问题数量,

                "precise": 准去率,

            ]

            "total_prciese": 业务准确率

        }
        """
        #  TODO: label_data check
        label_data = cms_rpc.get_tree_label_data(self.domain_id)
        ret = self._intent.train(self.domain_id, label_data)

        return {
            "code": 0,
            'statics': ret
        }

    def predict(self, context, question):
        """ Return NLU result like intent and slots.

        Parameters
        ----------
        context : dict, Context info from DM.
        question : str, Dialogue text.

        Returns
        -------
        dict.

        """
        # call rpc with dm_robot_id or call with dm robot directly
        log.info("----------------%s------------------" % question)
        intent, confidence = self._intent_classify(context, question)
        d_slots = {}
        if intent and intent not in ["sensitive", "casual_talk"]:
            # d_slots = self._slot.recognize(question, context["valid_slots"])
            # OPTIMIZE: Cache #
            ret = cms_rpc.get_intent_slots_without_value(self.domain_id,
                                                         intent)
            if ret['code'] != 0:
                log.error("调用失败！")
                return {}
            else:
                d_slots = self._slot.recognize(question, ret["slots"])
            log.debug("SLOTS DETECT to {0}".format(d_slots))
        return {
            "question": question,
            "intent": intent,
            "confidence": confidence,
            "slots": d_slots,
        }

    def _intent_classify(self, context, question):
        log.debug("Sensitive detecting.")
        if self._sensitive.detect(question):
            log.info("FILTERED QUESTION")
            return "sensitive", 1.0

        intent, confidence = self._intent.strict_classify(context, question)
        if intent:
            return intent, confidence

        if self._nonsense.detect(question):
            log.info("NONSENSE QUESTION")
            return "nonsense", 1.0

        intent, confidence = self._intent.fuzzy_classify(context, question)
        log.info("FUZZY CLASSIFY to {0} confidence {1}".format(
            intent, confidence))
        return intent, confidence
