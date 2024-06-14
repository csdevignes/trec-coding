'''
This file contains methods for image processing before giving them to the neural network
Whether this is for training or for making predictions
'''
import math
import os

import numpy as np
import cv2 as cv
import pandas as pd
from matplotlib import pyplot as plt


class Dataset:
    '''
    Put together the dataset and saves it in a csv file.
    '''
    def __init__(self, img, label):
        self.pict = img
        self.label = label
        self.combine_data()
    def combine_data(self):
        pict_2d = self.pict.reshape(len(self.pict), -1)
        self.dataset = np.concatenate((pict_2d, self.label[:, np.newaxis]), axis=1)
    def convert_csv(self):
        self.df = pd.DataFrame(self.dataset)
        return self.df.to_csv(index=False, header=False).encode('utf-8')
    def save_csv(self, imagefile):
        '''
        Saves the dataset as .csv
        :param imagefile: string, original name of the analyzed scanned image
        '''
        file_name = imagefile.split('.')[0]
        np.savetxt(f'data_resultsheets/{file_name}.csv', self.dataset, fmt='%d', delimiter=',')

class Trainer:
    '''
    Loads dataset and prepares it for use by the neural network.
    '''
    def __init__(self, pict=None, data = None, datapath = None, removezeros = False, ext_w=76, ext_h=82):
        '''
        Several data source can be used :
        :param pict: array of pictures (X, width, height) (labels provided separately)
        :param data: array of pictures (X, width*height+label) with labels (as the last column)
        :param datapath: string, path to folder containing .csv with data arrays (of picture + labels)
        :param removezeros: boolean, state if zero labelled pictures should be removed from dataset
        :param ext_w: int, original width of the image in pixel
        :param ext_h: int, original height of the image in pixel
        '''
        if pict is not None:
            self.pict = pict
        elif data is not None:
            self.full_da = data
            self.split_labels(ext_w, ext_h)
        elif datapath is not None:
            self.load_dataset(datapath)
            self.split_labels(ext_w, ext_h)
        self.redimension_pict()
        if removezeros:
            self.remove_zero()
    def load_dataset(self, datapath):
        '''
        Used when loading datasets from a folder. Iterated through .csv files and add them to the full_da array.
        :param datapath: string, path to folder containing .csv with data arrays (of picture + labels)
        '''
        self.full_da = None
        for filename in os.listdir(datapath):
            if filename.endswith('.csv'):
                if self.full_da is None:
                    self.full_da = np.loadtxt(f'{datapath}{filename}', dtype="int32", delimiter=',')
                else:
                    da = np.loadtxt(f'{datapath}{filename}', dtype="int32", delimiter=',')
                    self.full_da = np.append(self.full_da, da, axis=0)
            else:
                continue
    def split_labels(self, ext_w, ext_h):
        '''
        Used when loading a saved dataset (pict + label). Split pict and label from full dataset,
        reshape both arrays according to width and height of pictures.
        :param ext_w: int, original width of the image in pixel
        :param ext_h: int, original height of the image in pixel
        '''
        self.pict, self.label = np.split(self.full_da, [ext_w*ext_h], axis = 1)
        self.label = self.label.reshape((len(self.label),)).astype(np.int32)
        self.pict = self.pict.reshape((len(self.pict), ext_w, ext_h))
    def redimension_pict(self, size=(28, 28)):
        '''
        Redimension pict into appropriate size for the neural network.
        Performs min/max normalization.
        :param size: (int, int) size of redimensionned pictures
        '''
        self.size = size
        self.pict = self.pict.astype(np.float32)
        self.pict_redim = np.empty((len(self.pict), self.size[0], self.size[1]))
        for i in range(len(self.pict)):
            img_resized = cv.resize(self.pict[i], self.size, interpolation=cv.INTER_AREA)
            self.pict_redim[i] = img_resized
        self.pict_redim = self.pict_redim / 255
    def remove_zero(self):
        '''
        When dataset has no zeros class (errors) in it : this will not change anything
        When dataset has zeros class: this will create label and pict_redim without the zeros,
        and label_zeros and pict_zeros with the zeros.
        '''
        keeper_i = np.where(self.full_da[:, -1] != 0)[0]
        self.label_zeros = self.label
        self.pict_zeros = self.pict_redim
        self.label = self.label[keeper_i]
        self.pict_redim = self.pict_redim[keeper_i, :, :]

    def plot_mpi(self):
        '''
        Plot mean pixel intensity using full dataset (not redimensionned)
        '''
        mean_pix = self.full_da[:, :-1].mean(axis=1)
        labels = self.full_da[:, -1]
        jitter = np.random.normal(0, 0.1, size=len(labels))
        plt.plot(labels + jitter, mean_pix, 'o')
        plt.xlabel('Labels')
        plt.ylabel('Moyenne')
        plt.show()

    def visualize_symbols(self, labels, imgperrow=12):
        '''
        Visualize all symbols from pict_redim (can take time with big datasets)
        Symbols are sorted per label.
        :param labels: array (len(pict_redim),) of labels
        :param imgperrow: int, number of symbols per row
        '''
        for l in np.unique(labels):
            label_mask = (labels == l)
            img_indices = np.where(label_mask)[0]

            n_rows = math.ceil(len(self.pict_redim[img_indices]) / imgperrow)
            fig, axs = plt.subplots(n_rows, imgperrow, figsize=(imgperrow, n_rows))

            for i, pixels in enumerate(self.pict_redim[img_indices]):
                row = i // imgperrow
                col = i % imgperrow
                ax = axs[row, col]
                ax.imshow(pixels, cmap='gray')
                ax.text(0.5, 1.02, str(img_indices[i]), transform=ax.transAxes, ha='center', va='bottom', fontsize=10)
                ax.axis('off')
            fig.suptitle(f'Label {l}', fontsize=16)
            fig.subplots_adjust(top=0.75)
            plt.show()

    def visualize_random_samples(self, pict, y = None, num_samples=5):
        '''
        Visualize random symbols from an array
        :param pict: array (X, height, width) of symbols
        :param y: array (X,) of labels
        :param num_samples: int, number of samples to plot
        '''
        sample_indices = np.random.choice(len(pict), num_samples, replace=False)
        fig, axes = plt.subplots(1, num_samples, figsize=(12, 3))
        for i, idx in enumerate(sample_indices):
            axes[i].imshow(pict[idx], cmap='gray')
            if y is not None:
                axes[i].set_title(f"Label: {y[idx]}")
            axes[i].axis('off')
        plt.tight_layout()
        plt.show()

