# trec-coding
Symbols classification for automatic correction for the coding part of the TREC psychometric test

## Streamlit app

To run app in local, use ``streamlit run treccoding.py``
Link to app on streamlit community cloud [here](https://trec-coding.streamlit.app/)

## Improvements

* Extraction : Add possibility to loop in threshold up or down (in case of detection problem)
* Extraction : Display scanned resultsheet in transparency to see the grid better, and grid in black lines
* Correction : Aim of correction is to have the total number of filled boxes - number of errors
* * We can obtain this total number of filled boxes by using the mean pixel intensity