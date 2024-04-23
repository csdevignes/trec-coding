'''
This file contains methods for image processing before giving them to the neural network
Whether this is for training or for making predictions
'''
import numpy as np
import cv2 as cv


class Trainer:
    def __init__(self, data=None):
        if data is not None:
            self.pict = data
    def load_dataset(self, datapath):
        # Iterates into folder to load all data csv files
        self.full_da = np.ones(3412, 6233)
    def split_labels(self):
        # Split full dataset into pictures and labels dataset
        self.pict, self.label = np.split(self.full_da, [6232], axis = 1)
        self.pict = self.pict.reshape((len(self.pict), 76, 82))
    def redimension_pict(self):
        self.new_size = (56, 56)
        self.pict = self.pict.astype(np.float32)
        self.pict = self.pict.reshape(-1, self.pict.shape[1], self.pict.shape[2], 1)
        self.pict_redim = np.empty((len(self.pict), 56, 56))
        for i in range(len(self.pict)):
            img_resized = cv.resize(self.pict[i], self.new_size, interpolation=cv.INTER_AREA)
            self.pict_redim[i] = img_resized
        self.pict_redim = self.pict_redim / 255
