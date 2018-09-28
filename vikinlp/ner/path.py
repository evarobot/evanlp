#!/usr/bin/env python
# encoding: utf-8


class PathEntity(object):
    """ 解决从哪里到哪里的识别。 """
    def __init__(self):
        pass

    @classmethod
    def recognize(self, text, locations, from_verbs, to_verbs):
        """

        Parameters
        ----------
        text : ([str]), 句子分词结果
        locations : (set), 要识别的地点集合
        from_verbs : (([str], [str])), 从哪里来, 分别位于关键词两端。
        to_verbs : (([str], [str])), 到哪里去, 分别位于关键词两端。

        Returns
        -------

        """
        return self._recognize_with_rules(
            text, locations, from_verbs, to_verbs)

    @classmethod
    def _recognize_with_rules(self, text, locations, from_verbs, to_verbs):
        from_loc, to_loc = None, None
        cities = []
        for i, w in enumerate(text):
            if w in locations:
                cities.append((w, i))
        if len(cities) == 2:
            from_loc = cities[0][0]
            to_loc = cities[1][0]
            return from_loc, to_loc
        elif len(cities) == 1:
            # 处理默认出发地
            city, index = cities[0][0], cities[0][1]
            from_loc, to_loc = self._locate(
                text, from_verbs, city, index, True)
            if from_loc:
                return from_loc, to_loc
            from_loc, to_loc = self._locate(
                text, to_verbs, city, index, False)
            return from_loc, to_loc
        else:
            return None, None

    @classmethod
    def _locate(self, text, verbs, city, cindex, isfrom):
        index = cindex + 1
        rindex = cindex
        from_loc, to_loc = None, None
        while rindex > 0:
            rindex -= 1
            for verb in verbs[0]:
                if verb in text[rindex]:
                    if isfrom:
                        from_loc = city
                    else:
                        to_loc = city
                    return from_loc, to_loc
        while index < len(text):
            for verb in verbs[1]:
                if verb in text[index]:
                    if isfrom:
                        from_loc = city
                    else:
                        to_loc = city
                    return from_loc, to_loc
            index += 1
        return None, None
