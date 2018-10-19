import re
from datetime import datetime,timedelta

import jieba.posseg as psg
import jieba


class CustomTimeEntity():

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
    def get_now():
        return datetime.today()

    def __init__(self):
        jieba.add_word("分", freq=99999999, tag="m")
        jieba.add_word("今天", freq=99999999, tag="m")
        jieba.add_word("下午", freq=99999999, tag="m")
        jieba.add_word("点", freq=99999999, tag="m")
        jieba.add_word("分钟", freq=99999999, tag="m")
        jieba.add_word("秒钟", freq=99999999, tag="m")
        jieba.add_word("小时", freq=99999999, tag="m")
        self.UTIL_CN_NUM = {
            '零': 0, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4,
            '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
            '0': 0, '1': 1, '2': 2, '3': 3, '4': 4,
            '5': 5, '6': 6, '7': 7, '8': 8, '9': 9
        }
        self.UTIL_CN_UNIT = {'十': 10, '百': 100, '千': 1000, '万': 10000}

    def cn2dig(self, src):
        if src == "":
            return None
        m = re.match("\d+", src)
        if m:
            return int(m.group(0))
        rsl = 0
        unit = 1
        for item in src[::-1]:
            if item in self.UTIL_CN_UNIT.keys():
                unit = self.UTIL_CN_UNIT[item]
            elif item in self.UTIL_CN_NUM.keys():
                num = self.UTIL_CN_NUM[item]
                rsl += num * unit
            else:
                return None
        if rsl < unit:
            rsl += unit
        return rsl

    def year2dig(self, year):
        res = ''
        for item in year:
            if item in self.UTIL_CN_NUM.keys():
                res = res + str(self.UTIL_CN_NUM[item])
            else:
                res = res + item
        m = re.match("\d+", res)
        if m:
            if len(m.group(0)) == 2:
                return int(self.get_now().year/100)*100 + int(m.group(0))
            else:
                return int(m.group(0))
        else:
            return None

    def parse_datetime(self, msg):
        """
        对已经规范化后的文本进行标准datetime变量生成,已经不属于NER的范畴了，
        而是针对领域问题
        :param msg: e.g. “2018年10月11日早晨6点30”， “00点01分”，“2018年10月11日8点”
        :return:
        """
        if msg is None or len(msg) == 0:
            return None

        m = re.match(
            r"([0-9零一二两三四五六七八九十]+年)?([0-9一二两三四五六七八九十]+月)?"
            r"([0-9一二两三四五六七八九十]+[号日])?([上中下午晚早晨]+)?"
            r"([0-9零一二两三四五六七八九十百]+[点:时])?"
            r"([0-9零一二三四五六七八九十百][0-9零一二三四五六七八九十百]+分?)?"
            r"([0-9零一二三四五六七八九十百]+秒)?",
            msg)
        # print('m.group:',m.group(0),m.group(1),m.group(2),m.group(3),
        #       m.group(4),m.group(5),m.group(6),m.group(7))
        if m.group(0) is not None:
            res = {
                "year": m.group(1),
                "month": m.group(2),
                "day": m.group(3),
                "noon": m.group(4),  # 上中下午晚早
                "hour": m.group(5) if m.group(5) is not None else '00',
                "minute": m.group(6) if m.group(6) is not None else '00',
                "second": m.group(7) if m.group(7) is not None else '00',
            }

            if res["minute"] is not None and res["minute"][-1] != "分":
                res["minute"] += "分"
            if (res["noon"] == "下午" or res["noon"] == "晚") and\
                    int(self.cn2dig(res["hour"][:-1])) <= 12:
                res["hour"] = str(int(self.cn2dig(res["hour"][:-1])) + 12)\
                              + res["hour"][-1]
            params = {}
            for name in res:
                if res[name] is not None and len(res[name]) != 0:
                    if name == 'year':
                        tmp = self.year2dig(res[name][:-1])
                    else:
                        tmp = self.cn2dig(res[name][:-1])
                    if tmp is not None:
                        params[name] = int(tmp)
            target_date = self.get_now().replace(**params)
            is_pm = m.group(4)
            if is_pm is not None:
                if is_pm == u'下午' or is_pm == u'晚上' or is_pm == '中午':
                    hour = target_date.time().hour
                    if hour < 12:
                        target_date = target_date.replace(hour=hour + 12)
            return target_date.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return None

    def _recognize_with_rules(self, lst_date):
        """
        首先通过Jieba分词将带有时间信息的词进行切分，然后记录连续时间信息的词。
        这里面就用到Jieba词性标注的功能，提取其中“m”（数字）“t”（时间）词性的词
        :param lst_date:
        :return:
        """

        lst_result = []
        for text in lst_date:

            time_res = []
            word = ''
            key_date = {'今天': 0, '明天': 1, '后天': 2}

            for k, v in jieba.posseg.cut(text):
                # 将"分"单独挑出来处理，因为分词有时候会分错
                if "分" in k and word != "":
                    word = word + "分"
                    continue

                # 解决业务场景现象："今天"、"明天"这样的带有复合语义的词
                if k in key_date:
                    if word != '':
                        time_res.append(word)
                    # 日期的转换，timedelta提取任意延迟天数的信息
                    word = (self.get_now() +
                            timedelta(days=key_date.get(k, 0)))\
                        .strftime('%Y{y}%m{m}%d{d}')\
                        .format(y='年', m='月', d='日')
                elif word != '':
                    if v in ['m', 't']:
                        if k == "半":
                            k = "30"
                        word = word + k
                    elif k != "的":
                        time_res.append(word)
                        word = ''
                # m:数字 t:时间
                elif v in ['m', 't']:
                    if k in ["半", "半个"]:
                        k = "0.5"
                    word = k

            if word != '':
                time_res.append(word)
            result = time_res
            lst_result += result

        last_day = None
        for i in range(0, len(lst_result)):
            try:
                last_day = datetime.strptime(lst_result[i][:11], "%Y年%m月%d日")
            except:
                # 处理多次出现时间信息的文本,eg“明天记得明天记得在3点提醒我出门”
                if last_day is not None:
                    lst_result[i] = last_day.strftime("%Y年%m月%d日")\
                                    + lst_result[i]
                # 证明文本中只有时间段信息，没有其它任何日期信息，e.g.“三分钟提醒我睡觉”
                else:
                    # 区分"一分钟"和"3月5日7点"这两类样本
                    # 假设erase掉下面的关键词后，前面的这类句子长度均会降低到4以下
                    if len(lst_result[i].replace("分钟", "").replace("分", "")
                           .replace("小时", "").replace("时", "")
                           .replace("秒钟", "").replace("秒", "")) < 4 and\
                            lst_result[i].find("点") == -1:
                        # 对"3分钟后xxx"这样的信息处理
                        if lst_result[i][-1] == "分" \
                                and lst_result[i].find("点") == -1:
                            try:
                                value = float(lst_result[i]
                                              .replace("分钟", "")
                                              .replace("分", ""))
                            except:
                                value = self.cn2dig(lst_result[i]
                                                    .replace("分钟", "")
                                                    .replace("分", ""))
                            estimated_time = (self.get_now() +
                                              timedelta(minutes=value))
                        # 对“3小时后xxx”这样的信息处理
                        elif lst_result[i][-1] == "时":
                            try:
                                value = int(float(lst_result[i]
                                                  .replace("小时", "")
                                                  .replace("时", "")
                                                  .replace("个", "")) * 60)
                            except:
                                value = self.cn2dig(lst_result[i]
                                                    .replace("小时", "")
                                                    .replace("时", "")
                                                    .replace("个", "")) * 60
                            estimated_time = (self.get_now()
                                              + timedelta(minutes=value))
                        else:
                            try:
                                value = float(lst_result[i]
                                              .replace("秒钟", "")
                                              .replace("秒", ""))
                            except:
                                value = self.cn2dig(lst_result[i]
                                                    .replace("秒钟", "")
                                                    .replace("秒", ""))
                            estimated_time = (self.get_now()
                                              + timedelta(seconds=value))
                        lst_result[i] = estimated_time\
                            .strftime('%Y{y}%m{m}%d{d}%H{h}%M{mi}%S{s}')\
                            .format(y='年', m='月', d='日',
                                    h='点', mi='分', s='秒')

        final_res = [self.parse_datetime(w) for w in lst_result]
        return [x for x in final_res if x is not None]
