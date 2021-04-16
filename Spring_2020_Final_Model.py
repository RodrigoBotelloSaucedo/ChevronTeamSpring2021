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

'''
This first large code segment is used to build the compiled_data.csv file
that is used to build the complete model

The next four segments read in the csv data from each relabeled file
'''

# Open file m_dis.csv as f. with statement is used to not have to close the file later
with open('m_dis.csv', newline='') as f:
    # csv.reader(csvfile) will return a reader object 
    #which will iterate over lines in the given csvfile
    reader = csv.reader(f)
    
    # Creates a list of lists [[10,1],[9,2],[8,3]]
    m_dis_data = list(reader)

with open('b_imp.csv', newline='') as f:
    reader = csv.reader(f)
    b_imp_data = list(reader)

with open('l_valve.csv', newline='') as f:
    reader = csv.reader(f)
    l_valve_data = list(reader)

with open('b_valve.csv', newline='') as f:
    reader = csv.reader(f)
    b_valve_data = list(reader)


# The next four segments change the datetime from each csv data from 
# strings into datetime objeccts so that they can be organized when compiled


for i in range(len(m_dis_data)):

    # Iterates through each line in the csv or list in this case
    # [i] in this case is the list within a list, [0] is the  date stap im guessing
    # it would be the first column in the csv [0:4] they are slicing the string or whatever is 
    # in the column
    year = int(m_dis_data[i][0][0:4])
    month = int(m_dis_data[i][0][5:7])
    day = int(m_dis_data[i][0][8:10])
    hour = int(m_dis_data[i][0][11:13])
    minute = int(m_dis_data[i][0][14:16])
    seconds = int(m_dis_data[i][0][17:19])
    # they reformat the [row][first column]
    m_dis_data[i][0] = datetime(year,month,day,hour,minute,seconds)

for i in range(len(b_imp_data)):

    year = int(b_imp_data[i][0][0:4])
    month = int(b_imp_data[i][0][5:7])
    day = int(b_imp_data[i][0][8:10])
    hour = int(b_imp_data[i][0][11:13])
    minute = int(b_imp_data[i][0][14:16])
    seconds = int(b_imp_data[i][0][17:19])
    b_imp_data[i][0] = datetime(year,month,day,hour,minute,seconds)

for i in range(len(l_valve_data)):

    year = int(l_valve_data[i][0][0:4])
    month = int(l_valve_data[i][0][5:7])
    day = int(l_valve_data[i][0][8:10])
    hour = int(l_valve_data[i][0][11:13])
    minute = int(l_valve_data[i][0][14:16])
    seconds = int(l_valve_data[i][0][17:19])
    l_valve_data[i][0] = datetime(year,month,day,hour,minute,seconds)

for i in range(len(b_valve_data)):

    year = int(b_valve_data[i][0][0:4])
    month = int(b_valve_data[i][0][5:7])
    day = int(b_valve_data[i][0][8:10])
    hour = int(b_valve_data[i][0][11:13])
    minute = int(b_valve_data[i][0][14:16])
    seconds = int(b_valve_data[i][0][17:19])
    b_valve_data[i][0] = datetime(year,month,day,hour,minute,seconds)

'''
This segment initializes a matrix that is organized by time bins of 2 minutes
so that the data can be compiled in an organized fashion
'''
#datetime is a timestamp function I imagine, block below would be their time range
start_time = datetime(2018,2,20,15,0,0)
end_time = datetime(2020,2,20,15,0,0)
time_bins = []


while start_time < end_time:
    temp_time = start_time
    # They add 2 minutes to the start time
    start_time += timedelta(minutes = 2, seconds=0)
    # append the temp_time to the time_bins
    time_bins.append([temp_time])
  
# I think these are sets  
warning_labels = {'Motor_Distorted_Warning','Broken_Impeller_Warning','Leaking_Valve_Warning','Broken_Valve_Warning'}
broken_labels = {'Motor_Distorted','Broken_Impeller','Leaking_Valve','Broken_Valve','Cracked_Seal','Valve_Alignment'}

j = 0

for i in range(len(time_bins)):
    # If the time is the same
    if time_bins[i][0] == m_dis_data[j][0]:
        # Fill up the time bins 
        time_bins[i] = m_dis_data[j]
        
        j += 1

j = 0

for i in range(len(time_bins)):
    # if the time is the same
    if time_bins[i][0] == b_imp_data[j][0]:
        if len(time_bins[i]) == 1:
            time_bins[i] = b_imp_data[j]
            
        else:
            if time_bins[i][7] in warning_labels and b_imp_data[j][7] in broken_labels:
                time_bins[i][7] = b_imp_data[j][7]
            elif time_bins[i][7] == "Normal":
                time_bins[i][7] = b_imp_data[j][7] 
            
        j += 1
        

