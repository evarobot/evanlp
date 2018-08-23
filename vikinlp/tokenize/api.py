#!/usr/bin/env python
# encoding: utf-8

from abc import ABCMeta, abstractmethod
from nltk.tokenize import api
from six import add_metaclass


@add_metaclass(ABCMeta)
class TokenizerI(api.TokenizerI):
    """docstring for Api"""
    def __init__(self):
        pass

    @abstractmethod
    def load_userdict(self, fpath):
        """ load keywords file
        """
        pass
