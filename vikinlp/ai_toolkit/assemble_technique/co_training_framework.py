import numpy as np
import random
import copy
import math
import collections

from vikinlp.classifier.dl_framework import DeepLearningArchitecture
from keras.utils import to_categorical

class CoTrainingClassifier(object):
	"""
	Parameters:
	clf - The classifier that will be used in the cotraining algorithm on the X1 feature set
		(Note a copy of clf will be used on the X2 feature set if clf2 is not specified).

	clf2 - (Optional) A different classifier type can be specified to be used on the X2 feature set
		 if desired.

	p - (Optional) The number of positive examples that will be 'labeled' by each classifier during each iteration
		The default is the is determined by the smallest integer ratio of positive to negative samples in L (from paper)

	n - (Optional) The number of negative examples that will be 'labeled' by each classifier during each iteration
		The default is the is determined by the smallest integer ratio of positive to negative samples in L (from paper)

	k - (Optional) The number of iterations
		The default is 30 (from paper)

	u - (Optional) The size of the pool of unlabeled samples from which the classifier can choose
		Default - 75 (from paper)
	"""

	def __init__(self, clf, clf2=None, propotion={}, k=30, u = 75):
		self.clf1_ = clf
		
		#we will just use a copy of clf (the same kind of classifier) if clf2 is not specified
		if clf2 == None:
			self.clf2_ = copy.copy(clf)
		else:
			self.clf2_ = clf2

		#if they only specify one of n or p, through an exception
		# if (p == -1 and n != -1) or (p != -1 and n == -1):
		# 	raise ValueError('Current implementation supports either both p and n being specified, or neither')

		self.propotion_ = propotion
		# self.n_ = n
		self.k_ = k
		self.u_ = u

		random.seed()

	def fit_dl(self, clf, x, y, x_text, y_continuous, kwargs):

		if isinstance(clf, DeepLearningArchitecture):
			clf.fit(max_iter=kwargs["max_iter"], x=x,
					x_text=x_text,
					y=y, y_text=y_continuous,

					x_valid=kwargs["x_valid"], y_valid=kwargs["y_valid"],
					y_valid_text=kwargs["y_valid_text"],
					saver_path=kwargs["saver_path"],
					parameter=kwargs["parameter"])
			clf.load_tf_model([kwargs["parameter"].model_dump_path + "checkpoints/", "model.meta"])
		else:
			clf.fit(x, y)

	@staticmethod
	def func1(num_list):
		''' 直接使用set方法 '''
		if len(num_list)!=len(set(num_list)):
			print('have duplicates!!!')
		else:
			print('no duplicates!!')


	def fit(self, X1, X2, y, **kwargs):

		"""
		Description:
		fits the classifiers on the partially labeled data, y.

		Parameters:
		X1 - array-like (n_samples, n_features_1): first set of features for samples
		X2 - array-like (n_samples, n_features_2): second set of features for samples
		y - array-like (n_samples): labels for samples, -1 indicates unlabeled

		"""

		X1_text, Y1_continuous, X2_text, Y_dl = None, None, None, None
		if isinstance(self.clf1_, DeepLearningArchitecture):
			X1_text = kwargs["x1_text"]
			Y_dl = kwargs["y_"]

		if isinstance(self.clf1_, DeepLearningArchitecture):
			X2_text = kwargs["x2_text"]
			Y_dl = kwargs["y_"]

		#we need y to be a numpy array so we can do more complex slicing
		y = np.asarray(y)

		# 统计每个类别所占的比例
		#set the n and p parameters if we need to



		# category
		# for item in kwargs["labels"]:
		# 	for i in range(0, len(y)):
		# 		if y[i] == item


		int_count = 0
		for i in range(0, len(kwargs["labels"])):
			if kwargs["labels"][i] not in self.propotion_.keys():
				num = sum(1 for y_i in y if y_i == str(i))
				int_count += num
				self.propotion_[kwargs["labels"][i]] = num
		int_count = int_count / len(kwargs["labels"])

		for item in self.propotion_:
			self.propotion_[item] = round(self.propotion_[item] / float(int_count))

		# if self.p_ == -1 and self.n_ == -1:
		# 	num_pos = sum(1 for y_i in y if y_i == 1)
		# 	num_neg = sum(1 for y_i in y if y_i == 0)
		#
		# 	n_p_ratio = num_neg / float(num_pos)
		#
		# 	if n_p_ratio > 1:
		# 		self.p_ = 1
		# 		self.n_ = round(self.p_*n_p_ratio)
		#
		# 	else:
		# 		self.n_ = 1
		# 		self.p_ = round(self.n_/n_p_ratio)

		for item in self.propotion_:
			assert self.propotion_[item] > 0

		assert(self.k_ > 0 and self.u_ > 0)

		#the set of unlabeled samples
		U = [i for i, y_i in enumerate(y) if y_i == -1 or y_i == "-1"]

		#we randomize here, and then just take from the back so we don't have to sample every time
		random.shuffle(U)

		#this is U' in paper
		U_ = U[-min(len(U), self.u_):]

		#the samples that are initially labeled
		L = [i for i, y_i in enumerate(y) if y_i != -1 and y_i != "-1"]

		#remove the samples in U_ from U
		U = U[:-len(U_)]

		it = 0 #number of cotraining iterations we've done so far

		#loop until we have assigned labels to everything in U or we hit our iteration break condition
		while it != self.k_ and U:
			print("One Iteration !!!!")

			it += 1

			lst_x1_text = [X1_text[i] for i, x in enumerate(X1_text) if i in L]


			# self.func1(L)
			# lst_y_continuous = [Y_continuous[i] for i, x in enumerate(X1_text) if i in L]
			print(len(X1[L]), len(y[L]), len(lst_x1_text), len(L))
			# print("!!!!!!!!!!!!!!!!!!")
			self.fit_dl(self.clf1_, X1[L], Y_dl[L], lst_x1_text, y[L], kwargs)
			self.fit_dl(self.clf2_, X2[L], Y_dl[L], lst_x1_text, y[L], kwargs)



			# x_valid=kwargs["x_valid"], y_valid=kwargs["y_valid"],
			# y_valid_text=kwargs["y_valid_text"]


			y1 = self.clf1_.predict(X1[U_])[0]
			y2 = self.clf2_.predict(X2[U_])[0]

			# 保证是有序的字典，否则可能会在x-y匹配的时候出问题
			lst_each_class = collections.OrderedDict()
			for i in range(0, len(kwargs["labels"])):
				lst_each_class[i] = []
			# n, p = [], []



			for i, (y1_i, y2_i) in enumerate(zip(y1, y2)):
				#we added all that we needed to for this iteration, so break
				boo_is_break = True
				for item in lst_each_class:
					if len(lst_each_class[item]) != 2 * self.propotion_[kwargs["labels"][item]]:
						boo_is_break = False
						break
						# continue

				if boo_is_break == True:
					break


				# if len(p) == 2 * self.p_ and len(n) == 2 * self.n_:
				# 	break

				#update our newly 'labeled' samples.  Note that we are only 'labeling' a single sample
				#with each inner iteration.  We want to add 2p + 2n samples per outer iteration, but classifiers must agree

				# print(y1_i, y2_i)
				# print(lst_each_class[kwargs["labels"].index(y1_i)])
				# print(self.propotion_[y1_i])
				if y1_i == y2_i and len(lst_each_class[kwargs["labels"].index(y1_i)]) < self.propotion_[y1_i]:
					# print(str(i))
					lst_each_class[kwargs["labels"].index(y1_i)].append(i)

					print(X1_text[U_[i]], y1_i)
					# print(lst_each_class)

				# if y1_i == y2_i == 1 and len(p) < self.p_:
				# 	p.append(i)
				#
				# if y2_i == y1_i == 0 and len(n) < self.n_:
				# 	n.append(i)



			#label the samples and remove thes newly added samples from U_

			# item[1] = to_categorical(np.asarray(item[1]))

			num_to_add = 0
			for item in lst_each_class:
				# print(item)

				for x in lst_each_class[item]:
					# print(y[U_[x]])

					tmp = np.zeros(len(kwargs["labels"]))
					tmp[item] = 1

					Y_dl[U_[x]] = tmp
					y[U_[x]] = item
					# print(y[U_[x]])
					num_to_add += 1

				# y[[U_[x] for x in lst_each_class[item]]] = to_categorical(np.asarray([item]))


			# y[[U_[x] for x in p]] = 1
			# y[[U_[x] for x in n]] = 0

			for item in lst_each_class:
				# print(len(L))
				# L.extend([U_[x] for x in lst_each_class[item]])

				for x in lst_each_class[item]:
					L.extend([U_[x]])


				# print(len(L))
			# exit()
			# L.extend([U_[x] for x in p])
			# L.extend([U_[x] for x in n])


			#TODO: optimize these removals from U_
			#this is currently (2p + 2n)O(n)
			#and I think it can be reduced to O(n) rather easily
			# print(lst_each_class)
			lst_remove_index = []
			for item in lst_each_class:
				for element in lst_each_class[item]:
					lst_remove_index.append(element)

			lst_remove_index = sorted(lst_remove_index, reverse=True)

			# print(U_)
			# print(len(U_))
			for item in lst_remove_index:
				# print(item-1)
				U_.pop(item)

			# for i in p: U_.pop(i)
			# for i in n: U_.pop(i)

			#add new elements to U_
			add_counter = 0 #number we have added from U to U_
			# num_to_add = len(p) + len(n)
			while add_counter != num_to_add and U:
				add_counter += 1
				U_.append(U.pop())
			print("Augment " + str(num_to_add) + "samples from labeled samples.")

			#TODO: Handle the case where the classifiers fail to agree on any of the samples (i.e. both n and p are empty)

		#let's fit our final model
		lst_x1_text = [X1_text[i] for i, x in enumerate(X1_text) if i in L]
		# 深度学习模型
		self.fit_dl(self.clf1_, X1[L], Y_dl[L], lst_x1_text, y[L], kwargs)


		# if isinstance(self.clf1_, DeepLearningArchitecture):
		# 	clf, x, x_text, y, y_continuous
		#
		# 	self.fit_and_load_dl(self, self.clf1_, X1, kwargs["x_text"] y, kwargs)
		# else:
		# 	self.clf1_.fit(X1[L], y[L])

		self.fit_dl(self.clf2_, X2[L], Y_dl[L], lst_x1_text, y[L], kwargs)
		# if isinstance(self.clf2_, DeepLearningArchitecture):
		# 	self.fit_and_load_dl(self, self.clf2_, X1, y, kwargs)
		# else:
		# 	self.clf2_.fit(X2[L], y[L])


	#TODO: Move this outside of the class into a util file.
	def supports_proba(self, clf, x):
		"""Checks if a given classifier supports the 'predict_proba' method, given a single vector x"""
		# clf.predict_proba([x])
		try:
			clf.predict_proba([x])
			return True
		except:
			return False
	
	def predict(self, X1, X2, labels=[0, 1]):
		"""
		Predict the classes of the samples represented by the features in X1 and X2.

		Parameters:
		X1 - array-like (n_samples, n_features1)
		X2 - array-like (n_samples, n_features2)

		
		Output:
		y - array-like (n_samples)
			These are the predicted classes of each of the samples.  If the two classifiers, don't agree, we try
			to use predict_proba and take the classifier with the highest confidence and if predict_proba is not implemented, then we randomly
			assign either 0 or 1.  We hope to improve this in future releases.

		"""
		# print("clf1 is starting to predict.")
		y1 = self.clf1_.predict(X1)[0]
		# print("clf1 predicted.")
		# self.clf1_.predict_proba(X1)

		y2 = self.clf2_.predict(X2)[0]
		# self.clf2_.predict_proba(X2)



		proba_supported = self.supports_proba(self.clf1_, X1[0]) and self.supports_proba(self.clf2_, X2[0])

		#fill y_pred with -1 so we can identify the samples in which the classifiers failed to agree
		# y_pred = np.asarray([-1] * X1.shape[0])
		y_pred = [-1 for i in range(0, X1.shape[0])]



		for i, (y1_i, y2_i) in enumerate(zip(y1, y2)):
			if y1_i == y2_i:
				y_pred[i] = y1_i
			elif proba_supported:
				y1_probs = self.clf1_.predict_proba([X1[i]])[0]
				y2_probs = self.clf2_.predict_proba([X2[i]])[0]
				sum_y_probs = [prob1 + prob2 for (prob1, prob2) in zip(y1_probs, y2_probs)]
				max_sum_prob = max(sum_y_probs)
				y_pred[i] = labels[sum_y_probs.index(max_sum_prob)]

			else:
				#the classifiers disagree and don't support probability, so we guess
				y_pred[i] = random.sample(labels, 1)[0]
			
		#check that we did everything right
		assert not (-1 in y_pred)

		return y_pred


	def predict_proba(self, X1, X2):
		"""Predict the probability of the samples belonging to each class."""
		y_proba = np.full((X1.shape[0], 2), -1)

		y1_proba = self.clf1_.predict_proba(X1)
		y2_proba = self.clf2_.predict_proba(X2)

		for i, (y1_i_dist, y2_i_dist) in enumerate(zip(y1_proba, y2_proba)):
			y_proba[i][0] = (y1_i_dist[0] + y2_i_dist[0]) / 2
			y_proba[i][1] = (y1_i_dist[1] + y2_i_dist[1]) / 2

		_epsilon = 0.0001
		assert all(abs(sum(y_dist) - 1) <= _epsilon for y_dist in y_proba)
		return y_proba
