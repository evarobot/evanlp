#!/usr/bin/env python
# encoding: utf-8
from vikinlu.model import IntentQuestion
from evecms.models import (
    Domain,
    Slot
)
import pprint

def clear_intent_question():
    IntentQuestion.drop_collection()


def assert_intent_question(domain_id, data):
    intent_questions = IntentQuestion.objects(domain=domain_id)
    label_data = set()
    for db_obj in intent_questions:
        label_data.add((db_obj.treenode, db_obj.label, db_obj.question))
    for tuple_obj in data:
        assert(tuple_obj in label_data)