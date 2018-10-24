import copy

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report
from sklearn.datasets import make_classification

from vikinlp.ai_toolkit.assemble_technique import co_training_framework
from vikinlp.classifier.dl_framework import Instance, DeepLearningArchitecture
from vikinlp.classifier import lstm, cnn
from vikinlp.ai_toolkit.feeder import NLPFeeder
from vikinlp.ai_toolkit.preprocess import cv_producer


def co_training():
	lstm_model = Instance(lstm.lstm)


	# 1号模型
	predictor, parameters = lstm_model.model_selection()
	parameters.verbose = False

	lstm_model.data_cv_split(predictor, 0.7, 0.5)
	# 载入未标注的数据
	cur_df = NLPFeeder.read_file("../../data/query_unlabeled_origin_char/unlabeled_data.txt",
								 "@", "$",
								 ["意图", "问题"])
	cur_df.drop_duplicates(inplace=True)
	x_train, a, y_train, a = cv_producer.split_data(cur_df, 0, "问题", "意图")
	predictor.x_train += x_train
	predictor.y_train += y_train


	# =====
	# 2号模型
	lstm_model2 = Instance(cnn.TextCNN)
	predictor2, parameters2 = lstm_model2.model_selection()
	parameters2.verbose = False

	predictor2.x_train, predictor2.x_valid, predictor2.x_test,\
	predictor2.y_train, predictor2.y_valid, predictor2.y_test,\
	predictor2.lst_label\
		= copy.deepcopy(predictor.x_train), predictor.x_valid, predictor.x_test,\
		  predictor.y_train, predictor.y_valid, predictor.y_test,\
		  predictor.lst_label

	# =====
	lstm_model.data_transformer(predictor, 20, 0)
	lstm_model2.data_transformer(predictor2, 20, 0,
								 "../../data/sgns.target.word-character."
								 "char1-1.dynwin5.thr10.neg5.dim300.iter5")

	# lstm_instance = DeepLearningArchitecture(lstm.lstm)
	co_clf = co_training_framework.CoTrainingClassifier(predictor, predictor2, k=30, u=75)
	co_clf.fit(predictor.x_train, predictor.x_train, predictor.y_train_origin,
					max_iter=50,
					x1=predictor.x_train,
					x1_text=predictor.x_train_origin,
					x2=predictor2.x_train,
					x2_text=predictor2.x_train_origin,

					y_=predictor.y_train, y_text=predictor.y_train_origin,
					x_valid=predictor.x_valid, y_valid=predictor.y_valid,
					y_valid_text=predictor.y_valid_origin,
					saver_path=["../../data/model/checkpoints/", "model.meta"],
					parameter=parameters,
					labels=predictor.lst_label
					)

	# 测试预测功能

	y_pred = co_clf.predict(predictor.x_valid, predictor.x_valid, predictor.lst_label)
	# print(y_pred)

	lst_true_label = []
	for item in predictor.y_valid_origin:
		lst_true_label.append(predictor.lst_label[item])


	# 输出评估指标
	from vikinlp.ai_toolkit.evaluation import f1_score
	accuracy, precision, recall, f1, _ \
		= f1_score.sklearn_get_metrics(lst_true_label, y_pred)

	str_score = ("accuracy = %.3f, precision = %.3f, recall = %.3f, f1 = %.3f"
				 % (accuracy, precision, recall, f1))
	print(str_score)


if __name__ == '__main__':
	co_training()
	exit()


	N_SAMPLES = 25000
	N_FEATURES = 1000
	X, y = make_classification(n_samples=N_SAMPLES, n_features=N_FEATURES)

	y[:N_SAMPLES//2] = -1

	X_test = X[-N_SAMPLES//4:]
	y_test = y[-N_SAMPLES//4:]

	X_labeled = X[N_SAMPLES//2:-N_SAMPLES//4]
	y_labeled = y[N_SAMPLES//2:-N_SAMPLES//4]

	y = y[:-N_SAMPLES//4]
	X = X[:-N_SAMPLES//4]


	X1 = X[:,:N_FEATURES // 2]
	X2 = X[:, N_FEATURES // 2:]



	# 训练一个模型可以预测
	print ('Logistic')
	base_lr = LogisticRegression()
	base_lr.fit(X_labeled, y_labeled)
	y_pred = base_lr.predict(X_test)
	print (classification_report(y_test, y_pred))

	print ('Logistic CoTraining')
	lg_co_clf = co_training_framework.CoTrainingClassifier(LogisticRegression())
	lg_co_clf.fit(X1, X2, y)
	y_pred = lg_co_clf.predict(X_test[:, :N_FEATURES // 2], X_test[:, N_FEATURES // 2:])
	print (classification_report(y_test, y_pred))

	print ('SVM')
	base_svm = LinearSVC()
	base_svm.fit(X_labeled, y_labeled)
	y_pred = base_lr.predict(X_test)
	print (classification_report(y_test, y_pred))
	
	print ('SVM CoTraining')
	svm_co_clf = co_training_framework.CoTrainingClassifier(LinearSVC(), u=N_SAMPLES//10)
	svm_co_clf.fit(X1, X2, y)
	y_pred = svm_co_clf.predict(X_test[:, :N_FEATURES // 2], X_test[:, N_FEATURES // 2:])
	print (classification_report(y_test, y_pred))
	
	
