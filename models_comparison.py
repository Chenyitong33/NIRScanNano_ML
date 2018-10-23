from xgboost import XGBClassifier
from sklearn.multiclass import OneVsRestClassifier
# Import the `svm` model
from sklearn import svm
from sklearn.model_selection import cross_validate
from sklearn.metrics import recall_score
# Import 'knn'
from sklearn.neighbors import KNeighborsClassifier
# Import 'random forest'
from sklearn.ensemble import RandomForestClassifier

from sklearn.ensemble import BaggingClassifier
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import Perceptron
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import ParameterGrid
from sklearn.tree import DecisionTreeClassifier
from sklearn.utils import check_random_state
from sklearn.neural_network import MLPClassifier

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
path = os.path.join(parent_dir, 'data_scatter')
i = 0
for filename in os.listdir(path):
    with open(os.path.join(path, filename)) as f:
        
        # Read csv file and skip the top 19 rows that not related to Absorbance
        data = pd.read_csv(f, skiprows=19)
        # Get Absorbance values and fill NA/NaN values using the 0
        #absorbance = data['Absorbance (AU)'].fillna(0).values
        absorbance = pd.to_numeric(data['Absorbance (AU)'].fillna(0))
        #print(absorbance.shape)

        # Apply Savitzky-Golay Smoothing Filters:
        filtered = scipy.signal.savgol_filter(absorbance, window_length=25, polyorder=5)
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
print('=========================================================================')
print('1. In this part, the models will be evaluated by cross validation. Get precision macro, recall macro, fit time and score time.\n')
# --------------------------- Cross Validation -------------------------------
warnings.filterwarnings("ignore", category=sklearn.exceptions.UndefinedMetricWarning)
print("Default SVM Cross Validation:")
scoring = ['precision_macro', 'recall_macro']
clf = svm.SVC()
scores = cross_validate(clf, X_train, y_train, scoring=scoring, cv=5, return_train_score=False)
print("SVM test_precision_macro", scores['test_precision_macro'])
print("SVM test_recall_macro", scores['test_recall_macro'])
print("SVM average fit time", scores['fit_time'].mean())
print("SVM average score time", scores['score_time'].mean())
# The mean score and the 95% confidence interval of the score estimate are hence given by:
print("SVM Accuracy: %0.2f (+/- %0.2f)" % (scores['test_precision_macro'].mean(), scores['test_precision_macro'].std() * 2))
print('\n')

print("Tuned SVM Cross Validation:")
scoring = ['precision_macro', 'recall_macro']
clf = svm.SVC(C=2., gamma=0.5, kernel='poly', degree=2, probability=True)
scores = cross_validate(clf, X_train, y_train, scoring=scoring, cv=5, return_train_score=False)
print("SVM test_precision_macro", scores['test_precision_macro'])
print("SVM test_recall_macro", scores['test_recall_macro'])
print("SVM average fit time", scores['fit_time'].mean())
print("SVM average score time", scores['score_time'].mean())
# The mean score and the 95% confidence interval of the score estimate are hence given by:
print("SVM Accuracy: %0.2f (+/- %0.2f)" % (scores['test_precision_macro'].mean(), scores['test_precision_macro'].std() * 2))
print('\n')

print("Default KNN Cross Validation:")
scoring = ['precision_macro', 'recall_macro']
clf = KNeighborsClassifier()
scores = cross_validate(clf, X_train, y_train, scoring=scoring, cv=5, return_train_score=False)
print("KNN test_precision_macro", scores['test_precision_macro'])
print("KNN test_recall_macro", scores['test_recall_macro'])
print("KNN average fit time", scores['fit_time'].mean())
print("KNN average score time", scores['score_time'].mean())
# The mean score and the 95% confidence interval of the score estimate are hence given by:
print("KNN Accuracy: %0.2f (+/- %0.2f)" % (scores['test_precision_macro'].mean(), scores['test_precision_macro'].std() * 2))
print('\n')

