def epoch_time(series): 
    epoch_values = []
    pump_data_dropped = series.dropna().reset_index().drop(columns = 'index').to_numpy()

    for i in range(len(pump_data_dropped)):
        try: 
            epoch_values.append(pump_data_dropped[i][0].timestamp())
        
        except AttributeError as error:
            try: 
                epoch_values.append(time.mktime(time.strptime(pump_data_dropped[i][0], "%m/%d/%y %H:%M:%S %p")))
            except TypeError as error_numpy: 
                #print(pump_data_dropped[i][0], type(pump_data_dropped[i][0]))
                epoch_values.append(np.datetime64(pump_data_dropped[i][0], 's').astype(int))

        except IndexError as index_error: 
            break
    return epoch_values
	
def standard_date_types(series): 
    standard_times = []
    pump_data_dropped = series.dropna().reset_index().drop(columns = 'index').to_numpy()
    for i in range(len(pump_data_dropped)):
        try: 
            standard_times.append(np.datetime64(pump_data_dropped[i][0]))
            
        except ValueError as error:
            try: 
                standard_times.append(np.datetime64(datetime.fromtimestamp(mktime(time.strptime(pump_data_dropped[i][0], "%m/%d/%y %H:%M:%S %p")))))
            except TypeError as error_numpy: 
                standard_times.append((pump_data_dropped[i][0]))
        except IndexError as index_error: 
            break
    return standard_times