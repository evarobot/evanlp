import pandas as pd
import xlrd
import jieba

from vikinlp.ai_toolkit.util.sys import remove_folder


def read_file(input_path, separator1, separator2, column_name):
    df = pd.read_csv(input_path, separator1, names=column_name)
    df.replace('[' + separator2 + ']', '', regex=True, inplace=True)
    return df


def read_xls(input_path, output_path, str_separator):
    excel_file = xlrd.open_workbook(input_path)
    print(excel_file.sheet_names())
    sheet = excel_file.sheet_by_index(0)
    print(sheet.name, sheet.nrows, sheet.ncols)

    label_name = ""
    for i in range(1, sheet.nrows):
        row = sheet.row_values(i)

        if row[0] != "":
            if row[1] != "":
                label_name = row[1]

            if row[0].find(".") == -1:
                print("Error:" + row[0])
            context = row[0].split(".")[1].strip()

            # 通过结巴分词的全模式对文本内容进行分词
            acc_context = ' '.join(jieba.cut(context, cut_all=False))
            print(acc_context)

            with open(output_path + label_name + ".txt", 'a') as f:
                f.write(label_name + str_separator + acc_context + "\n")


def add_prefix(input_path, output_path, str_prefix, str_separator):
    # lst_text = []
    with open(input_path, 'r') as f:
        lst_text = f.readlines()

    with open(output_path, 'w') as f:
        for item in lst_text:
            acc_context = ' '.join(jieba.cut(item, cut_all=False))
            f.write(str_prefix + str_separator + acc_context)


if __name__ == '__main__':
    output_dir = "../input/query_binary/"
    remove_folder(output_dir)
    read_xls("../input/XiaodouLuo_query.xlsx", output_dir, "$@")
    pass