j = 0

for i in range(len(time_bins)):
    
    if time_bins[i][0] == b_valve_data[j][0]:
        if len(time_bins[i]) == 1:
            time_bins[i] = b_valve_data[j]
        else:
            if time_bins[i][7] in warning_labels and b_valve_data[j][7] in broken_labels:
                time_bins[i][7] = b_valve_data[j][7]
            elif time_bins[i][7] == "Normal":
                time_bins[i][7] = b_valve_data[j][7]
                  
        j += 1
    
j = 0

for i in range(len(time_bins)):
    
    if time_bins[i][0] == l_valve_data[j][0]:
        if len(time_bins[i]) == 1:
            time_bins[i] = l_valve_data[j]
        else:
            if time_bins[i][7] in warning_labels and l_valve_data[j][7] in broken_labels:
                time_bins[i][7] = l_valve_data[j][7]
                
            elif time_bins[i][7] == "Normal":
                time_bins[i][7] = l_valve_data[j][7]
                            
        j += 1
        

for i in range(len(time_bins)):
    
    if len(time_bins[i]) == 1:
        time_bins[i] = [time_bins[i][0],'Off','Off','Off','Off','Off','Off','Off']


with open('compiled_data.csv', 'w', newline='', encoding="utf-8") as csvfile:
    fieldnames = ['datetime','x vib', 's pressure', 'd pressure', 'flowrate', 'y vibration','motor stat','label']
    writer = csv.DictWriter(csvfile, fieldnames = fieldnames)

    for i in range(len(time_bins)):
        writer.writerow({'datetime':time_bins[i][0],'x vib':time_bins[i][1],'s pressure':time_bins[i][2],'d pressure':time_bins[i][3],'flowrate':time_bins[i][4],'y vibration':time_bins[i][5],'motor stat':time_bins[i][6],'label':time_bins[i][7]})

'''
This second large segment creates the final model and saves it in the file
complete_model.sav which can be called later on without having to rebuild it
'''
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

data = pd.read_csv("compiled_data.csv", names = col_names)
data = data[data.motor_stat != 'Off']

data_Y = data['label']
data_X = data.drop(['datetime','label','motor_stat'],axis=1)


### Best Parameters found so far, this segment prints the confusion matrix and 
# classification report for this model.

scaler = StandardScaler()
clf = SVC(C=1, class_weight={'Normal':1,'Broken_Impeller':25 ,'Broken_Valve':25 ,'Leaking_Valve':25 , 'Motor_Distorted':25,'Broken_Impeller_Warning':25, 'Motor_Distorted_Warning':25,'Leaking_Valve_Warning':25,'Broken_Valve_Warning':25 },kernel="rbf")
pipe = Pipeline(steps=[('scaler', scaler), ('svc', clf)])

predicts = cross_val_predict(pipe, data_X, data_Y, cv=10)
print(confusion_matrix(data_Y, predicts))
print(classification_report(data_Y,predicts))

# This code segment builds the final model. The best parameters were already found


scaler = StandardScaler()
clf = SVC()

pipe = Pipeline(steps=[('scaler', scaler), ('svc', clf)])

param_grid = {'svc__kernel': ['rbf'],
             'svc__class_weight': [{'Normal':1,'Broken_Impeller':25 ,'Broken_Valve':25 ,'Leaking_Valve':25 , 'Motor_Distorted':25,'Broken_Impeller_Warning':25, 'Motor_Distorted_Warning':25,'Leaking_Valve_Warning':25,'Broken_Valve_Warning':25 }],
              'svc__C': [1]
             }

grid_search = GridSearchCV(pipe, param_grid, cv=5,scoring='f1_macro')
model = grid_search.fit(data_X, data_Y)

filename = 'Final_Model.sav'
pickle.dump(model, open(filename, 'wb'))


# This last code segment is used to have the model predict new data.
# Data is read from a csv file names new_data.csv but this name can be changed.
# It is important that there aren't headers in this file and the columns
# are in the order: x_vibration, suction_pressure, discharge_pressure, 
# discharge_flow, and y_vibration otherwise it will not work.


with open('new_data.csv', newline='') as f:
    reader = csv.reader(f)
    new_data = list(reader)

loaded_model = pickle.load(open('Final_Model.sav', 'rb'))

results = {}

pred = loaded_model.predict(new_data)

for i in range(len(pred)):
    
    if pred[i] in results:
        results[pred[i]] += 1
    
    else:
        results[pred[i]] = 1
        
print(results)

