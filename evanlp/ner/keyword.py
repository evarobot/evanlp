#!/usr/bin/env python
# encoding: utf-8
#from flashtext import KeywordProcessor
import re


class KeyWordEntity(object):
    def __init__(self):
        pass

    @classmethod
    def recognize(self, text, cluewords, case_sensitive=False):
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
        # flag_negative = False
        # pos_processor = KeywordProcessor()
        # neg_processor = KeywordProcessor()
        #
        # for word in cluewords:
        #     if word.startswith('-'):
        #         neg_processor.add_keyword(word[1:])
        #         flag_negative = True
        #     else:
        #         print(word)
        #         pos_processor.add_keyword(word)
        # if isinstance(text, list):
        #     return list(set(text).intersection(set(cluewords)))
        #
        # neg = []
        # pos = pos_processor.extract_keywords(text)
        #
        # if flag_negative:
        #     neg = neg_processor.extract_keywords(text)
        #
        # if not neg:
        #     # 如果没有遇到黑名单中的词，返回识别到的关键字
        #     return pos
        # return []

        # if isinstance(cluewords, str):
        #     pattern = cluewords
        # else:
        #     pattern = '|'.join(cluewords)
        # r = re.compile(pattern, flags=re.I | re.X)
        # return r.findall(text)

        if isinstance(cluewords, str):
            cluewords = [cluewords]
        result = []
        if not case_sensitive:
            text = text.upper()
        for word in cluewords:
            if not case_sensitive:
                if word.upper() in text:
                    result.append(word)
            else:
                if word in text:
                    result.append(word)
        return result


if __name__ == '__main__':
    print(KeyWordEntity.recognize("美元和黄金和美元的相关性", ["美元", "黄金"]))
    print(KeyWordEntity.recognize("美元和黄金的相关性", "美元"))
    print(KeyWordEntity.recognize("美元和黄金的相关性", "特别"))
    print(KeyWordEntity.recognize("show me interest rate", "interest rate"))

