#!/usr/bin/env python
# encoding: utf-8

import mongoengine as db


class IntentQuestion(db.Document):
    domain = db.StringField(required=True)
    treenode = db.StringField(required=True)
    label = db.StringField(required=True)
    question = db.StringField(required=True)

    meta = {
        'indexes': [('domain', 'question')]
    }

class IntentModel(db.Document):
    domain = db.StringField(required=True)
    algorithm = db.StringField(required=True)
    model = db.StringField(required=True)
    interval = db.StringField(required=True)

    meta = {
        'indexes': [('domain', 'model')]
    }