print("Default RF Cross Validation:")
scoring = ['precision_macro', 'recall_macro']
clf = RandomForestClassifier()
scores = cross_validate(clf, X_train, y_train, scoring=scoring, cv=5, return_train_score=False)
print("RF test_precision_macro", scores['test_precision_macro'])
print("RF test_recall_macro", scores['test_recall_macro'])
print("RF average fit time", scores['fit_time'].mean())
print("RF average score time", scores['score_time'].mean())
# The mean score and the 95% confidence interval of the score estimate are hence given by:
print("RF Accuracy: %0.2f (+/- %0.2f)" % (scores['test_precision_macro'].mean(), scores['test_precision_macro'].std() * 2))
print('\n')

print("Tuned XGBoost Cross Validation:")
scoring = ['precision_macro', 'recall_macro']
clf = OneVsRestClassifier(XGBClassifier(
 learning_rate=0.2,
 random_state=3,
 n_estimators=500,
 subsample=0.8,
 colsample_bytree=0.8,
 max_depth=5,
 objective= 'multi:softmax',
 num_class=25))
scores = cross_validate(clf, X_train, y_train, scoring=scoring, cv=5, return_train_score=False)
print("XGBoost test_precision_macro", scores['test_precision_macro'])
print("XGBoost test_recall_macro", scores['test_recall_macro'])
print("XGBoost average fit time", scores['fit_time'].mean())
print("XGBoost average score time", scores['score_time'].mean())
# The mean score and the 95% confidence interval of the score estimate are hence given by:
print("XGBoost Accuracy: %0.2f (+/- %0.2f)" % (scores['test_precision_macro'].mean(), scores['test_precision_macro'].std() * 2))
print('\n')

print('========================================================================')
print('2. In this part, the models will be evaluated by a held-out test set. Get fit time, score time and accuracy.\n')

# ---------------------------- default SVM -----------------------------
# Create the SVC model 
svc_dmodel = svm.SVC()
t0=time.time()
# print(t0)
# Fit the data to the SVC model
svc_dmodel.fit(X_train, y_train)
print("Default SVC training time:", time.time()-t0, "s")
# ---------------------------- tuning parameteres -----------------------------
# Create the SVC model 
svc_model = svm.SVC(C=2., gamma=0.5, kernel='poly', degree=2, probability=True)
t0=time.time()
# print(t0)
# Fit the data to the SVC model
svc_model.fit(X_train, y_train)
print("Tuned SVC training time:", time.time()-t0, "s")
'''
#------------------------- SVM candidates ----------------------------
print("SVC candidates:")
# Set the parameter candidates
parameter_candidates = [
    {'C': [1, 10, 100, 1000], 'kernel': ['linear']},
    {'C': [1, 10, 100, 1000], 'gamma': [0.5,0.1,0.01, 0.001], 'kernel': ['rbf']},
    {'C': [1, 10, 100, 1000], 'gamma': [0.5,0.1,0.01, 0.001], 'kernel': ['poly']},
]

# Create a classifier with the parameter candidates
clf_grid = GridSearchCV(estimator=svm.SVC(), param_grid=parameter_candidates, n_jobs=1)

# Train the classifier on training data
clf_grid.fit(X_train, y_train)

# Print out the results
#print('Best score for training data:', clf.best_score_)
print('Best `C`:',clf_grid.best_estimator_.C)
print('Best kernel:',clf_grid.best_estimator_.kernel)
print('Best `gamma`:',clf_grid.best_estimator_.gamma)

# Apply the classifier to the test data, and view the accuracy score
print('Best score:',clf_grid.best_score_)
print('\n')
'''
# ---------------------------- KNN ---------------------------------
# Create the default KNN model 
knn_model = KNeighborsClassifier()
t0=time.time()
# print(t0)
# Fit the data to the SVC model
knn_model.fit(X_train, y_train)
print("Default KNN training time:", time.time()-t0, "s")
# ---------------------------- RF ---------------------------------
# Create the default RF model 
rf_model = RandomForestClassifier()
t0=time.time()
# print(t0)
# Fit the data to the SVC model
rf_model.fit(X_train, y_train)
print("Default RF training time:", time.time()-t0, "s")
#---------------------------- XGBoost ------------------------------
classif = OneVsRestClassifier(XGBClassifier(
 learning_rate=0.2,
 random_state=3,
 n_estimators=500,
 subsample=0.8,
 colsample_bytree=0.8,
 max_depth=5,
 objective= 'multi:softmax',
 num_class=25))
