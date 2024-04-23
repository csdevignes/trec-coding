'''
Contains functions for image display on streamlit web app
'''
import streamlit as st
import numpy as np
def roi_display(image_list, label_list, row_size):
    ## Image plot
    for l in np.unique(label_list):
        st.header(f'Label {l}')
        label_mask = (label_list == l)
        img_indices = np.where(label_mask)[0]
        grid = st.columns(row_size)
        col = 0
        for i, pixels in enumerate(image_list[img_indices]):
             with grid[col]:
                st.image(pixels, img_indices[i])
                col = (col + 1) % row_size
