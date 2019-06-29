#!/usr/bin/env python
# encoding: utf-8
import re


class QuantityEntity(object):
    def __init__(self):
        pass

    @classmethod
    def recognize(self, text):
        """
        Parameters
        ----------
        text : (str/[str]), 如果是str就用正则表达式匹配,
                                否者用精确匹配（默认已经分词）

        Returns
        -------
        [str], quantities entities.

        """
        return self._recognize_with_rules(text)

    @classmethod
    def _recognize_with_rules(self, text):
        cluetext = u'[\d零一两俩二三四五六七八九十\
            百千万亿壹贰叁肆伍陆柒捌玖拾]+'
        m = re.findall(cluetext, text)
        return m
