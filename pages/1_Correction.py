'''
TREC correction app - page Correction
This page aims to correct scanned resultsheet and analyse results
'''

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
    tcutil.set_labels()
    if st.button("Lancer la prédiction des labels"):
        t = train.Trainer(st.session_state['ex_roi_symbols'])
        e = evaluate.Evaluator(t.pict_redim)
        e.predict()
        e.correction(correct_labels= st.session_state['sheet_labels'][st.session_state['co_keeper_indx']],
                     test_labels=st.session_state['predicted_labels'][st.session_state['co_keeper_indx']])
        st.write(f"Nombre d'erreurs : {e.nb_erreurs}")
        st.pyplot(e.cm_plot())
    with st.expander('Voir la grille corrigée'):
        label_match = {'correct_labels': "Corrections",
                       'predicted_labels': "Prédictions du modèle"}
        st.radio("Labels tests :", ['predicted_labels', 'correct_labels'],
                 format_func=lambda x: label_match[x], index=0,
                 key=f"co_scan_label")
        res_scan = img_display.plot_results_scan(st.session_state['ex_scan_img'],
                                      st.session_state[st.session_state['co_scan_label']],
                                      st.session_state['ex_box_coord'])
        st.image(res_scan)
    st.header("Paramètres")
    tcutil.exclude_example("co")
    img_display.annotate(prefix="co", annotation=False)

    if 'correct_labels' in st.session_state:
        st.header("Résultats :")
        d = train.Dataset(st.session_state['ex_roi_symbols'][st.session_state['co_keeper_indx']],
                          st.session_state['correct_labels'][st.session_state['co_keeper_indx']])
        st.write(d.dataset.shape)
        file_name = st.session_state["uploaded_file_name"].split('.')[0]
        st.download_button(
            label="Download .csv dataset",
            data=d.convert_csv(),
            file_name=f'{file_name}.csv',
            mime="text/csv"
        )

st.write(st.session_state)