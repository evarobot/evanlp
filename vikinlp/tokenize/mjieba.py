# encoding=utf-8

import jieba
import jieba.posseg as pseg

from vikinlp.tokenize.api import TokenizerI


jieba.initialize()  # load default dict immediatly


class JieBa(TokenizerI):
    def __init__(self):
        pass

    def tokenize(self, text):
        words = jieba.cut(text, cut_all=False)
        return list(words)

    def load_userdict(self, fpath):
        """ load a user dict

        :fpath: path to the txt file

        """
        jieba.load_userdict(fpath)

    def posseg_cut(self, text):
        return map(lambda x: (x.word, x.flag), list(pseg.cut(text)))


mjieba = JieBa()

__all__ = ['mjieba']

if __name__ == '__main__':
    print(mjieba.tokenize('今天下午吃饭'))
    print(mjieba.posseg_cut('今天下午吃饭'))
