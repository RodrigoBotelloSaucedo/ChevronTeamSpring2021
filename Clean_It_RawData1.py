import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time


# Import the data from ExcelFile
raw_data_1 = pd.ExcelFile('ChevronDataFiles/P-16051 Raw Data1.xlsx')

# Import All the sheets. However, we will only be using Pump Data for now
vibration = pd.read_excel(raw_data_1,'Vibration')
vibration_filtered = pd.read_excel(raw_data_1,'Vib Filtered')
pump_data = pd.read_excel(raw_data_1,'Pump data')
dataset = pd.read_excel(raw_data_1,'dataset')

# Get the column names
column_names = pump_data.columns.values

# Function to Convert all to epoch time, returns an array of epoch values corresponding to the date.
# It can handle strings, datetime, and index errors. 
def epoch_time(series): 
    epoch_values = []
    pump_data_dropped = series.dropna().reset_index().drop(columns = 'index').to_numpy()

    for i in range(len(pump_data_dropped)):
        try: 
            epoch_values.append(float(pump_data_dropped[i][0].timestamp()))
        
        except AttributeError as string_error:
            epoch_values.append(time.mktime(time.strptime(pump_data_dropped[i][0], "%m/%d/%y %H:%M:%S %p")))
            
        except IndexError as index_error: 
            
            break
            
    return epoch_values
    
   
# Clean all the dataframes delete NaN values. Store data frame in array    
clean_frames = []
counter = 0
for i in range(0, len(column_names) - 2, 2): 
    clean_frames.append(pump_data[[column_names[i], column_names[i + 1]]].dropna().reset_index().drop(columns = 'index'))
    clean_frames[counter][column_names[i + 1]] = epoch_time(clean_frames[counter][column_names[i + 1]])
    counter += 1
    
# Concatonate frames  
clean_frame = pd.concat(clean_frames, axis = 1)


# Create bins
array_times = []
for epoch in range(1333281600, 1614870337,2628000):
    array_times.append(epoch)
epoch_df = pd.DataFrame(array_times, columns = ['Epoch'])


# Add bins to frame
clean_frame = pd.concat([epoch_df , clean_frame], axis = 1)


# Bin all the dates and average them. Time complexity kinda trash though
for i in range(len(clean_frame['Epoch']) - 1):
    # Iterate over columns
    for j in range(0, len(column_names) - 2, 2): 
        clean_frame[column_names[j]][i] = clean_frame.loc[((clean_frame[column_names[j + 1]] > clean_frame['Epoch'][i]) & (clean_frame[column_names[j +1]] < clean_frame['Epoch'][i + 1])), column_names[j]].mean()

# Convert from Epoch to Date 
clean_frame['Epoch'] = pd.to_datetime(clean_frame['Epoch'],unit='s')
clean_frame = clean_frame.loc[:, ~clean_frame.columns.str.startswith('Date')]

# Save into Excel 
clean_frame.to_excel("ChevronDataFiles/P-16051_Raw_Data1_Cleaned.xlsx", sheet_name = 'PumpData')