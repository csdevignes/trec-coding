'''
Contains functions for image display on streamlit web app
'''
import streamlit as st
import numpy as np

def roi_display(prefix="", excluded_indx=[]):
    '''
    Display function used to show all symbols images ordered by labels
    :param image_list: array of X images (X, height, width)
    :param label_list: array of X labels (X,)
    :param row_size:
    :param excluded_indx:
    :return:
    '''
    with st.expander("Voir/Cacher les symboles extraits"):
        controls = st.columns(2)
        with controls[0]:
            label_list = []
            for item in st.session_state.keys():
                if item.endswith('labels'):
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

        keeper_indx = [i for i in range(0, 200) if i not in excluded_indx]
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
    Display function used to show all symbols images ordered by labels
    :param image_list: array of X images (X, height, width)
    :param label_list: array of X labels (X,)
    :param row_size:
    :param excluded_indx:
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

