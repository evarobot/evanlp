from sklearn.model_selection import train_test_split
from pandas.core.frame import DataFrame
import matplotlib.pyplot as plt
import pandas as pd
import pickle

from vikinlp.ai_toolkit.visualization import ml_visualization,\
    statistical_visualization
from vikinlp.ai_toolkit.util import zh


def exclude_label_sample(df_complete, insufficient_label, label_name):
    backup_rows = []
    remaining_rows = list(df_complete[label_name])
    for each_label in insufficient_label.index:
        remaining_rows.remove(each_label)
        backup_rows.append(each_label)

    return df_complete[df_complete[label_name].isin(remaining_rows)],\
        df_complete[df_complete[label_name].isin(backup_rows)]


def balance_sample(x_sufficient, y_sufficient, x_insufficient, y_insufficient):
    # 判断是否存在train集某个label，在valid中没有样本的情况
    insufficient_label = set(y_sufficient) - set(y_insufficient)
    for item in insufficient_label:
        index = y_sufficient.index(item)

        y_insufficient.append(item)
        x_insufficient.append(x_sufficient[index])

        y_sufficient.remove(item)
        x_sufficient.remove(x_sufficient[index])


def split_data(input_data, cv_ratio, feature_name, label_name):
    insufficient_label = statistical_visualization.group_label(input_data,
                                                               label_name,
                                                               feature_name,
                                                               [label_name,
                                                                ""],
                                                               False)
    if len(insufficient_label) > 0:
        print("Warning: Insufficient Observations. ")

    sufficient_sample, insufficient_sample \
        = exclude_label_sample(input_data, insufficient_label, label_name)
    list_corpus = sufficient_sample[feature_name].tolist()
    list_labels = sufficient_sample[label_name].tolist()
    # 先按比例抽取30%的数据作为[Validation+Test]
    x_train, x_valid, y_train, y_valid\
        = train_test_split(list_corpus, list_labels, test_size=cv_ratio,
                           stratify=list_labels, shuffle=True)
    list_corpus = insufficient_sample[feature_name].tolist()
    list_labels = insufficient_sample[label_name].tolist()
    x_train += list_corpus
    y_train += list_labels
    x_valid += list_corpus
    y_valid += list_labels

    # 判断是否存在train集某个label，在valid中没有样本的情况
    balance_sample(x_train, y_train, x_valid, y_valid)
    balance_sample(x_valid, y_valid, x_train, y_train)

    return x_train, x_valid, y_train, y_valid


def validate_distribution(list_dataset, feature_name, label_name):
    # 验证生成数据的标签同比例特性
    i = 1
    for item in list_dataset:
        plt.subplot(220+i)
        i += 1
        combination = {label_name: item[0], feature_name: item[1]}
        data_visualization = DataFrame(combination)
        statistical_visualization.group_label(data_visualization,
                                              label_name, feature_name,
                                              [label_name, "Count"])


def dump_dataset(data, feature_name, label_name, train_untrain_rate, valid_test_rate, dump_file=None):
    list_label = ml_visualization.get_distinct_label(data, label_name)
    # label要以统一的[文本-数字编号]对来进行切换
    digital_label = ml_visualization.construct_label(data, label_name)
    # # 将文本类别名转换为数字类别名
    # print(to_categorical(np.asarray(digital_label)))
    data[label_name] = digital_label
    x_train, x_valid, y_train, y_valid = split_data(data, train_untrain_rate,
                                                    feature_name, label_name)
    # 将上面得到的validation集合划分一部分出来作为test
    data_valid = DataFrame({label_name: y_valid, feature_name: x_valid})
    x_valid, x_test, y_valid, y_test = split_data(data_valid, valid_test_rate,
                                                  feature_name, label_name)

    if dump_file is not None:
        with open(dump_file + ".pkl", "wb") as f:
            pickle.dump([list_label, [x_train, y_train], [x_valid, y_valid],
                         [x_test, y_test]], f)

        # 输出分割好的三个数据集
        train_set = pd.DataFrame({label_name: y_train, feature_name: x_train})
        train_set.to_csv(dump_file + "train.csv", index=False)

        valid_set = pd.DataFrame({label_name: y_valid, feature_name: x_valid})
        valid_set.to_csv(dump_file + "valid.csv", index=False)

        test_set = pd.DataFrame({label_name: y_test, feature_name: x_test})
        test_set.to_csv(dump_file + "test.csv", index=False)

    return x_train, y_train, x_valid, y_valid, x_test, y_test, list_label


if __name__ == '__main__':
    zh.set_chinese_font()

    # 读取数据源问题件
    # data = NLPFeeder.read_file("../input/big_guangkai.txt", '@', '$',
    #                            ["意图", "问题"])
    # data.drop_duplicates(inplace=True)

    # dump_dataset(data, "../input/big_guangkai_split.pkl")

    # with open(parameter.split_data, "rb") as f:
    #     [[x_train, y_train], [x_valid, y_valid], [x_test, y_test]]\
    #         = pickle.load(f)

    # x_train, x_valid, y_train, y_valid = split_data(data, 0.3)
    # # print(len(x_train), len(x_valid))
    #
    # data_valid = DataFrame({"意图": y_valid, "问题": x_valid})
    # # print(len(data_valid))
    #
    # x_valid, x_test, y_valid, y_test = split_data(data_valid, 0.5)
    # # print(len(x_valid), len(x_test))
    #
    # 验证生成数据的标签同比例特性
    # validate_distribution([(y_train, x_train), (y_valid, x_valid),
    #                        (y_test, x_test)], feature_name, label_name)
