import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
from datetime import datetime as tm


### $ Clear all variables
### %reset -f

### $ Filename imported by field engineer
filename = 'C:/Users/sambe/Desktop/Spring 2021/M E 266KP/Given Data/testP-1605&A New dataset 2.23.21.xlsx'

### $ Convert to pandas data frame
df = pd.read_excel(filename)

### $ Get the number of rows and columns in the file (# of covariates and sampling will probably be different)
number_rows = len(df.index)
number_cols = len(df.columns)

### $ Create empty data frames with the three points per covariate (value, time, good/bad)
variables = pd.DataFrame()
time = pd.DataFrame()
goodbad = pd.DataFrame()

### $ Sort out whole excel file to place the column in the right data frame (value, time, good/bad)
### $ Relabeled with Variable i names
### $ Iterates over the number of columns
for i in range(number_cols):
    ### $ Puts column title into str
    str = df.columns[i]
    ### $ if searches for a title that starts with 'Pen Name'
    if str.startswith('Pen Name'):
        ### $ takes variables from column and puts in separate 'variables' dataframe
        s = df.iloc[1:,i]
        variables = pd.concat([variables,s.rename('Value')], axis = 1)
    ### $ elif searches for a title that starts with 'Units'
    elif str.startswith('Units'):
        ### $ takes variables from column and puts in separate 'goodbad' dataframe
        s = df.iloc[1:,i]
        goodbad = pd.concat([goodbad,s.rename('GOOD/BAD')],axis = 1)
    ### $ This is for the blank columns in between variable columns
    elif str.startswith('Unnamed'):
        ### $ Skips over empty columns
        continue
    ### $ This is an else because the pen names vary and will be different for every pump/variable
    else:
        ### $ takes variables from column and puts in separate 'time' dataframe
        s = df.iloc[1:,i]
        time = pd.concat([time,s.rename('Time')], axis = 1)

### S convers all datetime to Timestamp
for j in range(len(time.columns)):
    ### $ iterates over only rows with data (aka without nan)
    for i in range(len(time.iloc[:,j].dropna())):
        ### $ Some of the times are in datetime format
        if type(time.iloc[i,j]) == type(tm(2020, 2, 25, 11, 48, 37)):
            time.iloc[i,j] = pd.Timestamp(time.iloc[i,j])
        ### $ Some of the times are in string format, so this will convert to a timestamp if a str
        elif type(time.iloc[i,j]) == type('hey'):
            tempa = tm.strptime(time.iloc[i,j],'%m/%d/%y %H:%M:%S %p')
            tempb = tm.timestamp(tempa)
            time.iloc[i,j] = pd.Timestamp(tempb, unit = 's')
            
        ### $ I truly hope that the time does not hit this else 
        else:
            print(type(time.iloc[i,j]))
            continue
        



### $ interpolates for BAD Values
### $ Excludes last row because you can't interpolate a machine being on or off
for j in range(len(variables.columns)-1):
    for i in range(len(variables.iloc[:,j].dropna())):
        str = goodbad.iloc[i,j]
        ### $ If the value is bad and the value has no prior value to interpolate from, just use next good value
        ### $ Needs improvement: could back interpolate and take care of case in which there are consecutive bad values     
        if str.startswith('B') and i == 0:
            variables.iloc[i,j] = variables.iloc[i+1,j]
            goodbad.iloc[i,j] = 'INT'
        ### $ Else if bad, then interpolate between the two good points
        elif str.startswith('B'):
            t1 = time.iloc[i-1,j]
            t2 = time.iloc[i,j]
            t3 = time.iloc[i+1,j]
            a = variables.iloc[i-1,j]
            c = variables.iloc[i+1,j]
            variables.iloc[i,j] = ((t2-t1)/(t3-t1))*(c-a)+a
            goodbad.iloc[i,j] = 'INT'

### $ Align times via binning
### $ kappa designates the grouping size
### $ Any timestamp outside of the bin will be group later
kappaa = '1/1/00 12:10:00 AM'
tempa = tm.strptime(kappaa,'%m/%d/%y %H:%M:%S %p')
tempb = tm.timestamp(tempa)
kappaa = pd.Timestamp(tempb, unit = 's')

kappab = '1/1/00 12:00:00 AM'
tempa = tm.strptime(kappab,'%m/%d/%y %H:%M:%S %p')
tempb = tm.timestamp(tempa)
kappab = pd.Timestamp(tempb, unit = 's')

