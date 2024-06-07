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
* Problem with number of errors, predicted labels in Model/correction pages: cannot repeat so far.
* Jupyter only : problem with roi_display_jup when not enough symbol to make 2 lines
* Correction of grid : problem with color of boxes for errors : red/blue
* Adapt visualisation functions so that they can be used also in model

### Deep learning aspects

* Confusion matrix aesthetics: normalisation on true or pred, possibility to hide diagonal
* Implement custom metrics and loss in training fit
* Image augmentation