#!/usr/bin/env python
# encoding: utf-8

from vikinlp.gate import HttpServiceGate


def test_http_gate():
    http_gate = HttpServiceGate()
    ret = http_gate.get_all_domains("ALL")
    assert(ret['code'] == 0)
    domain_id = None
    for domain in ret['domains']:
        if domain['name'] == 'C':
            domain_id = domain['id']
            break
    assert(domain_id)
    ret = http_gate.get_domain_slots(domain_id)
    assert(ret['code'] == 0)
    ret = http_gate.get_domain_values(domain_id, 0)
    assert(ret['code'] == 0)
    ret = http_gate.get_domain_intents(domain_id)
    assert(ret['code'] == 0)
    intent_id = None
    for intent in ret['intents']:
        if intent['name'] == 'location.query':
            intent_id = intent['id']
    assert(intent_id)
    ret = http_gate.get_intent(intent_id)
    assert(ret['code'] == 0)
    ret = http_gate.get_label_data('C')
    assert(ret['code'] == 0)

