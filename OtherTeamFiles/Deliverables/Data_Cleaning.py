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

# This file cleans the data provided by Mr. Barrios. The Boris_Data_reduced.csv file is the same file he
# shared with us but the suction level and pump choke differential columns are removed.


# This code segment reads in the csv data 
with open('Boris_Data_reduced.csv', newline='') as f:
    reader = csv.reader(f)
    data = list(reader)

# This code segment converts the datetime columns into datatime objects so that they can be used in logic statements
# It also converts the sensor data columns from strings to floats and fills in missing cells with the value above them
for i in range(len(data)):
    if i == 0:
        continue

    for j in range(len(data[i])):
        if j % 2 == 0:
            if data[i][j] == '':
                data[i][j] = float('nan')
            else:
                year = int(data[i][j][0:4])
                month = int(data[i][j][5:7])
                day = int(data[i][j][8:10])
                hour = int(data[i][j][11:13])
                minute = int(data[i][j][14:16])
                seconds = int(data[i][j][17:19])
                data[i][j] = datetime(year,month,day,hour,minute,seconds)

        else:
            
            if data[i][j] == '':
                data[i][j] = data[i-1][j]
            elif data[i][j] == 'On' or data[i][j] == 'Off':
                data[i][j] = data[i][j]
            else:
                data[i][j] = float(data[i][j])


# This code segment initializes a standard matrix with a column of 2 minute time intervals to organize the data points in a standardized manner
# so that each column is the same length
time_bins = []
start_time = datetime(2018,2,20,15,0,0)
end_time = datetime(2020,2,20,15,0,0)

i = 1
j = 1
k = 1
l = 1
m = 1
n = 1
while start_time < end_time:
    temp_time = start_time
    start_time += timedelta(minutes = 2, seconds=0)
    
    while data[i][0] < start_time and data[i][0] >= temp_time:
        x_vib = data[i][1]
        i+=1
    while data[j][2] < start_time and data[j][2] >= temp_time:
        s_pres = data[j][3]
        j+=1
    while data[k][4] < start_time and data[k][4] >= temp_time:
        d_pres = data[k][5]
        k+=1
    while data[l][6] < start_time and data[l][6] >= temp_time:
        d_flow = data[l][7]
        l+=1
    while data[m][8] < start_time and data[m][8] >= temp_time:
        y_vib = data[m][9]
        m+=1
    while data[n][10] < start_time and data[n][10] >= temp_time:
        motor_stat = data[n][11]
        n+=1

    time_bins.append([temp_time, x_vib, s_pres, d_pres, d_flow, y_vib, motor_stat, None])


# This code segment labels the data. The timeframes start at the repair date and go back until two days of 
# data points with the motor on are within the timeframe. This was done through testing and we have not included 
# this to simplify the code.
for i in range(len(time_bins)):

    if time_bins[i][0] < datetime(2018,9,20,0,0,0):
        time_bins[i][7] = "Normal"
    elif time_bins[i][0] > datetime(2018,9,22) and time_bins[i][0] < datetime(2018,9,24):
        time_bins[i][7] = "Valve_Alignment"
    elif time_bins[i][0] > datetime(2019,3,6) and time_bins[i][0] < datetime(2019,3,8):
        time_bins[i][7] = "Cracked_Seal"
    elif time_bins[i][0] > datetime(2019,4,10) and time_bins[i][0] < datetime(2019,5,30,12):
        time_bins[i][7] = "Broken_Impeller"
    elif time_bins[i][0] > datetime(2019,5,30,12) and time_bins[i][0] < datetime(2019,6,16):
        time_bins[i][7] = "Broken_Valve"
    elif time_bins[i][0] > datetime(2019,7,23) and time_bins[i][0] < datetime(2019,8,6):
        time_bins[i][7] = "Leaking_Valve"
    elif time_bins[i][0] > datetime(2019,9,22) and time_bins[i][0] < datetime(2019,10,1):
        time_bins[i][7] = "Motor_Distorted"
    else:
        time_bins[i][7] = "Normal"

# This segment writes the cleaned and labeled dataset into a csv file. The headers are not included because it messes with the ML algorithms
# but the order is: datetime, x vibration, suction pressure, discharge pressure, flow rate, y vibration, motor status, and the label.
with open('labeled_data.csv', 'w', newline='', encoding="utf-8") as csvfile:
    fieldnames = ['datetime','x vib', 's pressure', 'd pressure', 'flowrate', 'y vibration','motor stat','label']
    writer = csv.DictWriter(csvfile, fieldnames = fieldnames)

    for i in range(len(time_bins)):
        writer.writerow({'datetime':time_bins[i][0],'x vib':time_bins[i][1],'s pressure':time_bins[i][2],'d pressure':time_bins[i][3],'flowrate':time_bins[i][4],'y vibration':time_bins[i][5],'motor stat':time_bins[i][6],'label':time_bins[i][7]})

