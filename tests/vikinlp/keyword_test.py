from vikinlp.ner import keyword

if __name__ == "__main__":
    KeywordRecognizer = keyword.KeyWordEntity()
    result = KeywordRecognizer.recognize("你在干嘛？", ["干嘛", "你"])
    assert result == ['你', '干嘛']

    result = KeywordRecognizer.recognize("你在干嘛？", ["干嘛", "你", "-在"])
    assert result == []
