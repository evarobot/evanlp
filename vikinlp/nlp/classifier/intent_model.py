#!/usr/bin/env python
# encoding: utf-8

import math
import os
import sys
import numpy as np
import pandas as pd
from collections import namedtuple
from sklearn.base import BaseEstimator, TransformerMixin

from vikinlp.data import resource_url
from vikinlp.nlp.tokenize.mjieba import mjieba
from vikinlp.util import is_punctuation
from vikinlp.util.log import gen_log as log
from vikinlp.util.uniout import use_uniout

CUR_DIR = os.path.dirname(os.path.realpath(__file__))
WORD_NUM_TXT = os.path.join(CUR_DIR, "word_num.txt")
SAME_NUM_TXT = os.path.join(CUR_DIR, "same2.txt")
STOP_WORDS_TXT = os.path.join(CUR_DIR, "stopwords.txt")
KEY_WORDS_TXT = os.path.join(CUR_DIR, "keywords.txt")

domain_threhold = 50

# 同义词替换，暂时不用
synonym_dict = {}
lines = [line.rstrip('\n') for line in open(SAME_NUM_TXT)]
for line in lines:
    t = line.split(' ')
    synonym_dict[t[0]] = set(t[1:])


def replace_with_synonym_question(question):
    """
    同义词替换
    """
    for sword, synonyms in synonym_dict.iteritems():
        for t in sorted(synonyms, key=lambda x: len(x), reverse=True):
            if t in question:
                question = question.replace(t, sword)
    return question


def parse_labled_source(source):
    """
    return: {labelx: [inst1, inst2, ..], ..}

    """
    class Data(object):
        pass

    f = open(source, "r")
    labels = []
    data = []
    train = Data()
    for line in f:
        line = line.rstrip('\n')
        key, sent = line.split("$@")
        labels.append(key)
        #data.append(replace_with_synonym_question(sent))
        data.append(sent)
    train.data = np.array(data)
    train.target = np.array(labels)
    return train


def parse_labled_data(iterable):
    """
    return: {labelx: [inst1, inst2, ..], ..}

    """
    class Data(object):
        pass

    labels = []
    data = []
    train = Data()
    for line in iterable:
        line = line.rstrip('\n')
        key, sent = line.split("$@")
        labels.append(key)
        #data.append(replace_with_synonym_question(sent))
        data.append(sent)
    train.data = np.array(data)
    train.target = np.array(labels)
    return train


class WordsCounter(object):
    """ 通用语料统计 """
    def __init__(self):
        self.word_num = {}

    def initialize(self):
        if os.path.exists(WORD_NUM_TXT):
            self._init_with_cache()
        else:
            log.info("Init with baidu corpus.")
            self._init_with_corpus()

    def count(self, word):
        """ str word
        """
        return self.word_num.get(word, 0)

    def length(self):
        return len(self.word_num.keys())

    def _init_with_cache(self):
        with open(WORD_NUM_TXT, 'r') as f:
            for line in f:
                line = line.rstrip('\n')
                try:
                    word, num = tuple(line.split(' '))
                except ValueError as e:
                    log.error(e)
                    log.error(line)
                self.word_num[word] = num

    def _init_with_corpus(self):
        #  TODO: cache decrator
        f = open("/home/wells/baidu_cache.txt")
        fcache = open(WORD_NUM_TXT, "w")
        for i, line in enumerate(f):
            line = line.rstrip('\n')
            words = mjieba.tokenize(line)
            for w in words:
                t = self.word_num.setdefault(w.encode('utf8'), 0)
                t += 1
                self.word_num[w.encode('utf8')] = t

        t = sorted(self.word_num.items(), key=lambda x: x[1], reverse=True)
        for key, value in t:
            fcache.write("%s %s\n" % (key, value))
        fcache.close()

##############################
#特征处理
##############################

class PosSeg(BaseEstimator, TransformerMixin):
    def fit(self, x, y=None):
        return self

    def transform(self, posts):
        features = np.recarray(shape=(len(posts),),
                               dtype=[('word', object), ('pos', object)])
        for i, text in enumerate(posts):
            ret = mjieba.posseg_cut(text)
            ret_no_punct = filter(lambda x: x[1] != 'x', ret)
            word_list, pos_list = zip(*ret_no_punct)
            features['word'][i] = word_list
            features['pos'][i] = pos_list
        return features


