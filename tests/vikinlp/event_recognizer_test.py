from vikinlp.ner import event

if __name__ == '__main__':
    event_recognizer = event.EventEntity()

    # 单例测试
    # text1 = "定个闹钟"
    # print(event_recognizer.recognize(text1))
    # exit()

    with open("../data/date_and_event_recognition.txt", 'r') as f:
        lst_text = f.readlines()

    i = 0
    for item in lst_text:
        lst_entity = item.split("$@")
        lst_entity[2] = lst_entity[2].strip()
        if lst_entity[1][-1] == "-" or lst_entity[2][-1] == "-":
            continue

        event_entity = event_recognizer.recognize(lst_entity[0])

        print(lst_entity[0], lst_entity[1], event_entity, sep=';')
        assert(lst_entity[1] == str(event_entity))
        i += 1
    print("测试完成，共通过" + str(i) + "个测试样本。")