'''
Contains methods to evaluate predictions and to correct the scanned resultsheets
'''

from keras import saving
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.metrics import confusion_matrix, accuracy_score
import seaborn as sns


class Evaluator:
    '''
    Make label prediction using given array of images and given model. Calculates and display correction score,
    confusion matrix, metrics.
    '''
    def __init__(self, picts, labels = None):
        '''
        :param picts: array (X, height, width) of pictures
        :param labels: array (X,) of labels, optional
        '''
        self.X = picts
        self.labels = {}
        if labels is None:
            self.update_labels()
        else:
            self.labels['train_labels'] = labels
        self.detect_empty()
    def detect_empty(self):
        '''
        Detect empty boxes among picture array, results in a boolean mask
        '''
        self.fill_mask = self.X.reshape((len(self.X), 28*28)).std(axis=1) > 0.02
    def predict(self, modelpath = "models/CNN_10-0.996_20240611_t2.keras"):
        '''
        Predict y from X given in initialization, then infer labels from predictions by taking
        the highest probability class from y_predicted, if the probability is > 0.7. Otherwise it
        is considered as not reliable prediction and affected to class 0 (error).
        :param modelpath: str, path to model to use for prediction
        '''
        model = saving.load_model(modelpath)
        self.y_predicted = model.predict(self.X)
        self.labels["predicted_labels"] = np.array([int(np.argmax(i) + 1) if max(i) > 0.7 else 0 for i in self.y_predicted])
        return self.labels["predicted_labels"]
    def update_labels(self):
        '''
        Update labels present in the object depending on session state labels. Useful in case of
        page rerun, or if no label is given in object initialisation. Labels is a dict, similar to session state.
        '''
        for item in st.session_state.keys():
            if item.endswith('labels'):
                self.labels[item] = st.session_state[item].copy()
    def correction(self, correct_labels, test_labels, keeper_mask):
        '''
        Calculate number of errors depending on given correct labels and test labels
        (from prediction or correction). Compute the confusion matrix and accuracy based on these labels.
        :param correct_labels: array (X,) used as true labels
        :param test_labels: array (X,) used as predicted labels
        :param keeper_mask: boolean array (X,) used to filter labels
        '''
        mask = [True if f and k else False for f,k in zip(self.fill_mask, keeper_mask)]
        c_lab = correct_labels[mask]
        t_lab = test_labels[mask]
        self.erreurs = [i for i, l in enumerate(c_lab) if l != t_lab[i]]
        self.nb_erreurs = len(self.erreurs)
        self.cm = confusion_matrix(c_lab, t_lab)
        self.cm = np.array(self.cm)
        self.g_accuracy = accuracy_score(c_lab, t_lab)
        self.g_error = 1-self.g_accuracy
        self.result = f"Cases remplies : {self.fill_mask.sum()}, Nombre d'erreurs : {self.nb_erreurs}, Score : {self.fill_mask.sum() - self.nb_erreurs}"
    def metrics_calculation(self):
        '''
        Calculate a number of metrics from the confusion matrix. Recall per class as TP/TP+FN
        Precision per class as TP/TP+FP. Custom metrics are per class :
        - FP_error : labelled as class but are truly errors
        - FN_error : labelled as error but are truly class
        - FP_symbol : labelled as class but are truly another symbol
        - FN_symbol : labelled as another symbol but are truly class
        Custom metrics are stacked in a matrix and normalized on total number of test samples.
        '''
        self.recall = [self.cm[i, i] / self.cm[i, :].sum() for i in range(0,10)]
        self.precision = [self.cm[i, i]/self.cm[:, i].sum() for i in range(0,10)]
        FP_error = np.array([self.cm[0, i] for i in range(1, 10)])
        FN_error = np.array([self.cm[i, 0] for i in range(1, 10)])
        # delete uses the index in the np.arange(1,10) not from the self.cm, which is where the i-1 comes from
        FP_symbol = np.array([self.cm[np.delete(np.arange(1, 10), i - 1), i].sum() for i in range(1, 10)])
        FN_symbol = np.array([self.cm[i, np.delete(np.arange(1, 10), i - 1)].sum() for i in range(1, 10)])
        FP_total = FP_error + FP_symbol
        FN_total = FN_error + FN_symbol
        self.custom_metrics = np.vstack((FP_error, FP_symbol, FP_total, FN_error, FN_symbol, FN_total))
        self.metrics_n = self.custom_metrics / self.cm.sum() * 100
        total = self.metrics_n.sum(axis=1)
        self.TFP = total[2]
        self.TFN = total[5]
    def cm_plot(self):
        '''
        Plot the confusion matrix
        :return plt: matplotlib.pyplot
        '''
        plt.clf()
        sns.heatmap(self.cm, annot=True, fmt='d')
        plt.xlabel('Detected')
        plt.ylabel('True')
        return plt
    def metrics_df(self):
        '''
        Creates a df with per class precision and recall
        :return df.transpose(): pandas Dataframe
        '''
        df = pd.DataFrame({'Precision': self.precision, 'Recall': self.recall},
                          index=range(0, 10))
        return df.transpose()
    def metrics_plot(self):
        '''
        Plot custom metrics
        :return plt: matplotlib.pyplot
        '''
        plt.clf()
        heatmap = sns.heatmap(self.metrics_n, annot=True)
        cbar = heatmap.collections[0].colorbar
        cbar.set_label('% total symbols', rotation=270, labelpad=20)
        heatmap.set_xticklabels(range(1, 10))
        heatmap.set_yticklabels(["FP_error", "FP_symbol", "FP_total", "FN_error", "FN_symbol", "FN_total"], rotation=0)
        return plt

