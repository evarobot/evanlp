#!/usr/bin/env python
# encoding: utf-8
from vikinlu.model import IntentQuestion


def clear_intent_question():
    IntentQuestion.drop_collection()


def assert_intent_question(domain_id, data):
    intent_questions = IntentQuestion.objects(domain=domain_id)
    label_data = {}
    for intent_question in intent_questions:
        questions = label_data.setdefault(intent_question.label, [])
        questions.append(intent_question.question)
    for label, questions in label_data.iteritems():
        assert(set(data[label]) == set(questions))