class PosSegWithStopWords(BaseEstimator, TransformerMixin):
    def fit(self, x, y=None):
        return self

    def transform(self, posts, url):
        f = open(resource_url(url), "r")
        stop_words = set([line.rstrip('\n') for line in f])
        features = np.recarray(shape=(len(posts),),
                               dtype=[('word', object), ('pos', object)])
        for i, text in enumerate(posts):
            ret = mjieba.posseg_cut(text)
            ret_no_punct = filter(lambda x: x[1] != 'x', ret)
            ret_no_stopwords = filter(lambda x: x[0].encode('utf-8') not in stop_words, ret_no_punct)
            if ret_no_stopwords:
                word_list, pos_list = zip(*ret_no_stopwords)
                features['word'][i] = word_list
                features['pos'][i] = pos_list
            else:
                features['word'][i] = []
                features['pos'][i] = []
        return features


class Frequent(BaseEstimator, TransformerMixin):
    def fit(self, x, y=None):
        return self

    def transform(self, word_pos):
        features = np.recarray(shape=(len(word_pos),),
                               dtype=[('domain_freq', object), ('corpus_freq', object)])
        domain_word_num = {}
        for words in word_pos['word']:
            for word in words:
                num = domain_word_num.setdefault(word, 0)
                domain_word_num[word] = num + 1

        wordsinfo = WordsCounter()
        wordsinfo.initialize()
        for i, word_list in enumerate(word_pos['word']):
            freqs = map(lambda w: domain_word_num[w], word_list)
            corpus_freqs = map(lambda w: wordsinfo.count(w.encode('utf8')),
                               word_list)
            features['domain_freq'][i] = freqs
            features['corpus_freq'][i] = corpus_freqs

        return features


class TFIDF(BaseEstimator, TransformerMixin):
    def fit(self, x, y=None):
        self._data = x
        self._target = y
        return self

    def transform(self, word_pos):
        features = np.recarray(shape=(len(word_pos),),
                               dtype=[('tfidf', object)])
        word_label_num = {}  # 词在特定类别中出现的次数

        for i, words in enumerate(word_pos['word']):
            label = self._target[i]
            for word in words:
                labels_num = word_label_num.setdefault(word, {})
                num = labels_num.setdefault(label, 0)
                labels_num[label] = num + 1

        for i, words in enumerate(word_pos['word']):
            tfidfs = []
            label = self._target[i]
            for word in words:
                tfidfs.append(self._tfidf(word_label_num,
                                          label, word, len(word_pos)))
            features['tfidf'][i] = tfidfs
        return features

    def _tfidf(self, documents, label, word, num_docs):
        label_num = documents[word]
        appear_labels = len(label_num.keys())
        term_freq = label_num[label]
        ret = term_freq * math.log10(num_docs/float(appear_labels))
        return round(ret, 1)


class KeyWords(BaseEstimator, TransformerMixin):
    def fit(self, x, y=None):
        self._data = x
        self._target = y
        return self

    def transform(self, input_features):
        features = np.recarray(shape=(len(input_features),),
                               dtype=[('keywords', object)])
        for i, row in input_features.iterrows():
            features['keywords'][i] = set(self._statistic(row))  # t为词袋的列表形式
        return features

    def _statistic(self, features):
        ret_features = []
        word_num = len(features['word'])
        if word_num == 0:
            ret_features = self._feature(features, "n0v0")
        else:
            ret_features = self._feature(features, "nxvx")
        for ft in ret_features:
            if ft:
                yield ft.word

    def _feature(self, ft, type_):
        Feature = namedtuple('Feature',
                             'word, pos, tfidf, domain_freq, corpus_freq')
        word_features = zip(ft['word'], ft['pos'], ft['tfidf'],
                            ft['domain_freq'], ft['corpus_freq'])
        word_features = map(lambda x: Feature(*x), word_features)

        if type_ == "n0v0":
            the_word = None
            max_ratio = 0
            for ft in word_features:
                if ft.corpus_freq == 0:
                    if ft.domain_freq > domain_threhold:
                        the_word = ft
                    continue
                ratio = ft.domain_freq / float(ft.corpus_freq)
                if ratio > max_ratio:
                    the_word = ft
                    max_ratio = ratio
            return [the_word]

        elif type_ == "nxvx":
            n_v_features = []
            wordset = set()
            for ft in word_features:
                if ft.corpus_freq == 0:
                    ft = Feature(ft.word, ft.pos, ft.tfidf, ft.domain_freq, 1)
                if ft.word not in wordset:
                    n_v_features.append(ft)
                wordset.add(ft.word)

            t = sorted(n_v_features, key=lambda x: x.tfidf, reverse=True)
            if len(t) == 1 or t[0].tfidf > t[1].tfidf*2:
                return t[:1]
            # elif len(t) == 2 or t[1].tfidf > t[2].tfidf*2:
            else:
                return t[:2]
            # elif len(t) == 3 or t[2].tfidf > t[3].tfidf*2:
            #    return t[:3]
            # else:
            #    return t[:4]


