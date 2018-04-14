#!/usr/bin/env python
# encoding: utf-8
import logging
from vikinlu.util import cms_rpc
from vikinlp.nlp.ner import KeyWordEntity
log = logging.getLogger(__name__)


class SlotRecognizer(object):
    """"""
    def __init__(self):
        self._slots = {}

    def init_slots(self, domain_id):
        ret = cms_rpc.get_domain_slots(domain_id)
        for slot in ret["slots"]:
            d_values = {}
            for value_id in slot["values"].keys():
                ret = cms_rpc.get_value(value_id)
                ret["words"].append(ret["name"])
                d_values[ret["name"]] = ret["words"]
            self._slots[slot["id"]] = {
                "name": slot["name"],
                "values": d_values
            }

    @classmethod
    def get_slot_recognizer(self, domain_id):
        slot = SlotRecognizer()
        slot.init_slots(domain_id)
        return slot

    def recognize(self, question, slot_ids):
        slots = {}
        for slot_id in slot_ids:
            d_slot = self._slots[slot_id]
            for value_name, value_pattern in d_slot["values"].iteritems():
                ret = KeyWordEntity.recognize(question, value_pattern)
                if ret:
                    slots[d_slot["name"]] = value_name
        return slots
