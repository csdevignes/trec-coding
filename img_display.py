'''
Contains functions for image (symbols, region of interest = ROI) display on streamlit web app and Jupyter notebooks
'''

import math
import matplotlib.pyplot as plt
import streamlit as st
import numpy as np
import cv2 as cv

def roi_display_streamlit(prefix):
    '''
    Display streamlit controllers to adapt symbols display (row_size, label to sort by) and calls roi_display
    with the chosen parameters
    '''
    controls = st.columns(2)
    with controls[0]:
        label_list = []
        for item in st.session_state.keys():
            if item.endswith('labels') and item != 'dataset_labels':
                label_list.append(item)
        label_match = {'blank_labels': "Vides (zeros)",
                       'sheet_labels': "Numéros de la feuille",
                        'annot_labels': "Annotations en mémoire",
                        'correct_labels': "Corrections en mémoire",
                       'predicted_labels': "Prédictions du modèle"}
        st.radio("Charger les labels :", label_list,
                 format_func=lambda x: label_match[x],
                 key=f"{prefix}_labels_display")
    with controls[1]:
        size_match = {20: "Petit", 12: "Moyen", 6: "Grand"}
        st.select_slider("Taille:", [20, 12, 6], format_func=lambda x: size_match[x],
                                    value=12, key=f'{prefix}_row-size')
    roi_display(prefix, st.session_state[st.session_state[f'{prefix}_labels_display']],
                st.session_state['ex_roi_symbols'], row_size=st.session_state[f'{prefix}_row-size'])
def roi_display(prefix, labels, image_array, mask = None, row_size = None):
    '''
    Display function used to show all symbols images (ROI) ordered by labels, with a given row_size (number of
    symbols per row). A mask can be passed to specify which symbols to display.
    :param prefix: string, used to specify the context in which function is called
    :param labels: array of X labels (X,)
    :param image_array: array of X images (X, height, width)
    :param mask: boolean array matching labels dimension
    :param row_size: int, number of symbols per row
    '''
    if mask is None:
        mask = np.full((len(image_array)), True)
    if labels is None:
        labels = np.ones(len(image_array))
    if row_size is None:
        row_size = 12

    image_list_filtered = image_array[mask]
    label_list_filtered = labels[mask]

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
def update_label(img_indice, loadto, prefix=""):
    '''
    In annotation or correction, updates a specific index in loadto labels (annot_labels or correct_labels)
    using the position index of the symbol associated with form entry. Used as callback function in annotate.
    :param img_indice: int, index of symbol to update label from
    :param loadto: string, name of labels to update
    :param prefix: string, context in which the update is made ('an' or 'co')
    '''
    st.session_state[loadto][img_indice+9] = st.session_state[f'{prefix}_symbol{img_indice}']
def load_label_from(loadto, prefix=""):
    '''
    For annotation and correction. Allows to load labels from blank, sheet or predicted
    as 'loadto' labels which can be annot_labels or correct_labels, depending on where
    the function is called.
    :param loadto: string, name of labels to update
    :param prefix: string, context in which the update is made ('an' or 'co')
    '''
    label_match = {'blank_labels': "Vides (zeros)",
                   'sheet_labels': "Numéros de la feuille",
                   'annot_labels': "Annotations en mémoire",
                   'predicted_labels': "Prédictions du modèle"}
    with st.form(f"{prefix}_labelchoice"):
        st.selectbox("Charger les labels :", ['blank_labels', 'sheet_labels', 'annot_labels', 'predicted_labels'],
                     format_func=lambda x: label_match[x], index=1, key=f"{prefix}_labels_toload")
        an_submitted_sl = st.form_submit_button("Submit")
        if an_submitted_sl:
            st.session_state[loadto] = st.session_state[st.session_state[f'{prefix}_labels_toload']].copy()
            st.write("Labels de départ :", st.session_state[f'{prefix}_labels_toload'])

