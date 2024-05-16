'''
This file contains methods to evaluate predictions
and to correct the scanned resultsheets
'''
import keras
import matplotlib.pyplot as plt
import numpy as np
import cv2 as cv
import pandas as pd
import streamlit as st
from sklearn.metrics import confusion_matrix
import seaborn as sns


class Evaluator:
    def __init__(self, picts):
        self.X = picts
        self.labels = {}
        self.update_labels()
    def predict(self, modelpath = "models/DNN_alldata_Epoch30_20240516.keras"):
        model = keras.models.load_model(modelpath)
        self.y_predicted = model.predict(self.X)
        self.labels["predicted_labels"] = np.array([int(np.argmax(i) + 1) if max(i) > 0.7 else 0 for i in self.y_predicted])
        st.session_state["predicted_labels"] = self.labels["predicted_labels"]
    def plot_results(self, image, labels, boxes):
        image_copy = image.copy()
        for i, gbox in enumerate(boxes):
            x, y, w, h = gbox
            if (labels[i] == 0):
                cv.rectangle(image_copy, (x, y), (x + w, y + h), (255, 0, 0), 3)
            elif (labels[i] == self.labels["sheet_labels"][i]):
                cv.rectangle(image_copy, (x, y), (x + w, y + h), (0, 255, 0), 3)
            else:
                cv.rectangle(image_copy, (x, y), (x + w, y + h), (0, 0, 255), 3)
        return image_copy
    def update_labels(self):
        for item in st.session_state.keys():
            if item.endswith('labels'):
                self.labels[item] = st.session_state[item]
    def truncate(self, n):
        return int(n * 100) / 100
    def correction(self, correct_labels, test_labels):
        self.erreurs = [i for i, l in enumerate(correct_labels) if l != test_labels[i]]
        self.nb_erreurs = len(self.erreurs)
        self.cm = confusion_matrix(correct_labels, test_labels)
        self.recall = [self.truncate(self.cm[i, i] / self.cm[i, :].sum()) for i in range(0,10)]
        self.accuracy = [self.truncate(self.cm[i, i]/self.cm[:, i].sum()) for i in range(0,10)]
        FP_error = np.array([self.cm[0, i] for i in range(1, 10)])
        FN_error = np.array([self.cm[i, 0] for i in range(1, 10)])
        # /!\ delete uses the index in the np.arange(1,10) not from the self.cm, which is where the i-1 comes from
        FP_symbol = np.array([self.cm[np.delete(np.arange(1, 10), i - 1), i].sum() for i in range(1, 10)])
        FN_symbol = np.array([self.cm[i, np.delete(np.arange(1, 10), i - 1)].sum() for i in range(1, 10)])
        FP_total = FP_error + FP_symbol
        FN_total = FN_error + FN_symbol
        self.custom_metrics = np.vstack((FP_error, FP_symbol, FP_total, FN_error, FN_symbol, FN_total))
        self.metrics_n = self.custom_metrics / self.cm.sum() * 100
    def cm_plot(self):
        plt.clf()
        sns.heatmap(self.cm, annot=True, fmt='d')
        plt.xlabel('Detected')
        plt.ylabel('True')
        return plt
    def metrics_df(self):
        df = pd.DataFrame({'Accuracy': self.accuracy, 'Recall': self.recall},
                          index=range(0, 10))
        return df.transpose()
    def metrics_plot(self):

        plt.clf()
        heatmap = sns.heatmap(self.metrics_n, annot=True)
        cbar = heatmap.collections[0].colorbar
        cbar.set_label('% total symbols', rotation=270, labelpad=20)
        heatmap.set_xticklabels(range(1, 10))
        heatmap.set_yticklabels(["FP_error", "FP_symbol", "FP_total", "FN_error", "FN_symbol", "FN_total"], rotation=0)
        return plt

