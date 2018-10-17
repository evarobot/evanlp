#!/usr/bin/env python
# encoding: utf-8
import copy

import nltk

from vikinlp.ai_toolkit.util import zh
from vikinlp.ai_toolkit.feeder import NLPFeeder
from vikinlp.ai_toolkit.cleaner import NLP_cleaner


def group_label(df, main_column, auxiliary_column, axis_label, is_plt=True):
    df_grouped = df.groupby([main_column], sort=False)[auxiliary_column]\
        .nunique().sort_values(ascending=True)
    if is_plt:
        df_grouped.plot(kind='bar')
        plt.xlabel(axis_label[0])
        plt.ylabel(axis_label[1])
        plt.show()
    # 将那些对应样本数<2的标签显性返回，因为这部分样本是没有办法划分为三个集合的
    # 还有种情况是样本的采样率太低样本太少，导致按照那个采样率采会导致一个集合中一个样本都没有
    return df_grouped[df_grouped < 2]


def count_word(df, column_name):
    word_number = df[column_name].count(" ") + 1
    return word_number


def count_character(df, column_name):
    character_number = zh.count_characters(df[column_name].strip())
    return character_number


def word_feature(df, column_name):
    df[column_name] = df.apply(count_word, axis=1, column_name=column_name)
    return df


def character_feature(df, column_name):
    df[column_name] = df.apply(count_character, axis=1,
                               column_name=column_name)
    return df


def aggregate_text(func):
    def wrapper(*args):
        list_sequence = []
        args[0].apply(func, axis=1, column_name=args[1],
                      list_sequence=list_sequence)
        return list_sequence
    return wrapper


@aggregate_text
def aggregate_single_text(df, column_name, list_sequence):
    for item in df[column_name].split(" "):
        if item is not "":
            list_sequence.append(item)


def get_frequency(df, column_name):
    word_sequence = aggregate_single_text(df, column_name)
    fd = nltk.FreqDist(word_sequence)
    item = fd.items()
    # print ' '.join(keys)
    dicts = dict(item)
    sort_dict = sorted(dicts.items(), key=lambda d: d[1], reverse=True)

    print("共出现不同词汇个数" + str(len(sort_dict)))
    print("所有词汇词频:\n" + str(sort_dict))


def explore_guangkai():
    zh.set_chinese_font()
    # 读取数据源问题件
    data = NLPFeeder.read_file("../input/big_guangkai.txt", '@', '$',
                               ["意图", "问题"])
    print("原始数据描述：")
    print(data.describe())
    data.drop_duplicates(inplace=True)
    print("去重后数据描述：")
    print(data.describe())

    # 统计每个意图对应的问题数,升序排列并以柱状图来表示
    group_label(data, "意图", "问题", ["意图", "样本数"])
    #
    # # 每个问题词长度对应出现的意图数（相当于不同长度问题下的熵）
    data_word_number = word_feature(copy.deepcopy(data), "问题")
    group_label(data_word_number, "问题", "意图", ["问题中词长度", "意图数"])
    #
    # # 每个问题字长度对应出现的意图数（相当于不同长度问题下的熵）
    data_character_number = character_feature(copy.deepcopy(data), "问题")
    group_label(data_character_number, "问题", "意图", ["问题中字长度", "意图数"])

    # 统计词频
    get_frequency(data, "问题")
    data = NLP_cleaner.remove_all_stop_word(data, "../input/stop_word.txt",
                                            "问题")
    get_frequency(data, "问题")


if __name__ == '__main__':
    explore_guangkai()
