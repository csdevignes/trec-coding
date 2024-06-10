'''
TREC correction app - page Correction
This page aims to correct scanned resultsheet and analyse results
'''
import os

import numpy as np
import streamlit as st

import evaluate
import img_display
import tcutil
import train

tcutil.sidebar_progress()
tcutil.sidebar_legend()

if 'uploaded_file_name' in st.session_state:
    st.write(f"Fichier analysé : {repr(st.session_state['uploaded_file_name'])}")
if 'ex_roi_symbols' not in st.session_state:
    st.write("Veuillez d'abord extraire les symboles")

else:
    l = tcutil.Labels()
    l.set_labels()
    entrees = os.listdir("models/")
    model_list = [entree for entree in entrees if entree.endswith(".keras")]
    st.selectbox("Modèle à utiliser", model_list, key="model_path")
    t = train.Trainer(st.session_state['ex_roi_symbols'])
    e = evaluate.Evaluator(t.pict_redim)
    if st.button("Lancer la prédiction des labels"):
        st.session_state['predicted_labels'] = e.predict(f'models/{st.session_state["model_path"]}')
        e.correction(correct_labels= st.session_state['sheet_labels'],
                     test_labels=st.session_state['predicted_labels'],
                     keeper_mask=st.session_state['co_keeper_mask'])
        st.write(e.result)
        st.pyplot(e.cm_plot())
    if st.button("Calculer les résultats avec la correction manuelle"):
        e.correction(correct_labels= st.session_state['sheet_labels'],
                     test_labels=st.session_state['correct_labels'],
                     keeper_mask=st.session_state['co_keeper_mask'])
        st.write(e.result)
        st.pyplot(e.cm_plot())
    with st.expander('Voir la grille corrigée'):
        label_match = {'predicted_labels': "Prédictions du modèle",
                       'correct_labels': "Corrections"}
        st.radio("Labels tests :", ['predicted_labels', 'correct_labels'],
                 format_func=lambda x: label_match[x], index=0,
                 key=f"co_scan_label")
        res_scan = img_display.plot_results_scan(st.session_state['ex_scan_img'],
                                      st.session_state[st.session_state['co_scan_label']],
                                      st.session_state["sheet_labels"],
                                      st.session_state['ex_box_coord'])
        st.image(res_scan)

    st.header("Paramètres")
    tcutil.exclude_example("co")
    img_display.annotate(prefix="co", annotation=False)

    if 'correct_labels' in st.session_state:
        st.header("Résultats :")
        d = train.Dataset(st.session_state['ex_roi_symbols'][st.session_state[f'co_mask']],
                          st.session_state['correct_labels'][st.session_state[f'co_mask']])
        st.write(d.dataset.shape)
        file_name = st.session_state["uploaded_file_name"].split('.')[0]
        st.download_button(
            label="Download .csv dataset",
            data=d.convert_csv(),
            file_name=f'{file_name}.csv',
            mime="text/csv"
        )

st.write(st.session_state)