from datetime import datetime as dt

import evanlp.ner.time_custom as time_custom
import evanlp.ner.time_standard as time_standard


def fix_time():
    return dt(2018, 10, 10, hour=0, minute=0, second=0)


if __name__ == '__main__':
    date_recognizer = time_standard.TimeEntity()
    date_custom_recognizer = time_custom.CustomTimeEntity()
    date_custom_recognizer.get_now = fix_time

    # 单例测试
    # text1 = "定个闹钟"
    # date_entity = date_recognizer.recognize(text1)
    # print(date_entity)
    # if date_entity:
    #     date_entity = date_custom_recognizer.recognize(date_entity)[-1]
    #     print(date_entity)
    # exit()

    with open("../data/date_and_event_recognition.txt", 'r') as f:
        lst_text = f.readlines()

    i = 0
    for item in lst_text:
        lst_entity = item.split("$@")
        lst_entity[2] = lst_entity[2].strip()
        if lst_entity[2][-1] == "-":
            continue
        date_entity = date_recognizer.recognize(lst_entity[0])
        if date_entity:
            if len(lst_entity) > 3:
                lst_entity[3] = lst_entity[3].strip()
                print(lst_entity[0], lst_entity[3], date_entity[-1], sep=';')
                assert(lst_entity[3] == date_entity[-1])
            date_entity = date_custom_recognizer.recognize(date_entity)[-1]
        print(lst_entity[0], lst_entity[2], date_entity, sep=';')
        assert(lst_entity[2] == str(date_entity))
        i += 1
    print("测试完成，共通过" + str(i) + "个测试样本。")
