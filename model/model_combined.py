import tensorflow as tf
import numpy as np
from tqdm import tqdm
from config import Config
from data_combined import DataLoaderCombined 
from model import Model

class ModelCombined(Model):
	def __init__(self,config):
		self.static_size = config.static_size
		batch_size = config.batch_size
		input_size = config.input_size
		hidden_size = config.hidden_size
		static_size = config.static_size
		self.X_static = tf.placeholder(tf.float32, shape=(batch_size, static_size))
		Model.__init__(self, config)

	def add_fully_connected_layers(self):
		max_length = self.max_length
		reshaped_rnn_outputs = tf.reshape(self.rnn_outputs, [-1, self.hidden_size])
		print(self.X_static.get_shape())
		
		repeated_x_static = tf.tile(self.X_static, [max_length, 1])
		print(repeated_x_static.get_shape())
		concatenated_rnn_outputs = tf.concat([reshaped_rnn_outputs, repeated_x_static], 1)
		print(concatenated_rnn_outputs.get_shape())

		# [batch_size * max_length, hidden_size]
		hidden_layer = tf.layers.dense(concatenated_rnn_outputs, (self.hidden_size+self.static_size) / 2, tf.nn.relu)
		# [batch_size * max_length]
		self.reshaped_scores = tf.layers.dense(hidden_layer, 1)
		print("size")
		print(self.reshaped_scores )

if __name__ == "__main__":
	config = Config()

	X = "../data/X.npy"
	Y = "../data/Y.npy"
	X_static = "../data/X_static.npy"
	d = DataLoaderCombined(X, Y, config, X_static)

	model = ModelCombined(config)
	num_epochs = 4
	num_batchs = 100

	with tf.Session() as sess:
		sess.run(tf.global_variables_initializer())
		print("Initialized")

		for epoch in range(num_epochs):
			print("Training Epoch " + str(epoch))
			process_bar = tqdm(range(num_batchs))
			for i in process_bar:
				Xs, ys, s = d.get_batch_train()
				feed_dict = { model.Xs: Xs, model.Ys: ys, model.X_static: s}
				loss, _ = sess.run([model.loss, model.optimize], feed_dict=feed_dict)

				process_bar.set_description("Loss: %0.4f" % loss)

			print("Testing Epoch " + str(epoch))

			Xs, ys, s = d.get_batch_test()
			feed_dict = { model.Xs: Xs, model.Ys: ys, model.X_static: s}
			loss = sess.run([model.loss], feed_dict=feed_dict)
			print("test_loss", loss)