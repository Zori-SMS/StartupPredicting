import tensorflow as tf
import numpy as np


# this is the mock get_batch function
def get_batch():
	batch_size = 128
	max_length = 32
	input_size = 20

	# try to generate the sequences that are increasing or decreasing
	x = np.random.rand(batch_size, max_length, input_size)
	y = np.mean(x, axis=2) > 0.5

	return x, y


class Model:
	def __init__(self, config):
		self.batch_size = config.batch_size
		self.input_size = config.input_size
		self.hidden_size = config.hidden_size

		self.Xs = tf.placeholder(tf.float32, shape=(batch_size, None, input_size))
		self.isTraining = tf.placeholder(tf.bool)
		self.Ys = tf.placeholder(tf.int32, shape=(batch_size, None))

		with tf.variable_scope("model", reuse=tf.AUTO_REUSE):
			cell = tf.nn.rnn_cell.GRUCell()
			initial_state = cell.zero_state(self.batch_size, dtype=tf.float32)

			self.rnn_outputs, state = tf.nn.dynamic_rnn(cell, input_data, initial_state=initial_state, dtype=tf.float32)

			self.add_fully_connected_layers()
			self.add_loss()
			self.add_optimizer()

	def add_fully_connected_layers(self):
		reshaped_rnn_outputs = tf.reshape(self.rnn_outputs, [-1, self.hidden_size])
		# [batch_size * max_length, hidden_size]
		hidden_layer = tf.layers.dense(reshaped_rnn_outputs, self.hidden_size / 2, tf.nn.relu)
		# [batch_size * max_length, 2]
		self.reshaped_scores = tf.layers.dense(reshaped_rnn_outputs, 2)

	def add_prediction(self):
		pass

	def add_loss(self):
		self.loss = tf.reduce_mean( tf.nn.sparse_softmax_cross_entropy_with_logits(labels=self.Ys, logits=self.reshaped_scores))

	def add_optimizer(self): 
        optimizer = tf.train.AdamOptimizer(0.001)
        self.optimize = optimizer.minimize(self.loss)

	def save_model(self):
		pass


class Config:
	def __init__(self):
		self.batch_size = 300


if __name__ == "__main__":
	get_batch()
