# trec-coding
Symbols classification for automatic correction for the coding part of the TREC psychometric test

## Streamlit app

To run app in local, use ``streamlit run treccoding.py``
Link to app on streamlit community cloud [here](https://trec-coding.streamlit.app/)

## Improvements

### CV and interface aspects

* Extraction : Display scanned resultsheet in transparency to see the grid better, and grid in black lines
* Correction : Aim of correction is to have the total number of filled boxes - number of errors
* * We can obtain this total number of filled boxes by using the mean pixel intensity : to optimize
* * maybe max/min intensity, or number of pixel below/above a certain threshold.
* Add the possibility to take a picture of the scanned result sheet
* * Need improvement of box detection even with variation in sheet dimension : try SAM or keras CV module
* Problem with number of errors, predictes labels in Model/correction pages:
* * Try distinct label names in session state


### Deep learning aspects

* Jupyter part : factorize by adding modules to import for extraction, visualisation
* * Done for training, still ongoing for annotation and correction (usefulness?)
* Confusion matrix aesthetics: normalisation on true or pred, possibility to hide diagonal
* Implement custom metrics and loss in training fit
* CNN optimization : improvements:
  * add conv layers (2x64)
  * add padding
  * modify DNN layer architecture 
  * add batch normalisation
  * l1/l2 regularization 
  * modify dropout
* Image augmentation