##############################
# 基于词袋的规则构建
##############################

class BagOfWords(BaseEstimator, TransformerMixin):

    def fit(self, x, y=None):
        self._train_data = x
        self._train_target = y
        self.mode = "product"  # product, dev

        # 以下两个是要存数据库的。
        self._exact_rules = {}
        self.rules = None
        return self

    def transform(self, features):
        """ 测试

        :data: TODO
        :returns: TODO
        """
        sample_keywords = features['keywords']
        bows = map(self._construct_bag_of_words, sample_keywords)
        data = pd.DataFrame({'bow': bows, 'label': self._train_target, 'keywords': features['keywords'], 'sample': self._train_data})
        # self.output_bow_conflict(data)
        self.output_keywords_number(data)
        self.rules = self._construct_rules(data)
        return features

    def output_keywords_number(self, data):
        allf = open(KEY_WORDS_TXT, "w")
        groups = data.groupby('label')
        for key, value in groups.groups.iteritems():
            g = groups.get_group(key)
            keywords = list(g['keywords'])
            keywords_number = []
            for i in xrange(len(keywords)):
                if keywords[i] not in map(lambda x: x[0], keywords_number):
                    keywords_number.append([keywords[i], keywords.count(keywords[i])])
            output = []
            for k_n in keywords_number:
                keywords, number = tuple(k_n)
                keywords = ' '.join(keywords)
                output.append(keywords + '\t'  + str(number))
            output = key + '\n' + '\n'.join(output) + '\n'
            allf.write(output)

    def output_bow_conflict(self, data):
        """

        :data: TODO
        :returns: TODO

        """
        groups = data.groupby('bow')
        conflict_num = 0
        for key, value in groups.groups.iteritems():
            g = groups.get_group(key)
            labels = set(g['label'])
            if len(labels) > 1:
                conflict_num += 1

    def _construct_rules(self, data):
        """ 构建基于关键词词袋的规则。

        :data: 包含了sample, 关键词，label
        :returns: 规则集合{label1: [r1, r2, ...], ...}, 比如:

        {'信用卡境外消费手续费': [[-3124387127653363973, set([u'国外', u'手续费', u'信用卡', u'收']), 1], ...], ...}
        """
        groups = data.groupby('label')
        rules = {}
        for label, value in groups.groups.iteritems():
            g = groups.get_group(label)
            label_bow_groups = g.groupby('bow')
            sub_rules = rules.setdefault(label, [])
            for bow, value in label_bow_groups.groups.iteritems():
                sub_rules.append([bow, data['keywords'][value[0]],
                                  len(value)])  # hash, 关键词集合，出现次数

        # 训练时对错的分类问题构建精确分类规则
        for i, text in enumerate(self._train_data):
            label = self._train_target[i]
            rst = self._rule_match(text, rules)
            labels = set(map(lambda x: x[0], rst))
            if len(labels) > 1 or label != list(labels)[0]:     # 添加一个判断条件
                self._add_exact_rule(text, label)
        self.conflict_num = len(self._exact_rules)
        log.info("冲突的规则数目：%d" % self.conflict_num)
        return rules

    def _rule_match(self, text, rules):
        result = []
        max_len = 0
        for label, sub_rules in rules.iteritems():
            for sub_rule in sub_rules:
                bow, keywords, occur_num = tuple(sub_rule)
                match = True
                for word in keywords:
                    if word not in text:
                        match = False
                if match:
                    result.append([label, sub_rule, len(keywords)])
                    if len(keywords) > max_len:
                        max_len = len(keywords)
        result = filter(lambda x: x[2] == max_len, result)  #最长匹配：把非最长的去掉
        return result

    def _exact_rule_match(self, text):
        words = mjieba.tokenize(text)
        words = filter(lambda x: not is_punctuation(x), words)
        return self._exact_rules.get(hash(' '.join(words)), None)

    def _add_exact_rule(self, text, label):
        words = mjieba.tokenize(text)
        words = filter(lambda x: not is_punctuation(x), words)
        self._exact_rules[hash(' '.join(words))] = label

    def match(self, text):
        """ 匹配文本
        :returns: list of labels
        """
        if self.mode == "product":
            label = self._exact_rule_match(text)
            if label:
                return label
        rst = self._rule_match(text, self.rules)
        if not rst:
            return None
        labels = list(set(map(lambda x: x[0], rst)))
        # assert(len(labels) == 1)
        return labels[0]

    def predict(self,  data):
        """ 批量测试，仿sklearn
        """
        for text in data:
            yield self.match(text)

    def _construct_bag_of_words(self, words):
        bag = 0
        for word in words:
            bag += hash(word)
        return bag % sys.maxsize

