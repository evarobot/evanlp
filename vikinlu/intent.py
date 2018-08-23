#!/usr/bin/env python
# encoding: utf-8
import logging
import jieba

from vikinlu.util import cms_rpc
from vikinlu.classifier import QuestionSearch,\
    FuzzyClassifier, BizChatClassifier
log = logging.getLogger(__name__)


class IntentRecognizer(object):
    """
    Recognize intent from question.

    Attributes
    ----------
    custom_words : set, Custom words added to Tokenizer.
    _biz_chat_classifier : BizChatClassifier, Classify question to business and
        casual_talk.
    _biz_classifier : FuzzyClassifier, Classify
    """
    custom_words = set()

    def __init__(self, domain_id):
        self._domain_id = domain_id
        self._feature = None
        self._strict_classifier = QuestionSearch(domain_id)
        self._biz_classifier = FuzzyClassifier(domain_id, "logistic")
        self._biz_chat_classifier = BizChatClassifier(domain_id, "logistic")

    @classmethod
    def get_intent_recognizer(self, domain_id):
        intent = IntentRecognizer(domain_id)
        intent.init_custom_words()
        return intent

    def init_custom_words(self):
        """
        Read words of value from database.
        """
        value_words = []
        ret = cms_rpc.get_domain_values(self._domain_id)
        if ret['code'] != 0:
            assert(False)
        for value in ret["values"]:
            if value['name'].startswith('@'):
                continue
            value_words.append(value['name'])
            value_words += value['words']
        value_words = set(value_words)
        for word in value_words:
            if word not in self.custom_words:
                self.custom_words.add(word)
                jieba.add_word(word, freq=10000)

    def train(self, domain_id, label_data):
        """ Save Normalized question to database and train quetions to
        algorithm model.

        Parameters
        ----------
        label_data : [(label, question, treenode), ..], Labeld question.

        Returns
        -------
        {
            "biz_statics":  {
                "class_precise": {
                    "label1": "0.3",

                    "label2": "0.2",
                    ...
                },

                'total_precise': "0.38"
            },

            "biz_chat_statics": {
                "class_precise": {
                    "label1": "0.3",

                    "label2": "0.2",
                    ...
                },

                'total_precise': "0.38"
            }
        }

        """
        self._strict_classifier.train(label_data)
        biz_statics = self._biz_classifier.train(label_data)
        biz_chat_statics = self._biz_chat_classifier.train(label_data)
        return {
            'biz_statics': biz_statics,
            'biz_chat_statics': biz_chat_statics
        }

    def strict_classify(self, context, question):
        """ Classify question by database quering, given specific context.

        Parameters
        ----------
        context : dict, Context information from DM, used to filter invisible
                        agents.
        question : str, Dialogue text from user.

        Returns
        -------
        (label, confidence) : (str, float)

        """
        objects, confidence = self._strict_classifier.predict(question)
        return self._get_valid_intent(context, objects), confidence

    def fuzzy_classify(self, context, question):
        """ Classify question by algorithm model, given specific context.

        Parameters
        ----------
        context : dict, Context information from DM, used to filter invisible
                        agents.
        question : str, Dialogue text from user.

        Returns -------
        (label, confidence) : (str, float)

        """
        objects, confidence = self._biz_chat_classifier.predict(question)
        if objects[0].label == 'casual_talk':
            return (objects[0].label, confidence)
        objects, confidence = self._biz_classifier.predict(question)
        label = self._get_valid_intent(context, objects)
        return (label, confidence)

    def _get_valid_intent(self, context, candicates):
        """
        Filter candicate agents by context, ending with one label.
        """
        if not candicates:
            return None
        if len(candicates) > 1:
            for unit in context["agents"]:
                for candicate in candicates:
                    tag, intent, id_ = tuple(unit)
                    if candicate.treenode == id_:
                        return candicate.label
            log.info("NO VISIBLE AGENTS SATISFIED!")
        elif len(candicates) == 1:
            return candicates[0].label
        return None
