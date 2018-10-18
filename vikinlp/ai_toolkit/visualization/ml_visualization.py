import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from mpl_toolkits.mplot3d import Axes3D

from vikinlp.ai_toolkit.feeder import NLPFeeder
from vikinlp.ai_toolkit.visualization import statistical_visualization
from vikinlp.ai_toolkit.preprocess import embed


@statistical_visualization.aggregate_text
def aggregate_single_text(df, column_name, list_sequence):
    list_sequence.append(df[column_name])


def map_label_id(df, column_name, dict_label):
    df[column_name] = dict_label[df[column_name]]
    return df[column_name]


def get_distinct_label(df, column_name):
    df_label = df.drop_duplicates(subset=[column_name])
    list_label = list(df_label[column_name])
    return list_label


def construct_label(df, column_name):
    list_label = get_distinct_label(df, column_name)
    dict_label = {}
    index = 0
    for item in list_label:
        dict_label[item] = index
        index += 1

    df[column_name] = df.apply(map_label_id, axis=1,
                               column_name=column_name, dict_label=dict_label)
    return list(df[column_name])


def construct_vector(data, fun, vocabulary=None, feature_name=""):
    list_sequence = aggregate_single_text(data, feature_name)

    if vocabulary is None:
        cv_emb, cv_model = fun(list_sequence)
    else:
        cv_emb, cv_model = fun(list_sequence, vocabulary)

    if type(cv_emb) is list:
        cv_emb = np.array(cv_emb)
    else:
        cv_emb = cv_emb.toarray()

    return cv_emb


def pca(input_data, list_color, component):
    pca_estimator = PCA(n_components=component)
    pca_estimator.fit(input_data)

    # 每个纬度的数值分布方差值
    print(pca_estimator.explained_variance_)
    # 每个纬度的方差占所有纬度方差的比率
    print(pca_estimator.explained_variance_ratio_)
    # 当前PCA模型的降纬后纬度值
    print(pca_estimator.n_components_)

    input_transformed = pca_estimator.transform(input_data)

    if pca_estimator.n_components_ == 2:
        plt.scatter(input_transformed[:, 0], input_transformed[:, 1],
                    marker='o', c=list_color)
        plt.show()
    elif pca_estimator.n_components_ == 3:
        fig = plt.figure()
        Axes3D(fig, rect=[0, 0, 1, 1], elev=30, azim=20)
        plt.scatter(input_transformed[:, 0], input_transformed[:, 1],
                    input_transformed[:, 2], marker='o', c=list_color)
        plt.show()
    else:
        print("Unable to draw.")


def explore_guangkai():
    # 读取数据源问题件
    data = NLPFeeder.read_file("../input/big_guangkai.txt", '@', '$',
                               ["意图", "问题"])

    print(data.describe())
    data.drop_duplicates(inplace=True)

    list_label = construct_label(data, "意图")

    # 通过PCA来进行数据分析
    # 词向量专用方式
    vectors = embed.read_w2v("../../data/sgns.target.word-word."
                             "dynwin5.thr10.neg5.dim300.iter5", 100)
    bow = construct_vector(data, embed.get_word2vec_embeddings, vectors)
    # 非词向量方式
    # bow = construct_vector(data, embed.tfidf)
    pca(bow, list_label, 3)


if __name__ == '__main__':
    explore_guangkai()
