'''
TREC correction app - page Modèle
This page aims to provide interface for training and evaluating the model
'''
import numpy as np
import os
import streamlit as st

import train, evaluate, tcutil, img_display


tcutil.sidebar_progress()
tcutil.sidebar_legend()

# 1 - Load dataset from uploaded .csv, or train or test datasets
def dataset_load(t):
    st.write(t.full_da.shape)
    st.session_state['dataset_picts'] = t.pict_redim
    st.session_state['dataset_labels'] = t.label

if 'full_da' not in st.session_state:
    col1, col2 = st.columns([0.5, 0.5], gap="small")
    with col1:
        uploaded_file = st.file_uploader("Upload dataset annoté (format csv)", type=['csv'])
        if uploaded_file is not None:
            df = np.loadtxt(uploaded_file, delimiter=',')
            t = train.Trainer(data=df)
            dataset_load(t)
    with col2:
        if st.button("Test dataset complet"):
            t = train.Trainer(datapath="data_resultsheets/Test/")
            dataset_load(t)
        if st.button("Train dataset complet"):
            t = train.Trainer(datapath="data_resultsheets/Train/")
            dataset_load(t)
        if st.button("Effacer les données"):
            st.session_state.clear()

if 'dataset_picts' in st.session_state:
    # 2 - Make prediction using one of the model
    e = evaluate.Evaluator(st.session_state['dataset_picts'])
    entrees = os.listdir("models/")
    model_list = [entree for entree in entrees if entree.endswith(".keras")]
    st.selectbox("Modèle à utiliser", model_list, key="model_path")
    st.session_state['predicted_labels'] = e.predict(f'models/{st.session_state["model_path"]}')
    # 3 - Display metrics
    e.correction(st.session_state['dataset_labels'],
                 st.session_state['predicted_labels'], e.fill_mask)
    e.metrics_calculation()
    st.write(e.result)
    st.pyplot(e.cm_plot())
    st.write(f'Accuracy : {e.g_accuracy}, Errors : {e.g_error}')
    st.table(e.metrics_df())
    st.pyplot(e.metrics_plot())
    st.write(f'Total false positive : {e.TFP}, Total false negative : {e.TFN}')
    # 4 - Optional : display symbols from dataset and their labels, for verification only
    if st.button("Show symbols"):
        img_display.roi_display(prefix='mo', labels=st.session_state['dataset_labels'],
                                image_array=st.session_state['dataset_picts'], mask=e.fill_mask, row_size=20)
