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


# This code segment builds the dataset that only includes the Broken Impeller
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
data_valign = data[data.label == 'Valve_Alignment']
data_norm = data[data.label == 'Normal']

data = pd.concat([data_valign, data_norm], ignore_index=True)


# This code segment creates two separate data sets, one for the labels
# and another for the features we want the machine learning model
# to use to categorize the data points

data_Y = data['label']
data_X = data.drop(['datetime','label','motor_stat'],axis=1)



# This segment is used to find the best parameters for the model. It can be ignored because the best params
# have already been found and are in the following segment of code

'''
scaler = StandardScaler()
clf = SVC()

pipe = Pipeline(steps=[('scaler', scaler), ('svc', clf)])

param_grid = {'svc__kernel': ['rbf'],
             'svc__class_weight': [{'Normal':1, 'Valve_Alignment':10, 'Cracked_Seal':10 ,'Broken_Impeller':10 ,'Broken_Valve':10 ,'Leaking_Valve':10 , 'Motor_Distorted':10 },
                                   'balanced'],
              'svc__C': [5,10,15]
             }

grid_search = GridSearchCV(pipe, param_grid, cv=5,scoring='f1_macro')
grid_search.fit(data_X, data_Y)

print('Best Params', grid_search.best_params_)
print('Best Score', grid_search.best_score_)
'''


# This code segment is used to build the first model with the 
# optimized parameters to find the misclassifications close to the 
# decision surface

scaler = StandardScaler()
clf = SVC()

pipe = Pipeline(steps=[('scaler', scaler), ('svc', clf)])

param_grid = {'svc__kernel': ['rbf'],
             'svc__class_weight': [{'Normal':1, 'Valve_Alignment':25}],
              'svc__C': [1]
             }

grid_search = GridSearchCV(pipe, param_grid, cv=5,scoring='f1_macro')
model = grid_search.fit(data_X, data_Y)

dec_func = model.decision_function(data_X)


# This is used to find the indices of the data points that are within the uncertainty margin
# and prints out the number of these points

count = 0
indexes = []
for i in range(len(dec_func)):
    if dec_func[i] < 1 and dec_func[i] > 0:
        count += 1
        indexes.append(i)
count


# This code relabels the data point within the uncertainty margin as "Broken_Valve_Warning"

for i in range(len(data_Y)):
    if i in indexes:
        data_Y[i] = "Valve_Alignment_Warning"


# This segment compiles the complete dataset and adds back the datetime and motor_stat feature to be the same
# size as the other data sets

data_X = data.drop(['label'],axis=1)
valve_alignment_data = pd.concat([data_X,data_Y], axis=1)



# This code segment converts the datetime column to a datetime object that can be used to sort chronologically

valve_alignment_data.datetime = pd.to_datetime(valve_alignment_data.datetime, yearfirst=True)
valve_alignment_data.sort_values(by='datetime')



# Did not save the data set of this failure mode because the results were too
# poor to add to the final model

'''
# Best Parameters and Results

scaler = StandardScaler()
clf = SVC(C=.1, class_weight={'Normal':1,'Valve_Alignment':25, 'Valve_Alignment_Warning':25},kernel="rbf")
pipe = Pipeline(steps=[('scaler', scaler), ('svc', clf)])

predicts = cross_val_predict(pipe, data_X, data_Y, cv=5)
print(confusion_matrix(data_Y, predicts))
print(classification_report(data_Y,predicts))
'''
