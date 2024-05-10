'''
TREC correction app - page 3
This page aims to correct scanned resultsheet and analyse results
'''

import numpy as np
import streamlit as st

import evaluate
import sidebar
import train

sidebar.sidebar_progress()
sidebar.sidebar_legend()

if 'uploaded_file_name' in st.session_state:
    st.write(f"Fichier analysé : {repr(st.session_state['uploaded_file_name'])}")
if 'ex_roi_symbols' not in st.session_state:
    st.write("Veuillez d'abord extraire les symboles")

else:
    if 'correct_labels' not in st.session_state:
        st.session_state['correct_labels'] = st.session_state['sheet_labels'].copy()
    st.checkbox("Exclure les cases exemple", key='co_exclude-exemple', value=True)
    with st.form("co_label_choice"):
        co_label_match = {'sheet_labels': "Numéros de la feuille",
                       'annot_labels': "Annotations en mémoire"}
        co_labels_toload = st.selectbox("Charger les labels :", ['sheet_labels', 'annot_labels'],
                                     format_func=lambda x: co_label_match[x], index=0, key="co_labels_toload")
        co_submitted = st.form_submit_button("Submit")
        if co_submitted:
            st.session_state['correct_labels'] = st.session_state[co_labels_toload].copy()
            st.write("Labels de départ :", st.session_state['co_labels_toload'])


    def co_update_label(img_indice):
        st.session_state.correct_labels[img_indice + 9] = st.session_state[f'co_symbol{img_indice}']

    st.title("Corriger")
    if st.session_state['co_exclude-exemple'] == True:
        co_excluded_index = range(9)
    else:
        co_excluded_index = []
    co_keeper_index = [i for i in range(0, 200) if i not in co_excluded_index]
    co_image_list_filtered = st.session_state['ex_roi_symbols'][co_keeper_index]
    co_label_list_filtered = st.session_state['correct_labels'][co_keeper_index]

    co_size_match = {20: "Petit", 12: "Moyen", 6: "Grand"}
    co_row_size = st.select_slider("Taille:", [20, 12, 6], format_func=lambda x: co_size_match[x],
                                   value=12, key='co_row-size')
    for l in np.unique(co_label_list_filtered):
        st.header(f'Label {l}')
        label_mask = (co_label_list_filtered == l)
        img_indices = np.where(label_mask)[0]
        grid = st.columns(co_row_size)
        col = 0
        for i, pixels in enumerate(co_image_list_filtered[img_indices]):
            with grid[col]:
                st.image(pixels, img_indices[i])
                st.number_input(f"Symbol{img_indices[i]}", min_value=0, max_value=9,
                                value=co_label_list_filtered[img_indices[i]],
                                key=f"co_symbol{img_indices[i]}",
                                help="Entrez le label correct entre 1 et 9 ou 0 si erreur",
                                on_change=co_update_label, args=[img_indices[i]],
                                label_visibility="collapsed")
                col = (col + 1) % co_row_size

    if 'correct_labels' in st.session_state:
        st.header("Résultats :")
        e = evaluate.Evaluator(st.session_state['ex_roi_symbols'][co_keeper_index], st.session_state['sheet_labels'][co_keeper_index])
        e.update_manual_labels(st.session_state['correct_labels'][co_keeper_index])
        e.correction()
        st.write(e.y_test)
        st.write(e.manual_labels)
        st.write(f'Erreurs : {e.erreurs}')
        d = train.Dataset(st.session_state['ex_roi_symbols'][co_keeper_index], st.session_state['correct_labels'][co_keeper_index])
        st.write(d.dataset.shape)
        file_name = st.session_state["uploaded_file_name"].split('.')[0]
        st.download_button(
            label="Download .csv dataset",
            data=d.convert_csv(),
            file_name=f'{file_name}.csv',
            mime="text/csv"
        )

st.write(st.session_state)