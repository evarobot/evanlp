# coding=utf-8

import json
import os
import time
import random

from vikinlp.data import resource_url

dpath = resource_url("vikinlp:georgie/PrRecommendDemo/data")

# 饭点规则
# ==================================
tim_lunch_start = time.strptime("11:30:00", "%H:%M:%S")
tim_lunch_end = time.strptime("12:30:00", "%H:%M:%S")
tim_dinner_start = time.strptime("17:30:00", "%H:%M:%S")
tim_dinner_end = time.strptime("18:30:00", "%H:%M:%S")

# 品牌信息
# ==================================
dic_male_clothing = json.load(open(os.path.join(dpath, 'male_clothing.json'), 'r'))
dic_film = json.load(open(os.path.join(dpath, 'film.json'), 'r'))
dic_entertainment = json.load(open(os.path.join(dpath, 'entertainment.json'), 'r'))
dic_delicacy = json.load(open(os.path.join(dpath, 'delicacy.json'), 'r'))
dic_luxuries = json.load(open(os.path.join(dpath, 'luxuries.json'), 'r'))
dic_infant_products = json.load(open(os.path.join(dpath, 'infant_products.json'), 'r'))
dic_cosmetics = json.load(open(os.path.join(dpath, 'cosmetics.json'), 'r'))
dic_female_clothing = json.load(open(os.path.join(dpath, 'female_clothing.json'), 'r'))
# ==================================

# 年龄规则
# ==================================
lis_male_rule = [[5, 30, [dic_film, dic_male_clothing, dic_entertainment, dic_delicacy]],
                 [31, 55, [dic_luxuries, dic_male_clothing, dic_delicacy]],
                 [56, 75, [dic_infant_products, dic_delicacy]]]
lis_femail_rule = [[5, 27, [dic_film, dic_cosmetics, dic_female_clothing, dic_delicacy]],
                   [28, 50, [dic_luxuries, dic_female_clothing, dic_delicacy]],
                   [51, 75, [dic_infant_products, dic_delicacy]]]
# ==================================

# 判断是否是饭点
def boo_meal_time(tim_current):
    if (tim_current >= tim_lunch_start and tim_current <= tim_lunch_end) or \
            (tim_current >= tim_dinner_start and tim_current <= tim_dinner_end):
        return True
    else:
        return False


# 根据年龄建立的所有规则
def lis_age_choice(lis_rules, int_age):
    for item in lis_rules:
        if int_age >= item[0] and int_age <= item[1]:
            return item[2]


# 总的处理逻辑
def lis_final_choice(dic_feature):
    if dic_feature['sex'] == 'male':
        if boo_meal_time(dic_feature['current_time']) == True:
            return [dic_delicacy]
        else:
            return lis_age_choice(lis_male_rule, dic_feature['age'])
    else:
        if boo_meal_time(dic_feature['current_time']) == True:
            return [dic_delicacy]
        else:
            return lis_age_choice(lis_femail_rule, dic_feature['age'])


def recommend(data):
    data['current_time'] = time.strptime(data['time'], "%H:%M:%S")
    lis_class = lis_final_choice(data)
    if lis_class is not None:
        dic_brand = random.choice(lis_class)
        if dic_brand is not None:
            str_brand = random.choice(list(dic_brand.keys()))
            return str_brand, dic_brand[str_brand]
    return None, None


if __name__ == '__main__':
    from vikinlp.util.uniout import use_uniout

    use_uniout(True)
    dic_result = {}
    dic_result['sex'] = 'male'
    dic_result['current_time'] = time.strptime(time.strftime("%H:%M:%S", time.localtime()), "%H:%M:%S")
    dic_result['age'] = 56
    dic_result['with_kid'] = True
    print recommend(dic_result)
