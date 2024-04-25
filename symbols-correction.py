import numpy as np

import evaluate
import extract
import streamlit as st
import keras

import img_display
import train

st.title('TREC symbol correction')
image_file = "Test.png"
image_path = f"scan_resultsheets/{image_file}"
st.write(image_path)
b = extract.Boxdetection(image_path)
degree = st.number_input('Rotation degree', min_value=-360., max_value=360., value=0.3,
                         step=0.01, key="rotation-degree",
                         help="Adjust rotation so the grid is aligned on the lines")
b.image_rotation(degree)
col1, col2 = st.columns([0.5, 0.5], gap="small")
with col1:
    st.image(b.plot_scan(b.img))
with col2:
    st.image(b.plot_scan(b.img_rot))

start_box_extraction = st.checkbox('Extract boxes coordinates', key='start-box-extraction',
                                   help='Unselect while you optimize rotation')

if start_box_extraction:
    b.extract_boxes()
    st.write(f'Box extracted with rotation {degree} : dimension {b.box_coord.shape}')
    # st.image(b.plot_boxes(b.box_coord))

start_roi_extraction = st.checkbox('Extract ROI content images', key='start-roi-extraction',
                                   help='First extract boxes coordinates',
                                   disabled=not start_box_extraction)

if start_roi_extraction:
    r = extract.ROIExtract(b.img_rot)
    r.extract_roi_symbols(b.box_coord)
    st.write(f'ROI extracted : dimension {r.roi_symbols.shape}')

    with st.expander("See extracted pictures"):
        # Image display with streamlit
        ## Controllers
        controls = st.columns(2)
        with controls[0]:
            label = st.radio("Sort by label :", ["Blank", "True"], key='label-sorting')
            if label == "Blank":
                labels_fig = r.blank_labels
            elif label == "True":
                labels_fig = r.true_labels
        with controls[1]:
            row_size = st.select_slider("Row size:", range(1, 21), value=12, key='row-size-roi')
        img_display.roi_display(r.roi_symbols, labels_fig, row_size)

start_predictions = st.checkbox('Symbols identification', key='start-predictions',
                                   help='First extract ROI images',
                                   disabled=not start_roi_extraction)

if start_predictions:
    t = train.Trainer(r.roi_symbols)
    t.redimension_pict()
    e = evaluate.Evaluator(t.pict_redim, r.true_labels)
    e.predictions()
    st.image(e.plot_results(b.img_rot, b.box_coord[r.symbols_index]))

manual_correction = st.checkbox('Correct manually', key='manual-correction',
                                   help='Correct results manually if identification is not correct',
                                   disabled=not start_predictions)

if manual_correction:
    a = img_display.Annotation(r.roi_symbols, r.true_labels)
    a.controllers()
    a.update_labels()
    a.annotation_display()

with st.expander("See corrections"):
    controls = st.columns(2)
    row_size = st.select_slider("Row size:", range(1, 21), value=12, key='row-size-correction')
    img_display.roi_display(r.roi_symbols, a.manual_labels, row_size)

e.update_manual_labels(a.manual_labels)
e.correction()
st.write(f"Nombre d'erreurs dans le test {e.nb_erreurs} :")
st.write(e.erreurs)


st.write(st.session_state)