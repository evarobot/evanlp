#!/usr/bin/env python
# encoding: utf-8

import mongoengine as db


def connect_db(dbname, host, port):
    """ 连接数据库

    Parameters
    ----------
    dmname : 数据库名称
    host : 数据库IP
    port : 数据库端口

    Returns
    -------
    None

    """
    db.connect(db=dbname, host=host, port=port)


class IntentQuestion(db.Document):
    domain = db.StringField(required=True)
    treenode = db.IntField(required=True)
    label = db.StringField(required=True)
    question = db.StringField(required=True)

    meta = {
        'indexes': [('domain', 'question')]
    }


class IntentTreeNode(db.Document):
    domain = db.StringField(required=True)
    treenode = db.IntField(required=True)
    label = db.StringField(required=True,
                           unique_with=["domain", "treenode", "label"])

    meta = {
        'indexes': [('domain', 'label')]
    }


def clear_intent_question(domain_name):
    IntentQuestion.objects(domain=domain_name).delete()
    IntentTreeNode.objects(domain=domain_name).delete()