def output_features(features, labels):
    output = []
    allf = open(KEY_WORDS_TXT, "w")
    for i in xrange(len(features)):
        new_output_features = []
        output.append(labels[i])
        output_features = zip((features['word'][i]),
                              map(str, features['tfidf'][i]),
                              features['pos'][i],
                              map(str, features['corpus_freq'][i]),
                              map(str, features['domain_freq'][i]))
        for output_feature in output_features:
            output_feature = ' / '.join(output_feature)
            new_output_features.append(output_feature)
        output_features = '\n'.join(new_output_features)
        output.append(output_features)
        output.append('\t'.join(features['keywords'][i]))
        output.append('\n')
    output = '\n'.join(output)
    allf.write(output)

def output_keywords(features, labels):
    label_bows = {}
    output = []
    allf = open(KEY_WORDS_TXT, "w")
    for i in xrange(len(features)):
        bows = label_bows.setdefault(labels[i], [])
        bows.append(features['keywords'][i])
    for label, bows in label_bows.iteritems():
        new_bows = []
        for bow in bows:
            bow = '\t'.join(bow)
            new_bows.append(bow)
        new_bows = label + '-'*5 +'\n' + '\n'.join(new_bows)
        output.append(new_bows)
    output = "\n".join(output)
    allf.write(output)

def construct_bow_classifyier(train):
    # posseg = PosSeg()
    posseg = PosSegWithStopWords()
    freq = Frequent()
    tfidf = TFIDF()
    keywords = KeyWords()

    word_pos_feature = posseg.fit(train.data).transform(train.data, STOP_WORDS_TXT)

    freq_feature = freq.fit(train.data).transform(word_pos_feature)

    tfidf_feature = tfidf.fit(train.data,
                              train.target).transform(word_pos_feature)

    features = pd.DataFrame({'word': word_pos_feature['word'],
                             'pos': word_pos_feature['pos'],
                             'domain_freq': freq_feature['domain_freq'],
                             'corpus_freq': freq_feature['corpus_freq'],
                             'tfidf': tfidf_feature['tfidf']
                             })
    d = keywords.fit(train.data).transform(features)
    features['keywords'] = d['keywords']
    output_features(features, train.target)
    output_keywords(features, train.target)

    bow = BagOfWords()
    bow.fit(train.data, train.target)
    bow.transform(features)
    return bow


class BagOfWordsProduct(BagOfWords):

    def load_model(self, arg1):
        """TODO: Docstring for load_rule.

        :arg1: TODO
        :returns: TODO

        """
        pass

    def save_model(self, arg1):
        """TODO: Docstring for save_exact_rule.

        :arg1: TODO
        :returns: TODO

        """
        pass




if __name__ == '__main__':
    use_uniout(True)

    train = parse_labled_source("./air.txt")
    # train = parse_labled_source("./guangkai.txt")
    bow = construct_bow_classifyier(train)

    num = 0
    for i, text in enumerate(train.data):
        ret = bow.match(text)
        if ret == train.target[i]:
            num += 1
        else:
            print text
            log.info("数据有误，不同的label对应着相同数据: %d" % i)
            print ret, train.target[i]


    log.info('sample num: %d' % len(train.data))
    log.info('label num: %d' % len(set(train.target)))
    log.info('test passed: %d' % num)
