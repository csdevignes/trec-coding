'''
Contains functions for image display on streamlit web app
'''
import streamlit as st
import numpy as np
@st.cache_data
def roi_display(image_list, label_list, row_size, excluded_indx=[]):
    '''
    Display function used to show all symbols images ordered by labels
    :param image_list: array of X images (X, height, width)
    :param label_list: array of X labels (X,)
    :param row_size:
    :param excluded_indx:
    :return:
    '''
    keeper_indx = [i for i in range(0, 200) if i not in excluded_indx]
    image_list_filtered = image_list[keeper_indx]
    label_list_filtered = label_list[keeper_indx]

    for l in np.unique(label_list_filtered):
        st.header(f'Label {l}')
        label_mask = (label_list_filtered == l)
        img_indices = np.where(label_mask)[0]
        grid = st.columns(row_size)
        col = 0
        for i, pixels in enumerate(image_list_filtered[img_indices]):
            with grid[col]:
                st.image(pixels, img_indices[i])
                col = (col + 1) % row_size

class Annotation:
    def __init__(self, picts, labels):
        self.pict = picts
        self.true_labels = labels
    def update_labels(self):
        self.manual_labels = self.true_labels
        if 'manual_labels' not in st.session_state:
            st.session_state.manual_labels = self.true_labels
        else:
            self.manual_labels = st.session_state.manual_labels
    def controllers(self):
        self.row_size = st.select_slider("Row size:", range(1, 21), value=12, key='row-size-annotation')
    def update(self, img_index):
        self.manual_labels[img_index] = st.session_state[f'symbol{img_index}']
        if st.session_state.manual_labels[img_index] != self.manual_labels[img_index]:
            st.session_state.manual_labels[img_index] = self.manual_labels[img_index]
    def annotation_display(self):
        for l in np.unique(self.true_labels):
            st.header(f'Label {l}')
            label_mask = (self.true_labels == l)
            self.img_indices = np.where(label_mask)[0]
            grid = st.columns(self.row_size)
            col = 0
            for i, pixels in enumerate(self.pict[self.img_indices]):
                 with grid[col]:
                    st.image(pixels, self.img_indices[i])
                    st.number_input(f"Symbol{self.img_indices[i]}", min_value=0, max_value=9,
                                    value=self.manual_labels[self.img_indices[i]],
                                    key=f"symbol{self.img_indices[i]}",
                                    help="Enter label between 1 and 9 or 0 for errors",
                                    on_change= self.update, args=[self.img_indices[i]],
                                    label_visibility="collapsed")
                    col = (col + 1) % self.row_size

