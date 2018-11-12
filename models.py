# models.py
# Contains the network model class

import numpy as np
from meik.utils.losses import *
from meik.layers import Layer
from meik.metrics import Metrics
from meik.normalizers import Normalizer
from meik.layers import Dropout

class Sequential:
	
	def __init__(self):
		
		self.layers = []
		self.params = {
			'learning_rate': None,
			'epochs': None,
			'loss': None,
		}
		
		self.cost = []
		self.accuracy = []
		
	def add(self,layer):
		
		assert (issubclass(type(layer), Layer))
		
		_id = len(self.layers)
		if _id == 0:
			assert(type(layer.inputs) == int), "Provide number of inputs for initial layer"
			inputs = layer.inputs
		else:
			inputs = self.layers[-1].units
			
		layer.init(_id, inputs)
		self.layers.append(layer)
			
	def build(self, loss = None, normalization = 'none', learning_rate = 0.01, train_metrics = None, eval_metrics = None, thresholds = np.array([0.5])):
		
		self.params['loss'] = loss
		self.params['learning_rate'] = learning_rate
		self.params['normalization'] = normalization
		
		self.normalize = Normalizer(method = normalization)
		
		self.metrics = Metrics(loss = loss, train_metrics = train_metrics, eval_metrics = eval_metrics, thresholds = thresholds)

		# TO DO: proper optimizer objects passed to layer
		for i in range(len(self.layers)):
			self.layers[i].learning_rate = learning_rate

	def predict(self,X):
		
		layers = self.layers
		
		A = X
		for i in range(len(layers)):
			A = layers[i].predict(A)
		
		return A

	def forwardprop(self, X):

		layers = self.layers
		
		A = X
		for i in range(len(layers)):
			A = layers[i].forwardprop(A)
		
		return A

	def backprop(self, Y, A):
		
		layers = self.layers
		
		if self.params["loss"] in ['mse', 'binary_crossentropy', 'categorical_crossentropy']:
			dZ = A - Y
		elif self.params["loss"] == 'mae':
			dZ = np.sign(A - Y)
		dA = self.layers[-1].backprop_output(dZ)
		for i in range(len(layers)-2,-1,-1):
			dA = layers[i].backprop(dA)
	
	def update(self):

		layers = self.layers

		for i in range(len(layers)-1,-1,-1):
			layers[i].update()

	def regularization_loss(self, m):

		loss = 0.
		for l in self.layers:
			try:
				loss += l.regularizer.loss(l.W, m)
			except AttributeError:
				continue

		return loss
			
	def train(self, X, Y, epochs=1, verbose=1):

		m = Y.shape[1]
		
		layers = self.layers
		
		X_norm = self.normalize.train(X)
		
		for i in range(epochs):
			
			A = self.forwardprop(X_norm)
			self.backprop(Y, A)
			self.update()
			
			reg_loss = self.regularization_loss(m)
			cost = self.metrics.train(Y, A, reg_loss)
			self.cost.append(cost)
			
			if verbose == 1:
				self.metrics.train_print(i, epochs)
			
		print("------------ Final performance ------------\n")
		self.metrics.train_print(i, epochs)
		
	def evaluate(self, X, Y):

		m = Y.shape[1]
		
		X = self.normalize.evaluate(X)
			
		A = self.predict(X)
		
		reg_loss = self.regularization_loss(m)
		score = self.metrics.evaluate(Y, A, reg_loss)
		
		self.score = score
		
		return score
		