
import os
from .util import PROJECT_DIR, is_punctuation


stopwords = []


def get_stopwords():
    global stopwords
    with open(os.path.join(PROJECT_DIR, "data/stopwords.txt")) as fp:
        for line in fp.readlines():
            stopwords.append(line[:-1])
    return stopwords
