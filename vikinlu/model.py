#!/usr/bin/env python
# encoding: utf-8

import mongoengine as db


class IntentQuestion(db.Document):
    domain = db.StringField(required=True)
    treenode = db.StringField(required=True)
    label = db.StringField(required=True)
    question = db.StringField(required=True)

    meta = {
        'indexes': [('treenode', 'question')]
    }
