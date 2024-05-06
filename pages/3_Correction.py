'''
TREC correction app - page 3
This page aims to correct scanned resultsheet and analyse results
'''

import numpy as np
import streamlit as st
import sidebar
import train

sidebar.sidebar_progress()
sidebar.sidebar_legend()

if 'uploaded_file_name' in st.session_state:
    st.write(f"Fichier analysé : {repr(st.session_state['uploaded_file_name'])}")
if 'roi_symbols' not in st.session_state:
    st.write("Veuillez d'abord extraire les symboles")

else:
    if 'correct_labels' not in st.session_state:
        st.session_state['correct_labels'] = st.session_state['sheet_labels']
    st.checkbox("Exclure les cases exemple", key='exclude-exemple', value=True)
    with st.form("label_choice_correct"):
        label_match = {'sheet_labels': "Numéros de la feuille",
                       'annot_labels': "Annotations en mémoire"}
        labels_toload = st.selectbox("Charger les labels :", ['sheet_labels', 'annot_labels'],
                                     format_func=lambda x: label_match[x], index=0, key="labels_toload_correct")
        submitted_c = st.form_submit_button("Submit")
        if submitted_c:
            st.session_state['correct_labels'] = st.session_state[labels_toload]
            st.write("Labels de départ :", st.session_state['labels_toload_annot'])


    def update_label(img_indice):
        st.session_state.annot_labels[img_indice + 9] = st.session_state[f'c_symbol{img_indice}']

    st.title("Corriger")
    if st.session_state['exclude-exemple'] == True:
        excluded_index = range(9)
    else:
        excluded_index = []
    keeper_indx = [i for i in range(0, 200) if i not in excluded_index]
    image_list_filtered = st.session_state['roi_symbols'][keeper_indx]
    label_list_filtered = st.session_state['correct_labels'][keeper_indx]

    size_match = {20: "Petit", 12: "Moyen", 6: "Grand"}
    row_size = st.select_slider("Taille:", [20, 12, 6], format_func=lambda x: size_match[x], value=12,
                                key='row-size-correct')
    for l in np.unique(label_list_filtered):
        st.header(f'Label {l}')
        label_mask = (label_list_filtered == l)
        img_indices = np.where(label_mask)[0]
        grid = st.columns(row_size)
        col = 0
        for i, pixels in enumerate(image_list_filtered[img_indices]):
            with grid[col]:
                st.image(pixels, img_indices[i])
                st.number_input(f"Symbol{img_indices[i]}", min_value=0, max_value=9,
                                value=label_list_filtered[img_indices[i]],
                                key=f"c_symbol{img_indices[i]}",
                                help="Entrez le label correct entre 1 et 9 ou 0 si erreur",
                                on_change=update_label, args=[img_indices[i]],
                                label_visibility="collapsed")
                col = (col + 1) % row_size

if 'correct_labels' in st.session_state:
    keeper_index = [i for i in range(0, 200) if i not in excluded_index]
    d = train.Dataset(st.session_state['roi_symbols'][keeper_index], st.session_state['correct_labels'][keeper_index])
    st.write(d.dataset.shape)
    file_name = st.session_state["uploaded_file_name"].split('.')[0]
    st.download_button(
        label="Download .csv dataset",
        data=d.convert_csv(),
        file_name=f'{file_name}.csv',
        mime="text/csv"
    )

st.write(st.session_state)