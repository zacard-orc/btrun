# -*- coding:utf-8 -*-
# 火币 米匡-K线，走TensorFlow
import  numpy

class TfDataSet(object):
    def __init__(self, x, y):

        assert x.shape[0] == y.shape[0], ("ERR：x.shape: %s y.shape: %s" % (x.shape, y.shape))
        self._num_examples = x.shape[0]
        # # Convert shape from [num examples, rows, columns, depth]
        # # to [num examples, rows*columns] (assuming depth == 1)
        # assert x.shape[3] == 1
        # x = x.reshape(x.shape[0],x.shape[1] * x.shape[2])
        # # Convert from [0, 255] -> [0.0, 1.0].
        # images = images.astype(numpy.float32)
        # images = numpy.multiply(images, 1.0 / 255.0)
        self._x = x
        self._y = y
        self._epochs_completed = 0
        self._index_in_epoch = 0

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def num_examples(self):
        return self._num_examples

    @property
    def epochs_completed(self):
        return self._epochs_completed

    def next_batch(self, batch_size):
        """Return the next `batch_size` examples from this data set."""

        start = self._index_in_epoch
        self._index_in_epoch += batch_size
        if self._index_in_epoch > self._num_examples:
            # Finished epoch
            self._epochs_completed += 1
            # Shuffle the data
            perm = numpy.arange(self._num_examples)
            numpy.random.shuffle(perm)
            self._x = self._x[perm]
            self._y = self._y[perm]
            # Start next epoch
            start = 0
            self._index_in_epoch = batch_size
            assert batch_size <= self._num_examples
        end = self._index_in_epoch
        return self._x[start:end], self._y[start:end]