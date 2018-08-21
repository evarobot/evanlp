#!/usr/bin/env python
# encoding: utf-8


from vikinlp.nlp.tokenize.api import TokenizerI



class LTP(TokenizerI):
    def __init__(self):
        pass

    def tokenize(self, text):
        words = jieba.cut(text, cut_all=False)
        return words

    def load_userdict(self, fpath):
        """ load a user dict

        :fpath: path to the txt file

        """
        pass



ltp = LTP()

__all__ = ['ltp']

if __name__ == '__main__':
    print list(ltp.tokenize('今天下午吃饭'))
