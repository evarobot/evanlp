import re

import jieba
import jieba.posseg as psg

import evanlp.ner.quantity as quantity


class EventEntity(object):
    def __init__(self):
        jieba.add_word("今天", freq=99999999, tag="m")
        jieba.add_word("下午", freq=99999999, tag="m")
        jieba.add_word("点钟", freq=99999999, tag="m")
        jieba.add_word("分钟", freq=99999999, tag="m")
        jieba.add_word("秒钟", freq=99999999, tag="m")
        jieba.add_word("小时", freq=99999999, tag="m")

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
    def extract_middle(text, key_l, key_r):
        if key_r == "":
            pattern = re.compile(key_l + '(.*)', re.S)
        elif key_l == "":
            pattern = re.compile('(.*)' + key_r, re.S)
        else:
            pattern = re.compile(key_l + '(.*?)' + key_r, re.S)
        lst_result = pattern.findall(text)
        if len(lst_result) > 0:
            result = lst_result[-1]
            return result
        else:
            return None

    def distill_string_boundary(self, text):
        lst_key_l = ["叫", "叫", "提醒", "点", "之后"]
        lst_key_r = ["的日程", "的安排", "的", ""]

        break_flag = False
        result = None
        for key_l in lst_key_l:
            for key_r in lst_key_r:
                result = self.extract_middle(text, key_l, key_r)

                if result is not None and result != "":
                    # print(key_l, key_r)
                    break_flag = True
                    break
            if break_flag:
                break
        return result

    @staticmethod
    def distill_half_string_boundary(text):
        quan_detection = quantity.QuantityEntity()
        lis_quantity = quan_detection._recognize_with_rules(text)
        last_num = None
        if len(lis_quantity) > 0:
            last_num = lis_quantity[-1][-1]
            partial_text = text[text.find(str(last_num))+1:]
            return partial_text
        else:
            return None

    @staticmethod
    def non_sense_cut(text):
        lis_reconstruct_text = []
        for k, v in psg.cut(text):
            if v not in ['m', 't']:
                lis_reconstruct_text.append(k)
        text = "".join(lis_reconstruct_text)

        if text.startswith("的"):
            text = text[1:]
        if text.find("取消") > -1:
            text = text[:text.find("取消")]

        text = text.replace("我", "").replace("的提醒", "").replace("。", "")\
            .replace(".", "").replace("？", "").replace("?", "")\
            .replace("行吗", "").replace("提醒", "").replace("你", "")\
            .replace("好不好嘛", "")

        return text

    def _recognize_with_rules(self, text):
        # 先尝试字符串边界定位法
        result = self.distill_string_boundary(text)

        # 时间位+字符串边界定位法
        if not result:
            result = self.distill_half_string_boundary(text)

        if result:
            result = self.non_sense_cut(result)
        return result
