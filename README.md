# trec-coding
Symbols classification for automatic correction for the coding part of the TREC psychometric test

## Streamlit app

To run app in local, use ``streamlit run treccoding.py``
Link to app on streamlit community cloud [here](https://trec-coding.streamlit.app/)

To try it, use one of the resultsheets from scan_resultsheets folder.

> Better to run community cloud app on Chrome browser.
> On Firefox, problems with file uploading can happen.

## Improvements

### CV and interface aspects

* Extraction : Display scanned resultsheet in transparency to see the grid better, and grid in black lines
* Add the possibility to take a picture of the scanned result sheet
  * Need improvement of box detection even with variation in sheet dimension : try SAM or keras CV module
* Set default label on homepage roi display

### Deep learning aspects

* Confusion matrix aesthetics: normalisation on true or pred, possibility to hide diagonal
* Implement custom metrics and loss in training fit
* Image augmentation