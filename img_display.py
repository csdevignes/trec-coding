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
        self.manual_labels = self.true_labels
    def update_labels(self):
        if 'manual_labels' not in st.session_state:
            st.session_state.manual_labels = self.true_labels
        else:
            self.manual_labels = st.session_state.manual_labels
    def controllers(self):
        controls = st.columns(3)
        with controls[0]:
            label = st.radio("Tri par label :", ["Vide", "Numéros", "Annotations"], key='label-sorting2')
            if label == "Vide":
                labels_fig = st.session_state['blank_labels']
            elif label == "Numéros":
                labels_fig = st.session_state['sheet_labels']
            elif label == "Annotations":
                labels_fig = st.session_state['annot_labels']
        with controls[1]:
            size_match = {20: "Petit", 12: "Moyen", 6: "Grand"}
            self.row_size = st.select_slider("Taille:", [20, 12, 6], format_func=lambda x: size_match[x], value=12,
                                        key='row-size-annot-m')
        with controls[2]:
            exclude_exemple = st.checkbox("Exclure les cases exemple", key='exclude-exemple')
            if exclude_exemple:
                excluded_index = range(9)
    def update(self, img_index):
        self.manual_labels[img_index] = st.session_state[f'symbol{img_index}']
        if st.session_state.manual_labels[img_index] != self.manual_labels[img_index]:
            st.session_state.manual_labels[img_index] = self.manual_labels[img_index]
    def annotation_display(self):
        keeper_indx = [i for i in range(0, 200) if i not in excluded_indx]
        image_list_filtered = self.pict[keeper_indx]
        label_list_filtered = self.true_labels[keeper_indx]

        for l in np.unique(label_list_filtered):
            st.header(f'Label {l}')
            label_mask = (label_list_filtered == l)
            img_indices = np.where(label_mask)[0]
            grid = st.columns(self.row_size)
            col = 0
            for i, pixels in enumerate(image_list_filtered[img_indices]):
                with grid[col]:
                    st.image(pixels, img_indices[i])
                    st.number_input(f"Symbol{img_indices[i]}", min_value=0, max_value=9,
                                    value=self.manual_labels[img_indices[i]],
                                    key=f"symbol{img_indices[i]}",
                                    help="Enter label between 1 and 9 or 0 for errors",
                                    on_change= self.update, args=[img_indices[i]],
                                    label_visibility="collapsed")
                    col = (col + 1) % self.row_size

