
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime as tm


### $ Clear all variables
%reset -f

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
for i in range(number_cols):
    # print(df.columns[i])
    str = df.columns[i]
    if str.startswith('Pen Name'):
        # print('pen')
        variables = pd.concat([variables,df.iloc[1:,i]], axis = 1)
        
    elif str.startswith('Units'):
        # print('units')
        goodbad = pd.concat([goodbad,df.iloc[1:,i]],axis = 1)
    ### $ This is for the blank columns in between variable columns
    elif str.startswith('Unnamed'):
        # print('unnamed')
        continue
    ### $ This is an else because the pen names vary and will be different for every pump/variable
    else:
        # print('datetime')
        # print(df.iloc[:,i])
        time = pd.concat([time,df.iloc[1:,i]], axis = 1)

### convert all datetime into Timestamp
for j in range(len(time.columns)):
    for i in range(len(time.iloc[:,j])):
        ### $ Some of the datetimes are in string format sometimes, so this will convert to a timestamp if a str
        if type(time.iloc[i,j]) == type('hey'):#type(time.iloc[i,j]) == str:
            tempa = tm.strptime(time.iloc[i,j],'%m/%d/%y %H:%M:%S %p')
            tempb = tm.timestamp(tempa)
            time.iloc[i,j] = pd.Timestamp(tempb, unit = 's')
            
            
            
                   



### interpolate for BAD values
for j in range(len(variables.columns)):
    for i in range(len(variables.iloc[:,j].dropna())):
        str = goodbad.iloc[i,j]
        # print(i,j)
        ### $ If the value is bad and the value has no prior value to interpolate from, just use next good value
        ### $ Needs improvement: could back interpolate and take care of case in which there are consecutive bad values     
        if str.startswith('B') and i == 0:
            variables.iloc[i,j] = variables.iloc[i+1,j]
        ### $ Else if bad, then interpolate between the two good points
        elif str.startswith('B'):
            t1 = time.iloc[i-1,j]
            t2 = time.iloc[i,j]
            t3 = time.iloc[i+1,j]
            a = variables.iloc[i-1,j]
            c = variables.iloc[i+1,j]
            variables.iloc[i,j] = ((t2-t1)/(t3-t1))*(c-a)+a
            
fixed = pd.DataFrame()
for i in range(len(variables.columns)):
    fixed = pd.concat([fixed, time.iloc[:,i], variables.iloc[:,i], goodbad.iloc[:,i]], axis = 1)            
fixed.to_excel('interpolatedvar.xlsx')

# variables.dropna()
# goodbad.dropna()
# time.dropna()



# counter = 0
# for i in range(len(goodbad.columns)):
#     for j in range(len(goodbad)):
#         str = goodbad.iloc[j,i]
#         if str.startswith('B'):
#             print('bad')
#             print(j,i)
#             counter +=1
        

# for j in range(1,len(variables)):
#     print(variables.iloc[j])



# # plt.plot(vib)
# from lifelines import CoxPHFitter
# from lifelines.datasets import load_rossi
# rossi_dataset = load_rossi()
# cph = CoxPHFitter()
# cph.fit(rossi_dataset, duration_col='week', event_col='arrest')
# cph.print_summary()
# cph.plot(hazard_ratios=True)