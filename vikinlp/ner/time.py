#!/usr/bin/env python
# encoding: utf-8
import datetime
import re


class TimeEntity(object):
    """ 时间实体识别。"""
    time_units = [u'年', u'月', u'月份', u'日', u'号', u'点',
                  u'分', u'秒', u'.', u':']
    time_words = [u'早上', u'早晨', u'凌晨', u'上午', u'中午',
                  u'下午', u'晚上', u'傍晚', u'明天', u'后天', u'半']
    cn_num_map = {
        u'零': u'0',
        u'一': u'1',
        u'二': u'2',
        u'两': u'2',
        u'三': u'3',
        u'四': u'4',
        u'五': u'5',
        u'六': u'6',
        u'七': u'7',
        u'八': u'8',
        u'九': u'9'
    }
    cn_num_unit = {
        u'十': 10,
        u'百': 100,
        u'千': 1000,
        u'万': 10000,
    }
    numbers = cn_num_map.values() + cn_num_map.keys() + [u'十']

    @classmethod
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


    @classmethod
    def cn2dig(self, src, unit):
        if src == "":
            return None
        m = re.match("\d+", src)
        if m:
            return m.group(0)
        if unit == u'年':
            return ''.join(map(lambda x: str(self.cn_num_map[x]), list(src)))
        rsl = 0
        unit = 1
        for item in src[::-1]:
            if item in self.cn_num_unit.keys():
                unit = self.cn_num_unit[item]
            elif item in self.cn_num_map.keys():
                num = int(self.cn_num_map[item])
                rsl += num * unit
            else:
                return None
        if rsl < unit:
            rsl += unit
        return str(rsl)

    @classmethod
    def parse_datetime(self, msg):
        if msg is None or len(msg) == 0:
            return None
        # 一个括号表示一个group, 全是带？号的，所以无法匹配子串。
        m = re.search(ur"([0-9零一二两三四五六七八九十]+年)?\
                      ([0-9零一二两三四五六七八九十]+月)?\
                      ([0-9一二两三四五六七八九十]+[号日])?\
                      ([上下午晚早今天明天后天]+)?\
                      ([0-9零一二两三四五六七八九十百]+[点:\.时])?\
                      (半)?([0-9零一二三四五六七八九十百]+分?)?\
                      ([0-9零一二三四五六七八九十百]+秒)?", msg)

        if m.group(0) is not None:
            res = {
                "year": m.group(1),
                "month": m.group(2),
                "day": m.group(3),
                "hour": m.group(5) if m.group(5) is not None else '00',
                "minute": m.group(7) if m.group(7) is not None else '00',
                "second": m.group(8) if m.group(8) is not None else '00',
            }
            params = {}
            for name in res:
                if res[name] is not None and len(res[name]) != 0:
                    params[name] = int(
                        self.cn2dig(res[name][:-1], res[name][-1]))
            target_date = datetime.datetime.today().replace(**params)
            if m.group(6):
                target_date = target_date.replace(minute=30)
            is_pm = m.group(4)
            if is_pm is not None:
                if is_pm.endswith(u'下午') or is_pm.endswith(u'晚上'):
                    hour = target_date.time().hour
                    if hour < 12:
                        target_date = target_date.replace(hour=hour + 12)
                if is_pm.startswith(u'明天'):
                    day = target_date.day
                    target_date = target_date.replace(day=day + 1)
                if is_pm.startswith(u'后天'):
                    day = target_date.day
                    target_date = target_date.replace(day=day + 2)
            target_time = None
            if m.group(5):
                target_time = target_date.time()
            return target_date.date(), target_time
        else:
            return None, None

    @classmethod
    def _recognize_with_rules(self, text):
        t_words = []
        times = []
        possible_unit = ''
        half_hour = False
        rwords = list(reversed(text))
        length = len(rwords)
        for i, w in enumerate(rwords):
            if w.startswith(u'点半') and len(t_words) == 0:
                w = u'点'
                half_hour = True
            if w.startswith(u'半') and len(t_words) == 0 and\
                    u'点' in rwords[min(length, i + 1)]:
                half_hour = True
            for unit in self.time_units:
                if unit in w:
                    # 可能是时间词, 几点，点
                    v = map(lambda x: x in self.numbers, w[:-1])
                    if v and all(v):
                        # 是时间了, 3点
                        t_words.append(w)
                    elif len(t_words) > 0 and len(w) > 1:
                        # sesssion end, 几点
                        stime = ''.join(reversed(t_words))
                        if half_hour:
                            stime += u'半'
                            half_hour = False
                        if stime:
                            times.append(stime)
                        t_words = []
                    elif len(w) == 1 or w == u'月份':
                        # 点
                        possible_unit = w
                    break
            else:
                if possible_unit is not '':
                    # 前有点
                    v = map(lambda x: x in self.numbers, list(w))
                    if v and all(v):
                        # 找到和possible_unit匹配的数字。
                        t_words.append(w + possible_unit)
                    else:
                        # sesssion end
                        stime = ''.join(reversed(t_words))
                        if half_hour:
                            stime += u'半'
                            half_hour = False
                        if stime:
                            times.append(stime)
                        t_words = []
                    possible_unit = ''
                else:
                    if w in self.time_words:
                        t_words.append(w)
                    elif len(t_words) > 0:
                        # sesssion end
                        stime = ''.join(reversed(t_words))
                        if half_hour:
                            stime += u'半'
                            half_hour = False
                        if stime:
                            times.append(stime)
                        t_words = []
        ret = []
        if times:
            ret = map(lambda x: self.parse_datetime(x), times)
        return ret
