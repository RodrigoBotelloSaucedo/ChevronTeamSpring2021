from datetime import datetime, timedelta
import csv
import pandas as pd
import random as r
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import cross_val_score
from sklearn.metrics import f1_score, make_scorer, balanced_accuracy_score
import pickle
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report

# This code segment builds the dataset that only includes the broken
# and normal data

col_names = []
for i in range(8):
    if i ==0:
        col_names.append('datetime')
    if i == 1:
        col_names.append('x_vibration')
    if i == 2:
        col_names.append('suction_pressure')
    if i == 3:
        col_names.append('discharge_pressure')
    if i == 4:
        col_names.append('discharge_flow')
    if i == 5:
        col_names.append('y_vibration')
    if i == 6:
        col_names.append('motor_stat')
    if i == 7:
        col_names.append('label')

data = pd.read_csv("labeled_data.csv", names = col_names)
data = data[data.motor_stat != 'Off']


data_normal = data[data['label'] == 'Normal']
data_broken = data[data['label'] != 'Normal']
data_reduced = pd.concat([data_broken, data_normal_reduced], ignore_index=True)


# This code segment creates two separate data sets, one for the labels
# and another for the features we want the machine learning model
# to use to categorize the data points

data_Y = data_reduced['label']
data_X = data_reduced.drop(['datetime','label','motor_stat'],axis=1)


# This segment is used to find the best parameters for the model. It can be ignored because the best params
# have already been found and are in the following segment of code
'''
scaler = StandardScaler()
clf = SVC()

pipe = Pipeline(steps=[('scaler', scaler), ('svc', clf)])

param_grid = {'svc__kernel': ['rbf'],
             'svc__class_weight': [{'Normal':1, 'Broken':30},
                                   {'Normal':1, 'Broken':25}],
              'svc__C': [1]
             }

grid_search = GridSearchCV(pipe, param_grid, cv=5,scoring='f1_macro')
grid_search.fit(data_X, data_Y)

print('Best Params', grid_search.best_params_)
'''

### Best Parameters found, this segment prints the confusion matrix and 
# classification report for this model.
scaler = StandardScaler()
clf = SVC(C=3, class_weight={'Normal':1, 'Broken':30},kernel="rbf")
pipe = Pipeline(steps=[('scaler', scaler), ('svc', clf)])

predicts = cross_val_predict(pipe, data_X, data_Y, cv=10)
print(confusion_matrix(data_Y, predicts))
print(classification_report(data_Y,predicts))




