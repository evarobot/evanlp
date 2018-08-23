#!/usr/bin/env python
# encoding: utf-8


class Text(object):
    """ tool kit for text"""
    def __init__(self, text):
        self.text = text.decode('utf8')

    def __len__(self):
        return len(self.text)

    def word_num(self):
        return len(set(self.text))

    def count(self,  word):
        """ return the count of a specific word """
        pass

    def words(self,  word):
        """ return the word set of text """
        pass


def test_text():
    text = Text("你好")
    assert(len(text) == 2)

    text = Text("hello")
    assert(len(text) == 5)

    text = Text("你你好")
    assert(text.word_num() == 2)


if __name__ == '__main__':
    test_text()

