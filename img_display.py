'''
Contains functions for image display on streamlit web app
'''
import streamlit as st
import numpy as np
import cv2 as cv

def roi_display(prefix="", keeper_indx=range(0, 200)):
    '''
    Display function used to show all symbols images ordered by labels
    :param image_list: array of X images (X, height, width)
    :param label_list: array of X labels (X,)
    :param row_size:
    :param excluded_indx:
    :return:
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

    image_list_filtered = st.session_state['ex_roi_symbols'][keeper_indx]
    label_list_filtered = st.session_state[st.session_state[f'{prefix}_labels_display']][keeper_indx]

    for l in np.unique(label_list_filtered):
        st.header(f'Label {l}')
        label_mask = (label_list_filtered == l)
        img_indices = np.where(label_mask)[0]
        grid = st.columns(st.session_state[f'{prefix}_row-size'])
        col = 0
        for i, pixels in enumerate(image_list_filtered[img_indices]):
            with grid[col]:
                st.image(pixels, img_indices[i])
                col = (col + 1) % st.session_state[f'{prefix}_row-size']
def update_label(img_indice, loadto, prefix=""):
    st.session_state[loadto][img_indice+9] = st.session_state[f'{prefix}_symbol{img_indice}']
def load_label_from(loadto, prefix=""):
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
    Annotation function used to display images ordered by labels
    and to give the ability to modify their annotation.
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

    image_list_filtered = st.session_state['ex_roi_symbols'][st.session_state[f'{prefix}_keeper_indx']]
    label_list_filtered = st.session_state[loadto][st.session_state[f'{prefix}_keeper_indx']]
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

def plot_results_scan(image, labels, boxes):
    image_copy = image.copy()
    intervals = [(20, 40), (60, 80), (100, 120), (140, 160), (180, 200), (220, 240), (260, 280), (300, 320),
                 (340, 360), (380, 400)]
    symbols_index = np.concatenate([np.arange(start, end, 1) for start, end in intervals])
    for i, gbox in enumerate(boxes[symbols_index]):
        x, y, w, h = gbox
        if (labels[i] == 0):
            cv.rectangle(image_copy, (x, y), (x + w, y + h), (255, 0, 0), 3)
        elif (labels[i] == st.session_state["sheet_labels"][i]):
            cv.rectangle(image_copy, (x, y), (x + w, y + h), (0, 255, 0), 3)
        else:
            cv.rectangle(image_copy, (x, y), (x + w, y + h), (0, 0, 255), 3)
    return image_copy