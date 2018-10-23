import copy
from abc import abstractmethod
import logging

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt

from vikinlp.ai_toolkit.util import sys
from vikinlp.ai_toolkit.feeder import NLPFeeder
from vikinlp.ai_toolkit.cleaner import NLP_cleaner
from vikinlp.ai_toolkit.visualization import ml_visualization, \
    statistical_visualization
from vikinlp.ai_toolkit.preprocess import embed, cv_producer
from vikinlp.ai_toolkit.inspection import statistics_based, \
    model_based_not_w2v, model_based_w2v
from vikinlp.ai_toolkit.evaluation import f1_score
import vikinlp.io as io

log = logging.getLogger(__name__)

class QuestionClassfier(object):
    def __init__(self, data=None):
        if data is not None:
            self.data = data
        self.embed = None
        self.lst_label = None
        self.x_train = None
        self.x_valid = None
        self.x_test = None
        self.y_train = None
        self.y_valid = None
        self.y_test = None
        self.clf = None
        self.embed_mode = None
        self.actual_model = None

    @classmethod
    def get_classifier(cls, algorithm):
        if algorithm == "logistic":
            return LogisticRegressionClassifier()

    def split_data(self, feature_name, label_name, train_untrain_rate,
                   valid_test_rate, str_path=None):
        self.x_train, self.y_train, self.x_valid, self.y_valid, \
            self.x_test, self.y_test, self.lst_label \
            = cv_producer.dump_dataset(self.data, feature_name,
                                       label_name, train_untrain_rate,
                                       valid_test_rate, str_path)

    def dr_visualization(self, dimension, str_label_name,
                         w2v_num, feature_name, embed_file):
        list_label = ml_visualization.construct_label(self.data,
                                                      str_label_name)

        if self.embed_mode == "bow":
            bow = ml_visualization.construct_vector(self.data, embed.bow,
                                                    feature_name=feature_name)
        elif self.embed_mode == "tf-idf":
            bow = ml_visualization.construct_vector(self.data, embed.tfidf,
                                                    feature_name)
        else:
            vectors = embed.read_w2v(embed_file, w2v_num)
            bow = ml_visualization. \
                construct_vector(self.data,
                                 embed.get_word2vec_embeddings, vectors,
                                 feature_name)

        ml_visualization.pca(bow, list_label, dimension)

    def des_visualization(self, lst_column_name):
        str_label_name = lst_column_name[0]
        str_feature_name = lst_column_name[1]

        log.debug("原始数据描述：")
        log.debug(self.data.describe())

        # 语料清洗
        log.debug("数据清洗后描述：")
        data = NLP_cleaner.standardize_text(self.data, str_feature_name)
        # data = NLP_cleaner.remove_all_stop_word(data,
        #                                         "../input/stop_word.txt",
        #                                         "问题")
        log.debug(data.describe())

        # 统计每个意图对应的问题数,升序排列并以柱状图来表示
        statistical_visualization.group_label(data, str_label_name,
                                              str_feature_name,
                                              [str_label_name, "Count"])

        # 每个问题词长度对应出现的意图数（相当于不同长度问题下的熵）
        data_word_number \
            = statistical_visualization.word_feature(copy.deepcopy(data),
                                                     str_feature_name)
        log.debug("问题平均长度：" + str(data_word_number[str_feature_name].mean()))
        statistical_visualization. \
            group_label(data_word_number, str_feature_name,
                        str_label_name, ["Length of " + str_feature_name,
                                         "Count of " + str_label_name])

        # 每个问题字长度对应出现的意图数（相当于不同长度问题下的熵）
        data_character_number \
            = statistical_visualization.character_feature(copy.deepcopy(data),
                                                          str_feature_name)
        statistical_visualization.group_label(data_character_number,
                                              str_feature_name,
                                              str_label_name,
                                              ["Length of " + str_feature_name,
                                               "Count of " + str_label_name])

        # 统计词频
        statistical_visualization.get_frequency(data, str_feature_name)

    @staticmethod
    def save_model(model_object, save_path):
        try:
            io.save(model_object, save_path)
            log.debug("Save model to {0}".format(save_path))

            # feature_fname = embed_path
            # io.save(self.feature, feature_fname)
            # log.debug("Save feature to {0}".format(feature_fname))
        except Exception as e:
            log.error(e)
            return False
        return True

    @staticmethod
    def load_model(load_path):
        try:
            model_object = io.load(load_path)
            log.debug("Load model from {0}".format(load_path))

        except Exception as e:
            log.error(e)
            return None
        return model_object

    def train(self, **kwargs):
        # 模型训练
        return self.fit(**kwargs)

    def predict(self, text):
        """
        预测样本
        :param text:
        :return:
        """
        if type(text) is str:
            text = [text]

        if self.embed_mode == "bow" or self.embed_mode == "tf-idf":
            embedded_x_valid = self.embed.transform(text)
        elif self.embed_mode == "w2v-avg":
            embedded_x_valid, _ \
                = embed.get_word2vec_embeddings(text, self.embed)
        else:
            embedded_x_valid = text

        y_predicted = self.actual_model.predict(embedded_x_valid)

        lst_tmp = []
        for i in range(0, len(y_predicted)):
            lst_tmp.append(self.lst_label[y_predicted[i]])
        y_predicted = lst_tmp
        y_predicted_prb = self.clf.predict_proba(embedded_x_valid)
        if len(y_predicted) == 1:
            y_predicted = y_predicted[0]
            y_predicted_prb = max(y_predicted_prb[0])

        return y_predicted, y_predicted_prb

    def evaluation(self, x, y, is_display=False):
        # 模型评估(新版本内容)，目前为了测试旧版本，暂时disable
        # =====
        lst_predicted_label, _ = self.predict(x)

        lst_true_label = []
        for item in y:
            lst_true_label.append(self.lst_label[item])

        # 输出评估指标
        accuracy, precision, recall, f1, _ \
            = f1_score.sklearn_get_metrics(lst_true_label, lst_predicted_label)

        log.debug("accuracy = %.3f, precision = %.3f, recall = %.3f, f1 = %.3f"
              % (accuracy, precision, recall, f1))

        for i in range(0, len(x)):
            if lst_true_label[i] != lst_predicted_label[i]:
                # 深度学习模型输入的x是已经编码化后的序列
                if type(x[i]) is np.ndarray:
                    text = self.tokenizer.sequences_to_texts([list(x[i])])[0]
                # 非深度学习模型输入的x是一个文本的原始形式
                else:
                    text = x[i]
                log.debug(text, "\t", lst_true_label[i],
                                 "\t", lst_predicted_label[i])

        log.debug("*" * 30)
        log.debug("Model Precise: {0}".format(precision))
        matrix = metrics.confusion_matrix(lst_true_label, lst_predicted_label)
        log.debug(matrix)
        report = metrics.precision_recall_fscore_support(lst_true_label,
                                                         lst_predicted_label)
        labels = sorted(set(lst_true_label))

        # 基于统计学的方法
        cm = confusion_matrix(lst_true_label, lst_predicted_label)

        if is_display:
            plt.figure(figsize=(10, 10))
            statistics_based.plot_confusion_matrix(cm,
                                                   classes=self.lst_label,
                                                   normalize=True)

        class_precise = dict(zip(
            labels, map(lambda single_x: "%.2f" % round(single_x, 2),
                        report[0])))
        return {
            'class_precise': class_precise,
            'total_precise': precision
        }

    def lime_visualization(self, feature, label, output_path,
                           max_sequence_length=10, tokenizer=None):

        label = self.lst_label.index(label)
        model_based_w2v\
            .visualize_one_exp(feature, label,
                               self.lst_label, self.clf, self.embed,
                               tokenizer, output_path=output_path,
                               max_sequence_length=max_sequence_length)

    def word_importance(self, word_num):
        # 基于模型的方法
        # 只能用于BOW或者TF-IDF词典，不可用于Word2Vec
        model_based_not_w2v.batch_plot_importance(self.embed, self.clf,
                                                  self.lst_label,
                                                  word_num=word_num)

    def get_data(self, str_input_path, lst_column_name,
                 separator1, separator2):
        """
        载入数据
        :param str_input_path:
        :param lst_column_name:
        :param separator1:
        :param separator2:
        :return:
        """
        data = pd.DataFrame(columns=lst_column_name)

        list_file = sys.file_list(str_input_path)

        for item in list_file:
            cur_df = NLPFeeder.read_file(item,
                                         separator1, separator2,
                                         lst_column_name)
            data = pd.concat([data, cur_df], axis=0)

        data.drop_duplicates(inplace=True)
        self.data = data

    @abstractmethod
    def refresh_coef(self):
        pass

    @abstractmethod
    def fit(self):
        pass


class LogisticRegressionClassifier(QuestionClassfier):
    def __init__(self):
        QuestionClassfier.__init__(self)

        self.clf = self
        self.actual_model = LogisticRegression(C=30.0, class_weight="balanced",
                                               solver='liblinear',
                                               n_jobs=-1, random_state=0)
        self.clf.predict_proba = self.actual_model.predict_proba
        self.clf.fit = self.fit

    # 需要参数如下：x,y,embed_path,max_num
    def fit(self, **kwargs):
        # 词典嵌入
        if self.embed_mode == "bow":
            embedded_x_train, self.embed = embed.bow(kwargs["x"])
        elif self.embed_mode == "tf-idf":
            embedded_x_train, self.embed = embed.tfidf(kwargs["x"])
        else:
            self.embed = embed.read_w2v(kwargs["embed_path"],
                                        kwargs["max_num"])
            embedded_x_train, _ = embed.get_word2vec_embeddings(kwargs["x"],
                                                                self.embed)

        # 模型训练
        self.actual_model.fit(embedded_x_train, kwargs["y"])
        self.refresh_coef()

        # 输出模型评估报告
        return self.evaluation(self.x_valid, self.y_valid)

    def refresh_coef(self):
        self.coef_ = self.actual_model.coef_
