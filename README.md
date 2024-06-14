# trec-coding
Symbols classification for automatic correction for the coding part of the TREC psychometric test

## Streamlit app

To run app in local, use ``streamlit run treccoding.py``
Link to app on streamlit community cloud [here](https://trec-coding.streamlit.app/)

To try it, use one of the resultsheets from scan_resultsheets folder.

> Better to run community cloud app on Chrome browser.
> On Firefox, problems with file uploading can happen.

## Jupyter notebooks

* SymbolsAnnotation and SymbolsCorrection follow the same workflow as the streamlit app, but in a notebook format
* SymbolsTraining is used for hyperparameters tuning and training of the neural network
* SymbolsDataAugmentation is used to generate new pictures to increase the dataset size, and train again the model

## Workflow of the app

For a classic workflow starting from a scan of a test resultsheet, first detect the boxes coordinates 
and then extract region of interest (ROI), the pixels contained inside the coordinates (the symbols).
All these steps are performed on the homepage `treccoding.py`.
Then there are two options :
* if you just want to annotate data and save it as .csv, use `Annotation` page
* if you want to correct a resultsheet and obtain a score, use `Correction` page
  * there you can first run automatic correction using the model
  * if the automatic correction is not satisfying, you can adjust it manually
  * it is always possible to save this as a .csv dataset containing symbols + correct labels

> Score is calculated as : number of filled boxes - number of errors

An alternative workflow consists in going directly to the `Modele` page. There it is possible to load the train
dataset or the test dataset. Or upload a .csv file containing a dataset with the same format as the one used to save
in the other pages, meaning :
* one line per image
* each line contain the flatten pixel values (0-255), of an image of shape width = 76 and height = 82
* last column of the line is the label of the image (0-9, 0 meaning error : unexisting symbol)

From there all the available models can be evaluated, by running prediction and calculating metrics and confusion
table. Best model so far is `CNN_10-0.996_20240611_t2.keras`

## Improvements

### CV and interface aspects

* Extraction : Display scanned resultsheet in transparency to see the grid better, and grid in black lines
* Add the possibility to take a picture of the scanned result sheet
  * Need improvement of box detection even with variation in sheet dimension : try SAM or keras CV module
* Label management issues :
  * Set default label on homepage roi display
  * Empty boxes exclusion may cause problems in annotation / correction, due to the callback function used

### Deep learning aspects

* Encoding of labels
* Confusion matrix aesthetics: normalisation on true or pred, possibility to hide diagonal
* Implement custom metrics and loss in training fit
* Image augmentation for error generation