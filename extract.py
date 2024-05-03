'''
Contains methods for detecting boxes coordinates on the scanned resultsheets (Boxdetection)
and extracting and plotting roi extracted from the sheet (ROIExtract)
'''

import cv2 as cv
import numpy as np
import pandas as pd
import streamlit as st

class Boxdetection:
    '''
    Contains all the method to load scanned image file, display grid on it,
    Perform image rotation, box detection and coordinates storage, box display
    on scanned image.
    '''

    def __init__(self, image_file):
        '''
        When using with streamlit file uploader, use cv.imdecode line
        When using with local file, use cv.imread together with image path
        (also modify in __init__)
        :param image_path: directory path to image file
        :param image_file: image file loaded from another method
        '''
        #self.img = cv.imread(image_path)
        self.img = cv.imdecode(image_file, cv.IMREAD_COLOR)
    @st.cache_data
    def plot_scan(_self, image, grid = [5, 4]):
        '''
        Draw horizontal and vertical lines on a copy of the image, then returns it
        :param image: image to plot on
        :param grid: number of [rows, cols] in the grid. Pass None to remove the grid
        :return: image copy with lines plotted on
        '''
        h, w, _ = image.shape
        img_lines = image.copy()
        if grid is not None :
            rows, cols = grid
            dy, dx = h / rows, w / cols
            for x in np.linspace(start=dx, stop=w-dx, num=cols-1): # vertical
                x = int(round(x))
                cv.line(img_lines, (x, 0), (x, h), color=(0, 255, 0), thickness=3)
            for y in np.linspace(start=dy, stop=h - dy, num=rows - 1): # horizontal
                y = int(round(y))
                cv.line(img_lines, (0, y), (w, y), color=(255, 0, 0), thickness=3)
        return img_lines
    def image_rotation(self, degree):
        '''
        Rotates an image of a certain degree counterclockwise
        :param degree: float
        '''
        rows, cols, _ = self.img.shape
        M = cv.getRotationMatrix2D(((cols - 1) / 2.0, (rows - 1) / 2.0), degree, 1)
        self.img_rot = self.img.copy()
        self.img_rot = cv.warpAffine(self.img_rot, M, (cols, rows))
        self.gray = cv.cvtColor(self.img_rot, cv.COLOR_BGR2GRAY)
    def find_boxes(self, lower_threshold):
        '''
        Run findcontour with a given threshold for binary image, then loops
        into the contours to keep only the ones corresponding to the right size
        and aspect ratio for the boxes.
        :param lower_threshold: int between 0 and 255
        '''
        _, thresh = cv.threshold(self.gray, lower_threshold, 250, cv.THRESH_BINARY_INV)
        contours, _ = cv.findContours(thresh, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
        self.box_coord = []
        for contour in contours:
            x, y, w, h = cv.boundingRect(contour)
            if(w>=90 and w<100):
                aspect_ratio = w/h
                if aspect_ratio <= 1.15:
                    self.box_coord.append((x, y, w, h))
    def align_boxes(self):
        '''
        Align boxes horizontally and vertically by replacing the given coordinates
        with the average of the line (of 20 boxes).
        Then sort the boxes left -> right and top -> bottom
        '''
        boxdf = pd.DataFrame(self.box_coord, columns=['x', 'y', 'w', 'h'])
        boxdf_sorted = boxdf.copy()
        # Horizontal alignment (mean y)
        boxdf_sorted = boxdf_sorted.sort_values(by='y', ignore_index=True)
        for i in range(0, 400, 20):
            boxdf_sorted.loc[i:i + 19, 'y'] = round(boxdf_sorted.loc[i:i + 19, 'y'].mean(), 0)
        # Vertical alignment (mean x)
        boxdf_sorted = boxdf_sorted.sort_values(by='x', ignore_index=True)
        for j in range(0, 400, 20):
            boxdf_sorted.loc[j:j + 19, 'x'] = round(boxdf_sorted.loc[j:j + 19, 'x'].mean(), 0)
        # Final reordering
        boxdf_sorted = boxdf_sorted.sort_values(by=['y', 'x'], ignore_index=True)
        self.box_coord = boxdf_sorted.to_numpy()
    def extract_boxes(self):
        '''
        Iteration among thresholds for binary image, to find the one that
        will allow for the detection of all the boxes (400). Then reorder
        the box list top to bottom, and perform box alignment.
        '''
        max_box_detected = 0
        lower_TSt = 255
        while (max_box_detected) != 400 and (lower_TSt >= 0):
            lower_TSt -= 1
            self.find_boxes(lower_TSt)
            max_box_detected = len(self.box_coord)
        self.box_coord = np.array(self.box_coord)
        self.box_coord = np.flip(self.box_coord, axis=0)
        self.align_boxes()
    @st.cache_data
    def plot_boxes(_self, coord):
        '''
        Display detected boxes
        :param coord: array of X coordinates (X, 4)
        :return:
        '''
        img_box = _self.img_rot.copy()
        if coord.ndim > 1:
            for gbox in coord:
                x, y, w, h = gbox
                cv.rectangle(img_box, (x, y), (x + w, y + h), (0, 255, 0), 2)
        else:  # If giving only one box to the function
            x, y, w, h = coord
            cv.rectangle(img_box, (x, y), (x + w, y + h), (0, 255, 0), 2)
        return img_box

class ROIExtract:
    '''
    Define parameters and methods needed for image (ROI) extraction from given box coordinates
    Also includes symbols/numbers indexes and standard labels definition.
    '''
    def __init__(self, image_rot):
        '''
        Loads image, defines indexes for symbols and numbers. Defines box width and height
        Also defines standard labels.
        :param image_rot: image (openCV loaded file)
        '''
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
        '''
        Extract image (ROI) located inside given coordinates, on the scanned image
        :param coord: list of 4 coordinates
        :return: image (ROI) of dimension [height, width]
        '''
        gray = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)
        x, y, w, h = coord
        roi = gray[y + 4:y + self.height, x + 5:x + self.width]
        return roi
    def extract_roi_symbols(self, coord_list):
        '''
        Iterated through coordinates to extract all the images (ROI) corresponding
        to symbols index. Boxes must be properly aligned and reordered for index
        selection to work.
        :param coord_list: array of X coordinates (X, 4)
        '''
        self.roi_symbols = []
        for coord in coord_list[self.symbols_index]:
            roi_img = self.extract_roi_inside_box(coord)
            self.roi_symbols.append(roi_img)
        self.roi_symbols = np.array(self.roi_symbols)
    def extract_roi_all(self, coord_list):
        '''
        Iterated through coordinates to extract all the images (ROI).
        :param coord_list: array of X coordinates (X, 4)
        '''
        self.roi_all = []
        for coord in coord_list:
            roi_img = self.extract_roi_inside_box(coord)
            self.roi_all.append(roi_img)
        self.roi_all = np.array(self.roi_all)
    def set_labels(self):
        '''
        Define default labels usable for all result sheet.
        '''
        self.blank_labels = np.zeros(200, dtype=int)
        self.sheet_labels = np.array([3, 6, 4, 2, 9, 8, 7, 9, 1, 6, 3, 7, 6, 2, 5, 8, 4, 1, 9, 5,
                        2, 9, 6, 8, 1, 7, 5, 3, 4, 7, 2, 5, 3, 1, 9, 6, 7, 8, 2, 4,
                        6, 3, 7, 9, 5, 4, 8, 1, 2, 9, 8, 4, 1, 8, 7, 5, 9, 2, 6, 3,
                        1, 8, 5, 2, 4, 3, 9, 6, 7, 1, 5, 6, 7, 5, 1, 3, 4, 9, 8, 2,
                        9, 7, 4, 6, 8, 2, 1, 5, 3, 2, 9, 8, 4, 3, 6, 7, 2, 5, 9, 1,
                        4, 6, 1, 5, 3, 9, 2, 7, 8, 5, 6, 3, 9, 4, 5, 2, 6, 7, 1, 8,
                        5, 2, 8, 1, 7, 6, 3, 4, 9, 8, 1, 2, 6, 9, 8, 1, 5, 3, 4, 7,
                        3, 5, 2, 4, 9, 1, 7, 8, 6, 4, 3, 1, 8, 7, 2, 4, 3, 6, 5, 9,
                        7, 1, 9, 3, 6, 8, 4, 2, 5, 6, 7, 9, 2, 6, 3, 8, 1, 4, 7, 5,
                        8, 4, 3, 7, 2, 5, 6, 9, 1, 3, 4, 7, 5, 2, 4, 9, 8, 1, 3, 6])

