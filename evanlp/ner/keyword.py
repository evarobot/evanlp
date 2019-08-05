#!/usr/bin/env python
# encoding: utf-8
from flashtext import KeywordProcessor


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
        flag_negative = False
        pos_processor = KeywordProcessor()
        neg_processor = KeywordProcessor()

        for word in cluewords:
            if word.startswith('-'):
                neg_processor.add_keyword(word[1:])
                flag_negative = True
            else:
                pos_processor.add_keyword(word)
        if isinstance(text, list):
            return list(set(text).intersection(set(cluewords)))

        neg = []
        pos = pos_processor.extract_keywords(text)

        if flag_negative:
            neg = neg_processor.extract_keywords(text)

        if not neg:
            # 如果没有遇到黑名单中的词，返回识别到的关键字
            return pos
        return []


if __name__ == '__main__':
    print(KeyWordEntity.recognize("美元和黄金的相关性", ["美元", "黄金"]))
    print(KeyWordEntity.recognize("美元和黄金2003的相关性", ["美元", "黄金"]))


