#!/usr/bin/env python
# encoding: utf-8
import logging
from vikinlu.util import cms_gate
from vikinlp.ner import KeyWordEntity
log = logging.getLogger(__name__)


class SlotRecognizer(object):
    """
    Detect slots from dialogue text.

    Attributes
    ----------
    _slots : dict, Slots and related value, like:
            {
                "slot_name1": {
                    "value_name1": ["word1", "word2", ..],

                    "value_name2": ["word1", "word2", ..]
                },

                "slot_name2": {
                    "value_name1": ["word1", "word2", ..],

                    "value_name2": ["word1", "word2", ..]
                }
            }
    """
    def __init__(self):
        self._slots = {}

    def init_slots(self, domain_id):
        """ Initialize slots and values from data module.

        Parameters
        ----------
        domain_id : str, Project id.

        """
        ret = cms_gate.get_domain_slots(domain_id)
        if ret['code'] != 0:
            raise RuntimeError("Failed to invoke `get_domain_slots`.")
        for slot in ret["slots"]:
            d_values = {}
            ret = cms_gate.get_slot_values_for_nlu(slot['id'])
            if ret['code'] != 0:
                raise RuntimeError("Failed to invoke 'get_slot_values_for_nlu'")
            for value in ret['data']['values']:
                value["words"].append(value["name"])
                d_values[value["name"]] = value["words"]
            self._slots[slot["name"]] = d_values

    @classmethod
    def get_slot_recognizer(self, domain_id):
        slot = SlotRecognizer()
        slot.init_slots(domain_id)
        return slot

    def recognize(self, question, slot_names):
        """

        Parameters
        ----------
        question : str, Dialogue text.
        slot_names : [str], Name of target slots to detect.

        Returns
        -------
        dict.

        """
        slots = {}
        for slot_name in slot_names:
            value = self._slots[slot_name]
            for value_name, value_pattern in value.iteritems():
                ret = KeyWordEntity.recognize(question, value_pattern)
                if ret:
                    slots[slot_name] = value_name
        return slots
