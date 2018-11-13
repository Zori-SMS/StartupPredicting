import numpy as np
from config import Config
import sklearn.model_selection

class DataLoader:
    def __init__(self, X_path, Y_path, config):
        self._X = np.load(X_path)
        self._Y = np.load(Y_path)
        self.max_length = config.max_length
        self.batch_size = config.batch_size

        # create random sequnces first, and then sample from it
        self.positive_startpoints = []
        for i in range(self._Y.shape[0]):
            for j in range(self._Y.shape[1] - self.max_length):
                if self._Y[i, j+self.max_length] > 0:
                    self.positive_startpoints.append((i, j))
        # print(np.sum(self._Y, axis=0))
        # print(len(self.positive_startpoints))
        q = 10
        num_pos = len(self.positive_startpoints)
        num_rand = q*num_pos

        list_X = [self._X[pair[0], pair[1]:pair[1]+self.max_length] for pair in self.positive_startpoints]
        list_Y = [self._Y[pair[0], pair[1]+self.max_length] for pair in self.positive_startpoints]

        rand_start_row = np.random.randint(self._Y.shape[0], size=num_rand)
        rand_start_col = np.random.randint(self._Y.shape[1] - self.max_length, size=num_rand)
        
        rand_start_points = np.stack([rand_start_row, rand_start_col]).transpose()
        rand_list_X = [ self._X[list(pair)[0], list(pair)[1]:list(pair)[1]+self.max_length] for pair in rand_start_points]
        rand_list_Y = [ self._Y[list(pair)[0], list(pair)[1] + self.max_length] for pair in rand_start_points]

        list_X.extend(rand_list_X)
        list_Y.extend(rand_list_Y)

        self._sequence_X = np.stack(list_X)
        self._sequence_Y = np.stack(list_Y)

        self.X_train, self.X_test, self.y_train, self.y_test = sklearn.model_selection.train_test_split(self._sequence_X, self._sequence_Y)

        

    def get_X(self):
        return self._X

    def get_Y(self):
        return self._Y

    def get_batch_random(self):
        # this is not going to work, the y_batch is most likely to be zero
        row_ids = np.random.randint(self._X.shape[0], size=self.batch_size)
        time_start = np.random.randint(self._X.shape[1] - self.max_length)
        X_batch = self._X[row_ids, time_start:time_start+self.max_length]
        y_batch = self._Y[row_ids, time_start+self.max_length]
        return X_batch.shape, y_batch.shape, np.sum(y_batch)

    def get_batch(self):
        # this batch is to get sequnces from the sample table
        ids = np.random.randint( self._sequence_X.shape[0], size=self.batch_size)
        Xs = self._sequence_X[ids]
        ys = self._sequence_Y[ids]
        return Xs, ys

    def get_batch_train(self):
        ids = np.random.randint( self.X_train.shape[0], size=self.batch_size)
        Xs = self.X_train[ids]
        ys = self.y_train[ids]
        return Xs, ys


    def get_batch_test(self):
        ids = np.random.randint( self.X_test.shape[0], size=self.batch_size)
        Xs = self.X_test[ids]
        ys = self.y_test[ids]
        return Xs, ys


# unit test
if __name__ == "__main__":
    conf = Config()
    X = "../data/X.npy"
    Y = "../data/Y.npy"
    d = DataLoader(X, Y, conf)
