# -*- coding: utf-8 -*-

import re
import jieba.posseg as psg
import jieba


class TimeEntity(object):
    def recognize(self, text):
        """

        Parameters
        ----------
        text :

        Returns
        -------
        [Datetime],

        """
        return self._recognize_with_rules(text)

    @staticmethod
    # 对提取出的拼接日期串进行进一步的处理，进行有效性判断
    def check_time_valid(word):
        m = re.match("\d+$", word)
        if m:
            if len(word) <= 6:
                return None
        word1 = re.sub('[号|日]\d+$', '日', word)
        if word1 != word:
            return TimeEntity.check_time_valid(word1)
        else:
            return word1

    # 时间提取
    def _recognize_with_rules(self, text):
        """
        首先通过Jieba分词将带有时间信息的词进行切分，然后记录连续时间信息的词。
        这里面就用到Jieba词性标注的功能，提取其中“m”（数字）“t”（时间）词性的词
        :param text:
        :return:
        """
        text = self.replace_keywords(text)
        time_res = []
        word = ''
        key_date = ('今天', '明天', '后天')

        for k, v in jieba.posseg.cut(text):
            # 将"分"单独挑出来处理
            if "分" in k and word != "":
                word = word + "分"
                continue

            if k in key_date:
                if word != '':
                    time_res.append(word)
                word = k

            elif word != '':
                if v in ['m', 't']:
                    word = word + k
                elif k != "的":
                    time_res.append(word)
                    word = ''
            # m:数字 t:时间
            elif v in ['m', 't']:
                word = k

        if word != '':
            time_res.append(word)
        result = list(filter(lambda x: x is not None,
                             [self.check_time_valid(w) for w in time_res]))
        return result

    @staticmethod
    def replace_keywords(text):
        text = text.replace(":", "点")
        text = text.replace("明早", "明天早上")
        text = text.replace("明晚", "明天晚上")
        return text
