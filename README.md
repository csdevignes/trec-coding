# trec-coding
Symbols classification for automatic correction for the coding part of the TREC psychometric test

## Streamlit app

To run app in local, use ``streamlit run treccoding.py``
Link to app on streamlit community cloud [here](https://trec-coding.streamlit.app/)

## Improvements

### CV and interface aspects

* Extraction : Display scanned resultsheet in transparency to see the grid better, and grid in black lines
* Add the possibility to take a picture of the scanned result sheet
  * Need improvement of box detection even with variation in sheet dimension : try SAM or keras CV module
* Jupyter only : problem with roi_display_jup when not enough symbol to make 2 lines

### Deep learning aspects

* Confusion matrix aesthetics: normalisation on true or pred, possibility to hide diagonal
* Implement custom metrics and loss in training fit
* Image augmentation