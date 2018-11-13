import tensorflow as tf
import numpy as np
from tqdm import tqdm
from config import Config
from data import DataLoader

class Model:
	def __init__(self, config):
		self.batch_size = config.batch_size
		self.input_size = config.input_size
		self.hidden_size = config.hidden_size
		self.max_length = config.max_length

		batch_size = self.batch_size
		input_size = self.input_size
		hidden_size = self.hidden_size


		self.Xs = tf.placeholder(tf.float32, shape=(batch_size, None, input_size))
		self.isTraining = tf.placeholder(tf.bool)
		self.Ys = tf.placeholder(tf.float32, shape=batch_size)

		with tf.variable_scope("model", reuse=tf.AUTO_REUSE):
			cell = tf.nn.rnn_cell.GRUCell(hidden_size)
			initial_state = cell.zero_state(self.batch_size, dtype=tf.float32)

			# [batch_size, max_length, hidden_size]
			self.rnn_outputs, state = tf.nn.dynamic_rnn(cell, self.Xs, initial_state=initial_state, dtype=tf.float32)

			self.add_fully_connected_layers()
			self.add_prediction()
			self.add_loss()
			self.add_optimizer()
			# self.add_F1()

	def add_fully_connected_layers(self):
		reshaped_rnn_outputs = tf.reshape(self.rnn_outputs, [-1, self.hidden_size])
		# [batch_size * max_length, hidden_size]
		hidden_layer = tf.layers.dense(reshaped_rnn_outputs, self.hidden_size / 2, tf.nn.relu)
		# [batch_size * max_length]
		self.reshaped_scores = tf.layers.dense(reshaped_rnn_outputs, 1)

	def add_prediction(self):
		# [batch_size]
		self.predict = tf.reshape(self.reshaped_scores, [self.batch_size, self.max_length])[:, -1]

	def add_loss(self):
		self.loss = tf.reduce_mean( tf.nn.sigmoid_cross_entropy_with_logits(labels=self.Ys, logits=self.predict))

	def add_optimizer(self): 
		optimizer = tf.train.AdamOptimizer(0.001)
		self.optimize = optimizer.minimize(self.loss)

	def add_F1(self):
		self.F1 = tf.contrib.metrics.f1_score(self.Ys, self.predict)

	def save_model(self):
		pass





if __name__ == "__main__":
	config = Config()

	X = "../data/X.npy"
	Y = "../data/Y.npy"
	d = DataLoader(X, Y, config)

	model = Model(config)
	num_epochs = 4
	num_batchs = 100

	with tf.Session() as sess:
		sess.run(tf.global_variables_initializer())
		print("Initialized")

		for epoch in range(num_epochs):
			print("Training Epoch " + str(epoch))
			process_bar = tqdm(range(num_batchs))
			for i in process_bar:
				Xs, ys = d.get_batch_train()
				feed_dict = { model.Xs: Xs, model.Ys: ys }
				loss, _ = sess.run([model.loss, model.optimize], feed_dict=feed_dict)

				process_bar.set_description("Loss: %0.4f" % loss)

			print("Testing Epoch " + str(epoch))

			Xs, ys = d.get_batch_test()
			feed_dict = { model.Xs: Xs, model.Ys: ys }
			loss = sess.run([model.loss], feed_dict=feed_dict)
			print("test_loss", loss)








	
		
