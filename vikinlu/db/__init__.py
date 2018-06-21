#!/usr/bin/env python
# encoding: utf-8

from vikinlu.model import IntentQuestion, IntentTreeNode


def clear_intent_question(domain_name):
    IntentQuestion.objects(domain=domain_name).delete()
    IntentTreeNode.objects(domain=domain_name).delete()