kappa = kappaa - kappab
### $ Sets to dataframes: windows and shutters. windows is the number row that is being looked at for that variable. shutters is end of the length of that variable
### $ column titles designate which variable is being investigated
windows = pd.DataFrame()
shutters = pd.DataFrame()
for j in range(len(variables.columns)):
    w = pd.DataFrame([0], columns = [f'{j}'])
    windows = pd.concat([windows, w], axis = 1)
    temp = variables.iloc[:,j]
    s = pd.DataFrame([len(temp.dropna())], columns = [f'{j}'])
    shutters = pd.concat([shutters, s], axis = 1)
    

binsize = kappa
bin = 10 # min                  ### $ Need to pick both kappa and bin, I suppose to be the same value
### $ abstime is the merged and grouped time of all the variables
abstime = pd.DataFrame([[0]], columns = ['Time'])
### $ vars is the merged and grouped variables
vars = pd.DataFrame([[0]])
### $ This creates a data frame with the exact number of columns as the number of variables
for j in range(len(variables.columns)):
    a = ['NaN']
    vars[f'Variable {j}'] = a
vars.drop(columns = [0])
### $ counter just used for progress, I guess
#counter = 
### $ Flag1 designates that this is the very first time through the while statement. This flag is used for formatting the data
Flag1 = 0
### $ This iterates until each individual variable has its respective bin
while max(shutters.iloc[0,:]-windows.iloc[0,:]) != 0:
    timenow = []
    ### $ timenow is built and designates the exact timestamps that are to be compared and binned, if possible 
    for k in range(len(variables.columns)):
        timenow.append(time.iloc[windows.iloc[0,k],k])
    ### $ now is just the earliest time in the timenow group          
    now = min(timenow)
    ### $ next we round now to the nearest bin value ### $### $### $ Really want to improve this later
    now = now.round(freq = f'{bin}T')
    ### $ a is a pd.DataFrame created to append to the abstime dataframe
    a = pd.DataFrame([[f'{now}']], columns = ['Time'])
    abstime = abstime.append(a, ignore_index = True)
    ### $ Flag0 designates that this is the first time through that specific row. This is also for formatting and allows the rest of the variables to be placed on the right row.
    Flag0 = 0
   
    for l in range(len(variables.columns)):
        ### $ Makes sure that the time is within that bin, if not the program skips any input into the time or variables dataframes
        if time.iloc[windows.iloc[0,l],l] - now <= binsize:
            ### $ If this is the first time through the row
            if Flag0 == 0:
                ### $ Appends a to a brand new row of the variables dataframe. This in affect adds a row to the dataframe
                a = pd.DataFrame([variables.iloc[windows.iloc[0,l],l]], columns = [f'Variable {l}'])
                vars = vars.append(a, ignore_index = True)
                ### $ If this is the first time throught the while statement
                if Flag1 == 0:
                    ### $ Formatting
                    vars = vars.drop(columns = [0])
                    vars = vars.drop([0])
                    Flag1 = 1
                ### $ If the time is within the bin, it assigns that variable the bin (group) time
                time.iloc[windows.iloc[0,l],l] = now
                ### $ If the time and variable make it into the bin, the window moves to the next value, one row down
                windows.iloc[0,l] +=1
                Flag0 = 1
                #counter += 1
                #print(counter)
            ### $ If this is not the first time through the row, the program does not have to append another row, but can insert the value right into the cell
            else:
                vars.iloc[windows.iloc[0,l],l] = variables.iloc[windows.iloc[0,l],l]
                time.iloc[windows.iloc[0,l],l] = now
                ### $ Still moves the window because it was binned
                windows.iloc[0,l] +=1
        ### $ If its not in the bin, ignore it.
        else:
            continue

### $ Formatting
abstime = abstime.drop([0])
### $ Also formatting
vars.index += 1


            
fixed = pd.concat([abstime,vars], axis = 1)
fixed.to_excel('interpolatedvar.xlsx')

print(fixed)






# from lifelines import CoxPHFitter
# from lifelines.datasets import load_rossi
# rossi_dataset = load_rossi()
# cph = CoxPHFitter()
# cph.fit(rossi_dataset, duration_col='week', event_col='arrest')
# cph.print_summary()
# cph.plot(hazard_ratios=True)
