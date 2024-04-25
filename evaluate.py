'''
This file contains methods to evaluate predictions
and to correct the scanned resultsheets
'''
import keras
import numpy as np
import cv2 as cv


class Evaluator:
    def __init__(self, picts, labels):
        self.X_test = picts
        self.y_test = labels
    def predictions(self, modelpath = "model_CS_new9BC_Epoch90_20240423.keras"):
        model = keras.models.load_model(modelpath)
        self.y_predicted = model.predict(self.X_test)
        self.y_predicted_labels = [int(np.argmax(i) + 1) if max(i) > 0.7 else 0 for i in self.y_predicted]

    def plot_results(self, image, boxes):
        image_copy = image.copy()
        for i, gbox in enumerate(boxes):
            x, y, w, h = gbox
            if (self.y_predicted_labels[i] == 0):
                cv.rectangle(image_copy, (x, y), (x + w, y + h), (255, 0, 0), 3)
            elif (self.y_predicted_labels[i] == self.y_test[i]):
                cv.rectangle(image_copy, (x, y), (x + w, y + h), (0, 255, 0), 3)
            else:
                cv.rectangle(image_copy, (x, y), (x + w, y + h), (0, 0, 255), 3)
        return image_copy
    def update_true_labels(self, newtarget):
        self.y_test = newtarget
    def update_manual_labels(self, manual_labels):
        self.manual_labels = manual_labels
    def correction(self):
        self.erreurs = set(self.manual_labels) - set(self.y_test)
        self.nb_erreurs = len(self.erreurs)