t1=time.time()
classif.fit(X_train,y_train)
print("Tuned XGBoost training time:", time.time()-t1, "s")
print("\n")
# --------------------------- test -----------------------------

X_test = pd.DataFrame(columns=col)
y_test = pd.DataFrame(columns=['Type'])


# Loop through all the csv files and read their data.
path = os.path.join(parent_dir, 'test')
i = 0
for filename in os.listdir(path):
    with open(os.path.join(path, filename)) as f:
        
        data = pd.read_table(f, sep=",", skiprows=19)
        absorbance = pd.to_numeric(data['Absorbance (AU)'].fillna(0))
        
        # filtered <- filter(sgolay(p=3, n=11, m=0),absorbance)
        filtered = scipy.signal.savgol_filter(absorbance, window_length=11, polyorder=3)

        # filtered <- scale(t(filtered),center=TRUE)
        filtered = scale(np.transpose(filtered))
        
        # features <- c(filtered,diff(filtered))
        features = np.concatenate([filtered, np.diff(filtered)])

        # features = np.append(features, filename.split('O1')[0])
        X_test.loc[i] = features
        y_test.loc[i] = filename.split('O1')[0]
        #print(svc_model.predict([X_test.loc[i]]),y_test.loc[i],round(np.amax(svc_model.predict_proba([X_test.loc[i]])), 3),'\n')
        i = i + 1

# test_X.dropna(how='any')    #to drop if any value in the row has a nan
y_test['Type'].astype('category')
y_test = np.ravel(y_test)
t1=time.time()
q = svc_dmodel.score(X_test, y_test)
print("Default SVM score time:", time.time()-t1, "s")
t1=time.time()
x = svc_model.score(X_test, y_test)
print("Ideal SVM score time:", time.time()-t1, "s")
t1=time.time()
z = knn_model.score(X_test, y_test)
print("Default KNN score time:", time.time()-t1, "s")
t1=time.time()
y = classif.score(X_test, y_test)
print("Tuned XGBoost score time:", time.time()-t1, "s")
t1=time.time()
k = rf_model.score(X_test, y_test)
print("Default RF score time:", time.time()-t1, "s")
print('\n')

print("Default SVM accuracy is ", q)
print("Ideal SVM accuracy is ", x)
#print('Best accuracy from SVM search candidates:',clf_grid.score(X_test, y_test))
print("Default KNN accuracy is", z)
print("Default RF accuracy is", k)
print("Default XGBoost accuracy is", y)

'''
#============================ Save models ==============================
# Set working directory 
os.chdir(os.path.join(parent_dir, 'model'))
# save the model to disk
filename = 'finalized_model.sav'
pickle.dump(svc_model, open(filename, 'wb'))

filename = 'xgboost_model.sav'
pickle.dump(classif, open(filename, 'wb'))
'''

print('=========================================================================')
print('3. In this part, test Bagging classifier.\n')
#=========================== Bagging ===============================
def test_bagging():
    # Check classification for various parameter settings.
    rng = check_random_state(0)
    grid = ParameterGrid({"max_samples": [0.5, 1.0],
                          "max_features": [1, 2, 4],
                          "bootstrap": [True, False],
                          "bootstrap_features": [True, False]})

    for base_estimator in [None,
                           DummyClassifier(),
                           #Perceptron(),
                           MLPClassifier(),
                           KNeighborsClassifier(),
                           DecisionTreeClassifier(),
                           svm.SVC(C=2., gamma=0.5, kernel='poly', degree=2, probability=False)]:
        print(base_estimator)
        for params in grid:
            print(params)
            print(BaggingClassifier(base_estimator=base_estimator,
                              random_state=rng,
                              **params).fit(X_train, y_train).score(X_test, y_test),'\n')

test_bagging()

                              

