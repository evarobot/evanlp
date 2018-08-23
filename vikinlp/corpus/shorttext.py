# encoding: utf-8

import os
from vikinlp.util import PROJECT_DIR

data_path = os.path.join(PROJECT_DIR, 'data/corpus')


class BaiduKnows(object):
    def __init__(self, count=10):
        self._text= []

    @property
    def text(self):
        ''' return text line by line '''
        if self._text:
            return self._text
        list_dirs = os.walk(os.path.join(data_path, 'baidu_knows'))
        for path, dirs, files in list_dirs:
            for f in files:
                if f.endswith('txt'):
                    source = os.path.join(path, f)
                    lines = [line.rstrip('\n') for line in open(source)]
                    for line in lines:
                        self._text.append(line)
        return self._text

    def iter_text(self):
        ''' return text line by line '''
        list_dirs = os.walk(os.path.join(data_path, 'baidu_knows'))
        for path, dirs, files in list_dirs:
            for f in files:
                if f.endswith('txt'):
                    source = os.path.join(path, f)
                    lines = [line.rstrip('\n') for line in open(source)]
                    for line in lines:
                        yield line


baidu_knows = BaiduKnows()

if __name__ == '__main__':
    for i, line in enumerate(baidu_knows.iter_text()):
        if i > 30:
            break
        print line

