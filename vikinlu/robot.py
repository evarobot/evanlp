#!/usr/bin/env python
# encoding: utf-8
import logging
from pprint import pformat

from vikinlu.intent import IntentRecognizer
from vikinlu.filters import NonSense, Sensitive
from vikinlu.slot import SlotRecognizer
from vikinlu.model import IntentQuestion, IntentModel
from vikinlu.util import cms_rpc, SYSTEM_DIR
from vikinlu.config import ConfigApps


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

        print(c)

        for e in c:
            correct_p = []
            for q in c[e]:
                p = self._intent.fuzzy_classify(1, q)
                if (p[0] == e):
                    correct_p.append(p[1])
            c[e] = correct_p

        for e in c:
            if (len(c[e]) != 0):
                print(e, len(c[e]), c[e])

        for e in c:
            n = len(c[e])
            if n != 0:
                c1 = np.array(c[e])
                mean = c1.mean()
                std = c1.std()
                interval = stats.t.interval(0.90, len(c[e]) - 1, mean, std)
                global_pmaxmin[e] = [max(c[e]), min(c[e])]
                global_interval[e] = interval

        print(global_pmaxmin)
        print(global_interval)
        return global_interval

    def train(self, algorithm):
        log.debug("get_tree_label_data")
        label_data = cms_rpc.get_tree_label_data(self.domain_id)
        for k in label_data:
            print k[2]
        # import pdb
        # pdb.set_trace()
        log.debug("train with context")
        # save strict model
        for obj in IntentQuestion.objects(domain=self.domain_id):
            obj.delete()
        for td in label_data:
            IntentQuestion(domain=self.domain_id, treenode=td[0], label=td[1], question=td[2]).save()

        # save fuzzy model
        intent_question = IntentQuestion.objects()
        x = map(lambda x:x.question, intent_question)
        y = map(lambda y:y.treenode, intent_question)
        z = map(lambda z:z.label, intent_question)
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2)
        stop_words_file = os.path.join(SYSTEM_DIR, "VikiNLP/data/stopwords.txt")
        stpwrdlst = self.readfile(stop_words_file).splitlines()
        count_vec = TfidfVectorizer(
            binary=False,
            decode_error='ignore',
            stop_words=stpwrdlst)
        x_train = count_vec.fit_transform(x_train)
        x_test = count_vec.transform(x_test)
        clf = LogisticRegression()
        clf.fit(x_train, y_train)
        import pdb
        pdb.set_trace()
        temp_fname = os.path.join(ConfigApps.temp_data_path, "{0}.txt".format(self.domain_id), "wb")
        with open(temp_fname) as temp_file:
            pickle.dump(clf, temp_file)
        fr = open(temp_fname, 'rb')
        data = fr.read()

        #interval = self.confidence_interval()
        intent_model = IntentModel(domain=self.domain_id, algorithm=algorithm, model=data, interval="")
        intent_model.save()
        multi_score = clf.score(x_test, y_test)
        return {
            "code": 0
        }

    def predict(self, dm_robot, question):
        # call rpc with dm_robot_id or call with dm robot directly
        context = dm_robot.get_context()
        intent, confidence = self._intent_classify(context, question)
        d_slots = {}
        if intent and intent not in ["sensitive", "casual_talk"]:
            d_slots = self._slot.recognize(question, context["valid_slots"])
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
            return "sensitive", 1.0
        intent, confidence = self._intent.strict_classify(context, question)
        log.info("STRICTLY CLASSIFY to [{0}]".format(intent))
        if intent:
            return intent, confidence
        if self._intent.is_casual_talk(question):
            log.info("BINARY CLASSIFY to [casual_talk]")
            return "casual_talk", 1.0
        if intent is None:
            intent, confidence = self._intent.fuzzy_classify(context, question)
            log.info("FUZZY CLASSIFY to {0}".format(intent))
        return intent, confidence




