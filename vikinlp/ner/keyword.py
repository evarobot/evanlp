#!/usr/bin/env python
# encoding: utf-8
import re


class KeyWordEntity(object):
    def __init__(self):
        pass

    @classmethod
    def recognize(self, text, cluewords):
        """

        Parameters
        ----------
        text : str/[str]: 如果是str就用正则表达式匹配,
                            否者用精确匹配（默认已经分词）
        cluewords : (str/[str]): 关键词列表或者正则表达式

        Returns
        -------
        [str], 匹配的关键词数组

        """
        return self._recognize_with_rules(text, cluewords)

    @classmethod
    def _recognize_with_rules(self, text, cluewords):
        postive_words = []
        negative_words = []
        for word in cluewords:
            if word.startswith('-'):
                negative_words.append(word[1:])
            else:
                postive_words.append(word)
        if isinstance(text, list):
            return list(set(text).intersection(set(cluewords)))
        if isinstance(cluewords, list):
            postive_words = u'|'.join(postive_words)
            negative_words = u'|'.join(negative_words)
        neg = []
        pos = re.findall(postive_words, text)
        if negative_words:
            neg = re.findall(negative_words, text)
        if not neg:
            return pos
        return []
