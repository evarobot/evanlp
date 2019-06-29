import evanlp.ner.time_custom as time_custom
import evanlp.ner.time_standard as time_standard
import evanlp.ner.quantity as quantity

if __name__ == '__main__':
    tim_detection = quantity.QuantityEntity()
    str_time = tim_detection._recognize_with_rules("77779990是你的编号？")[-1]

#
    with open("../data/quantity_recognition.txt", 'r') as f:
        lst_text = f.readlines()

    for item in lst_text:
        lst_entity = item.split("$@")
        lst_entity[1] = lst_entity[1].strip()
        quantity_entity = tim_detection._recognize_with_rules(lst_entity[0])[-1]

        print(lst_entity[0], lst_entity[1], quantity_entity, sep=';')
        assert(lst_entity[1] == quantity_entity)
