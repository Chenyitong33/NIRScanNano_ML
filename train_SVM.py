
# Import the `svm` model
from sklearn import svm
from sklearn.model_selection import cross_validate
from sklearn.metrics import recall_score

import os
import numpy as np
import pandas as pd
import scipy.signal
from sklearn.preprocessing import scale
import pickle
import time
from os.path import dirname
import warnings
import sklearn.exceptions

# Global: the number of frequency bands we have
F = 228

# For each sample we use 2 spetra to improve classification. The 2nd spectrum uses -1 because we use the diff() filter
FREQ = 2 * F - 1

# define Standard Normal Variate 
snv = lambda x:(x-x.mean())/x.std()

# get path of the current script
this_dir = os.path.realpath(__file__)
parent_dir = dirname(this_dir)

# create a data frame to hold all absorbance values
# need an extra column at the start to hold "type" (i.e. the thing we are trying to predict)
col=["column"+str(i) for i in range(1,FREQ+1)]
X_train = pd.DataFrame(columns=col)
y_train = pd.DataFrame(columns=['Type'])


# Loop through all the csv files and read their data.
path = os.path.join(parent_dir, 'training')
i = 0
for filename in os.listdir(path):
    with open(os.path.join(path, filename)) as f:
        
        # Read csv file and skip the top 19 rows that not related to Absorbance
        data = pd.read_csv(f, skiprows=19)
        # Get Absorbance values and fill NA/NaN values using the 0
        absorbance = data['Absorbance (AU)'].fillna(0).values
        #print(absorbance.shape)

        # Apply Savitzky-Golay Smoothing Filters:
        filtered = scipy.signal.savgol_filter(absorbance, window_length=11, polyorder=3)
        # Apply Standard Normal Variate Filters:
        filtered = snv(filtered)
        # Apply differentials and concate to original filtered features
        features = np.concatenate([filtered, np.diff(filtered)])

        # features = np.append(features, filename.split('O1')[0])
        X_train.loc[i] = features
        y_train.loc[i] = filename.split('O1')[0]
        i = i + 1

path = os.path.join(parent_dir, 'feedback')
for filename in os.listdir(path):
    with open(os.path.join(path, filename)) as f:
        
        # Read csv file and skip the top 19 rows that not related to Absorbance
        data = pd.read_csv(f)
        # Get Absorbance values and fill NA/NaN values using the 0
        absorbance = data['Absorbance'].fillna(0).values
        #print(absorbance.shape)

        # Apply Savitzky-Golay Smoothing Filters:
        filtered = scipy.signal.savgol_filter(absorbance, window_length=11, polyorder=3)
        # Apply Standard Normal Variate Filters:
        filtered = snv(filtered)
        # Apply differentials and concate to original filtered features
        features = np.concatenate([filtered, np.diff(filtered)])

        # features = np.append(features, filename.split('O1')[0])
        X_train.loc[i] = features
        y_train.loc[i] = filename.split('O1')[0]
        i = i + 1

y_train['Type'].astype('category')
y_train = np.ravel(y_train)
#print(X_train)
#print(y_train)

# ----------------------------SVC--------------------------------
# Import the `svm` model
from sklearn import svm

# Create the SVC model 
svc_model = svm.SVC(C=.1, gamma=0.5, kernel='poly', degree=2, probability=True)

t0=time.time()
#print(t0)
# Fit the data to the SVC model
svc_model.fit(X_train, y_train)
print("training time:", time.time()-t0, "s")
'''
# ---------------------------test-------------------------------
l = ['Col'] * FREQ
X_test = pd.DataFrame(columns=l)
y_test = pd.DataFrame(columns=['Type'])


# Loop through all the csv files and read their data.
path = os.path.join(parent_dir, 'test')

i = 0
for filename in os.listdir(path):
    with open(os.path.join(path, filename)) as f:
        # fileName = fileList[i]
        data = pd.read_table(f, sep=",", skiprows=19)
        absorbance = pd.to_numeric(data['Absorbance (AU)'].fillna(0))
        # filtered <- filter(sgolay(p=3, n=11, m=0),absorbance)
        filtered = scipy.signal.savgol_filter(absorbance, window_length=11, polyorder=3)

        # filtered <- scale(t(filtered),center=TRUE)
        filtered = scale(np.transpose(filtered))

        # Access the attribute 'scaled:center'
        # filtered <- attr(filtered,"scaled:center")
        # features <- c(filtered,diff(filtered))
        # filtered = filtered.reshape(1,228)
        # print(filtered.shape)
        # print(np.diff(filtered).shape)
        features = np.concatenate([filtered, np.diff(filtered)])

        # features = np.append(features, filename.split('O1')[0])
        X_test.loc[i] = features
        y_test.loc[i] = filename.split('O1')[0]
        i = i + 1

# test_X.dropna(how='any')    #to drop if any value in the row has a nan
y_test['Type'].astype('category')

t1=time.time()
x = svc_model.score(X_test, y_test)
print("test time:", time.time()-t1, "s")
print("accuracy is ", x)
'''

# Set working directory
#os.chdir(r'C:\Users\frankie\Desktop\research project\ML_part\r\model')
os.chdir(os.path.join(parent_dir, 'model'))
# save the model to disk
filename = 'finalized_model.sav'
pickle.dump(svc_model, open(filename, 'wb'))
