from model import Model
from model import get_batch
from model import Config
import tensorflow as tf 



class Trainer:
	def __init__(self, model, data, config, sess):
		self.model = model
		self.config = config
		self.data = data

	def train(self):
		pass

	def test(self):
		pass

	def save(self):
		pass

	def load(self):
		pass




if __name__ == "__main__":
	data = None

	config = Config()
	with tf.Session as sess:
		model = Model(config)
		trainer = Trainer(model, config, data, sess)

		



