#!/usr/bin/env python
# encoding: utf-8
import logging

from vikinlu.intent import IntentRecognizer
from vikinlu.filters import NonSense, Sensitive
from vikinlu.slot import SlotRecognizer
from vikinlu.util import cms_rpc, SYSTEM_DIR
from vikinlu.classifier import BizChatClassifier

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cross_validation import train_test_split
from sklearn.linear_model import LogisticRegression

import os
import pickle
from sklearn.datasets.base import Bunch
import numpy as np
from scipy import stats


log = logging.getLogger(__name__)



class NLURobot(object):
    robots = {}

    """"""
    def __init__(self, domain_id, ):
        self.domain_id = domain_id
        self.use_fuzzy = True  # use for test
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

    def readfile(self, path):
        # fp = open(path, "r", encoding='utf-8')
        fp = open(path, "r")
        content = fp.read()
        fp.close()
        return content


    def writebunchobj(self, path, bunchobj):
        file_obj = open(path, "wb")
        pickle.dump(bunchobj, file_obj)
        file_obj.close()

    def confidence_interval(self):
        intent_question = IntentQuestion.objects()
        x = map(lambda x: x.question, intent_question)
        y = map(lambda y: y.treenode, intent_question)
        c = {}
        global_pmaxmin = {}
        global_interval = {}

        for i in range(len(y)):
            l = c.get(y[i])
            if l == None:
                c[y[i]] = []
                c[y[i]].append(x[i])
            else:
                c[y[i]].append(x[i])

        for e in c:
            correct_p = []
            for q in c[e]:
                p = self._intent.fuzzy_classify(1, q)
                if (p[0] == e):
                    correct_p.append(p[1])
            c[e] = correct_p


        for e in c:
            n = len(c[e])
            if n != 0:
                c1 = np.array(c[e])
                mean = c1.mean()
                std = c1.std()
                interval = stats.t.interval(0.90, len(c[e]) - 1, mean, std)
                global_pmaxmin[e] = [max(c[e]), min(c[e])]
                global_interval[e] = interval

        return global_interval

    def train(self, algorithm):
        log.debug("get_tree_label_data")
        label_data = cms_rpc.get_tree_label_data(self.domain_id)
        log.debug("train with context")
        label_question = {}
        label_question_count = {}
        for record in label_data:
            label_question.setdefault(record.label, record.question)
            count = label_question_count.get(record.label, 0)
            count += 1
            label_question_count[record.label] = count
        ret = self._intent.train(self.domain_id, label_data)
        for label, value in ret['biz_statics']['class_precise'].iteritems():
            ret['biz_statics']['class_precise'][label] = [value,
                                                          label_question[label],
                                                          label_question_count[label]]
        ret['biz_chat_statics']['class_precise']['biz'] = [ret['biz_chat_statics']['class_precise']['biz'], u'业务', len(label_data)]
        ret['biz_chat_statics']['class_precise']['casual_talk'] = [ret['biz_chat_statics']['class_precise']['casual_talk'], u'闲聊', len(BizChatClassifier.chat_label_data)]

        return {
            "code": 0,
            'statics': ret
        }

    def predict(self, dm_robot, question):
        # call rpc with dm_robot_id or call with dm robot directly
        log.info("----------------%s------------------" % question)
        context = dm_robot.get_context()
        intent, confidence = self._intent_classify(context, question)
        d_slots = {}
        if intent and intent not in ["sensitive", "casual_talk"]:
            # d_slots = self._slot.recognize(question, context["valid_slots"])
            ret = cms_rpc.get_intent_slots_without_value(self.domain_id, intent)
            if ret['code'] != 0:
                log.error("调用失败！")
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
        log.info("STRICTLY CLASSIFY to [{0}]".format(intent))
        if intent:
            return intent, confidence
        if self._nonsense.detect(question):
            log.info("NONSENSE QUESTION")
            return "nonsense", 1.0
        if self._intent.is_casual_talk(question):
            log.info("BINARY CLASSIFY to [casual_talk]")
            return "casual_talk", 1.0
        if self.use_fuzzy:
            intent, confidence = self._intent.fuzzy_classify(context, question)
            log.info("FUZZY CLASSIFY to {0} confidence {1}".format(intent, confidence))
        return intent, confidence