def annotate(prefix="", annotation=False):
    '''
    Annotation function used to display images ordered by labels and to give the ability to modify their annotation.
    In annotation context, it is possible to use streamlit interface to load as label a single label for the whole grid.
    :param prefix: string, context in which the update is made ('an' or 'co')
    :param annotation: boolean, set to load annotation streamlit interface
    '''

    if annotation==True:
        loadto = 'annot_labels'
        st.radio(
            "Comment annoter les symboles :",
            ["Monolabel", "Plusieurs labels"],
            captions=["La feuille contient un seul type de symbole", "La feuille contient différents symboles"],
            key=f'{prefix}_label-type')
        if st.session_state[f'{prefix}_label-type'] == "Monolabel":
            with st.form(f"{prefix}_monolabel"):
                st.number_input('Label', key=f"{prefix}_label-value", min_value=0, max_value=9, step=1)
                an_submitted_ml = st.form_submit_button("Submit")
                if an_submitted_ml:
                    st.session_state[loadto] = np.full(200, st.session_state[f'{prefix}_label-value'])
                    st.write("Monolabel, valeur :", st.session_state[f'{prefix}_label-value'])
        if st.session_state[f'{prefix}_label-type'] == "Plusieurs labels":
            load_label_from(loadto, prefix)
    else:
        st.session_state[f'{prefix}_label-type'] = "Correction"
        loadto = 'correct_labels'
        load_label_from(loadto, prefix)
    image_list_filtered = st.session_state['ex_roi_symbols'][st.session_state[f'{prefix}_mask']]
    label_list_filtered = st.session_state[loadto][st.session_state[f'{prefix}_mask']]
    st.header("Symboles")
    size_match = {20: "Petit", 12: "Moyen", 6: "Grand"}
    row_size = st.select_slider("Taille:", [20, 12, 6], format_func=lambda x: size_match[x], value=12,
                                     key=f'{prefix}_row-size')
    for l in np.unique(label_list_filtered):
        st.header(f'Label {l}')
        label_mask = (label_list_filtered == l)
        img_indices = np.where(label_mask)[0]
        grid = st.columns(row_size)
        col = 0
        for i, pixels in enumerate(image_list_filtered[img_indices]):
            with grid[col]:
                st.image(pixels, img_indices[i])
                if st.session_state[f'{prefix}_label-type'] != "Monolabel":
                    st.number_input(f"Symbol{img_indices[i]}", min_value=0, max_value=9,
                                    value=label_list_filtered[img_indices[i]],
                                    key=f"{prefix}_symbol{img_indices[i]}",
                                    help="Enter label between 1 and 9 or 0 for errors",
                                    on_change=update_label, args=[img_indices[i], loadto, prefix],
                                    label_visibility="collapsed")
                col = (col + 1) % row_size

def plot_results_scan(image, labels, sheet_labels, boxes):
    '''
    Plot box coordinates on the scanned sheet, with different colors depending on symbol correction.
    If correct label is 0 (error/undetected) : blue, if correct label is the same as sheet label (correct) : green,
    if corrrect label is different from sheet label (incorrect) : red.
    :param image: image, to plot coordinates on
    :param labels: array of X labels (X,) from prediction or correction, to compare with sheet labels
    :param sheet_labels: array of X labels (X,) corresponding to numbers written on the sheet
    :param boxes: array of X coordinates (X, 4), coordinates from all the boxes
    '''
    image_copy = image.copy()
    intervals = [(20, 40), (60, 80), (100, 120), (140, 160), (180, 200), (220, 240), (260, 280), (300, 320),
                 (340, 360), (380, 400)]
    symbols_index = np.concatenate([np.arange(start, end, 1) for start, end in intervals])
    for i, gbox in enumerate(boxes[symbols_index]):
        x, y, w, h = gbox
        if (labels[i] == 0):
            cv.rectangle(image_copy, (x, y), (x + w, y + h), (0, 0, 255), 3)
        elif (labels[i] == sheet_labels[i]):
            cv.rectangle(image_copy, (x, y), (x + w, y + h), (0, 255, 0), 3)
        else:
            cv.rectangle(image_copy, (x, y), (x + w, y + h), (255, 0, 0), 3)
    return image_copy

def roi_display_jup(image_array, labels = None, mask = None, row_size = None):
    '''
    Used to display symbols (region of interest - ROI) on Jupyter notebooks
    :param image_array: array of X images (X, height, width)
    :param labels: array of X labels (X,)
    :param mask: boolean array matching labels dimension
    :param row_size: int, number of symbols per row
    '''
    if mask is None:
        mask = np.full((len(image_array)), True)
    if labels is None:
        labels = np.ones(len(image_array))
    if row_size is None:
        row_size = 12

    image_list_filtered = image_array[mask]
    label_list_filtered = labels[mask]

    for l in np.unique(label_list_filtered):
        label_mask = (label_list_filtered == l)
        img_indices = np.where(label_mask)[0]
        n_rows = math.ceil(len(image_list_filtered[img_indices]) / row_size)

        if n_rows == 1:
            fig, axs = plt.subplots(n_rows, row_size, figsize=(row_size, n_rows))
            axs = np.reshape(axs, (1, row_size))
        else:
            fig, axs = plt.subplots(n_rows, row_size, figsize=(row_size, n_rows))

        for i, pixels in enumerate(image_list_filtered[img_indices]):
            row = i // row_size
            col = i % row_size
            ax = axs[row, col]
            ax.imshow(pixels)
            ax.text(0.5, 1.02, str(img_indices[i]), transform=ax.transAxes, ha='center', va='bottom', fontsize=10)
            ax.axis('off')

        fig.suptitle(f'Label {l}', fontsize=16)
        fig.subplots_adjust(top=0.75)
        plt.show()
