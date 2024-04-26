'''
Contains methods for detecting box on the scanned resultsheets (Boxdetection)
and extracting and plotting roi extracted from the sheet (Roiextract)
'''
import cv2 as cv
import numpy as np
import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt
import math
class Boxdetection:

    def __init__(self, image_path = "b3_09"):
        self.img = cv.imread(image_path)
    @st.cache_data
    def plot_scan(_self, image, lines = True):
        # Draw horizontal and vertical lines on a copy of the iamge, then returns it
        rows, cols, _ = image.shape
        img_lines = image.copy()
        if lines == True :
            cv.line(img_lines, (0, rows // 2), (cols, rows // 2), (0, 255, 0), 5)
            cv.line(img_lines, (cols // 2, 0), (cols // 2, rows), (0, 0, 255), 5)
        return img_lines
    def image_rotation(self, degree):
        # Rotate an image of a certain degree counterclockwise
        rows, cols, _ = self.img.shape
        M = cv.getRotationMatrix2D(((cols - 1) / 2.0, (rows - 1) / 2.0), degree, 1)
        self.img_rot = self.img.copy()
        self.img_rot = cv.warpAffine(self.img_rot, M, (cols, rows))
    def find_boxes(self, lower_threshold):
        gray = cv.cvtColor(self.img_rot, cv.COLOR_BGR2GRAY)
        _, thresh = cv.threshold(gray, lower_threshold, 250, cv.THRESH_BINARY_INV)
        contours, _ = cv.findContours(thresh, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
        self.box_coord = []
        for contour in contours:
            x, y, w, h = cv.boundingRect(contour)
            if(w>=90 and w<100):
                aspect_ratio = w/h
                if aspect_ratio <= 1.15:
                    self.box_coord.append((x, y, w, h))
        # Reorder box list to have top to bottom list
        self.box_coord = np.array(self.box_coord)
        self.box_coord = np.flip(self.box_coord, axis=0)
    def reorder_boxes(self):
        # To avoid little variations in the alignment, which will mess up the sort
        # We replace each line and each column of 20 by the mean y and mean x
        boxdf = pd.DataFrame(self.box_coord, columns=['x', 'y', 'w', 'h'])
        boxdf_sorted = boxdf.copy()
        # Sort the df on y, and replace y for the line of 20 by mean y
        boxdf_sorted = boxdf_sorted.sort_values(by='y', ignore_index=True)
        for i in range(0, 400, 20):
            boxdf_sorted.loc[i:i + 19, 'y'] = round(boxdf_sorted.loc[i:i + 19, 'y'].mean(), 0)
        # Sort the df on x, and replace x for the line of 20 by mean x
        boxdf_sorted = boxdf_sorted.sort_values(by='x', ignore_index=True)
        for j in range(0, 400, 20):
            boxdf_sorted.loc[j:j + 19, 'x'] = round(boxdf_sorted.loc[j:j + 19, 'x'].mean(), 0)
        # We want boxes in order : left -> right (x asc), top -> bottom (y asc)
        boxdf_sorted = boxdf_sorted.sort_values(by=['y', 'x'], ignore_index=True)
        self.box_coord = boxdf_sorted.to_numpy()
    def extract_boxes(self):
        max_box_detected = 0
        lower_TSt = 0
        while (max_box_detected) != 400 and (lower_TSt <= 255):
            lower_TSt += 1
            self.find_boxes(lower_TSt)
            max_box_detected = len(self.box_coord)
        self.reorder_boxes()
    def plot_boxes(self, coord):
        img_box = self.img_rot.copy()
        if coord.ndim > 1:
            for gbox in coord:
                x, y, w, h = gbox
                cv.rectangle(img_box, (x, y), (x + w, y + h), (0, 255, 0), 2)
        else:  # If giving only one box to the function
            x, y, w, h = coord
            cv.rectangle(img_box, (x, y), (x + w, y + h), (0, 255, 0), 2)
        return img_box

class ROIExtract:
    def __init__(self, image_rot):
        self.img = image_rot
        intervals = [(20, 40), (60, 80), (100, 120), (140, 160), (180, 200), (220, 240), (260, 280), (300, 320),
                     (340, 360), (380, 400)]
        self.symbols_index = np.concatenate([np.arange(start, end, 1) for start, end in intervals])
        self.all_index = np.arange(0, 400, 1)
        self.number_index = np.setdiff1d(self.all_index, self.symbols_index)
        self.width = 87
        self.height = 80
        self.set_labels()
    def extract_roi_inside_box(self, coord):
        gray = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)
        x, y, w, h = coord
        roi = gray[y + 4:y + self.height, x + 5:x + self.width]
        return roi
    def extract_roi_symbols(self, coord_list):
        self.roi_symbols = []
        for coord in coord_list[self.symbols_index]:
            roi_img = self.extract_roi_inside_box(coord)
            self.roi_symbols.append(roi_img)
        self.roi_symbols = np.array(self.roi_symbols)
    def extract_roi_all(self, coord_list):
        self.roi_all = []
        for coord in coord_list:
            roi_img = self.extract_roi_inside_box(coord)
            self.roi_all.append(roi_img)
        self.roi_all = np.array(self.roi_all)
    def set_labels(self):
        self.blank_labels = np.ones(200, dtype=int)
        self.true_labels = np.array([3, 6, 4, 2, 9, 8, 7, 9, 1, 6, 3, 7, 6, 2, 5, 8, 4, 1, 9, 5,
                        2, 9, 6, 8, 1, 7, 5, 3, 4, 7, 2, 5, 3, 1, 9, 6, 7, 8, 2, 4,
                        6, 3, 7, 9, 5, 4, 8, 1, 2, 9, 8, 4, 1, 8, 7, 5, 9, 2, 6, 3,
                        1, 8, 5, 2, 4, 3, 9, 6, 7, 1, 5, 6, 7, 5, 1, 3, 4, 9, 8, 2,
                        9, 7, 4, 6, 8, 2, 1, 5, 3, 2, 9, 8, 4, 3, 6, 7, 2, 5, 9, 1,
                        4, 6, 1, 5, 3, 9, 2, 7, 8, 5, 6, 3, 9, 4, 5, 2, 6, 7, 1, 8,
                        5, 2, 8, 1, 7, 6, 3, 4, 9, 8, 1, 2, 6, 9, 8, 1, 5, 3, 4, 7,
                        3, 5, 2, 4, 9, 1, 7, 8, 6, 4, 3, 1, 8, 7, 2, 4, 3, 6, 5, 9,
                        7, 1, 9, 3, 6, 8, 4, 2, 5, 6, 7, 9, 2, 6, 3, 8, 1, 4, 7, 5,
                        8, 4, 3, 7, 2, 5, 6, 9, 1, 3, 4, 7, 5, 2, 4, 9, 8, 1, 3, 6])

if __name__ == "__main__":
    image_file = "Test2.png"
    image_path = f"scan_resultsheets/{image_file}"
    print(image_path)
    b = Boxdetection(image_path)
    b.image_rotation(0.3)
    b.extract_boxes()
    print(b.box_coord.shape)
