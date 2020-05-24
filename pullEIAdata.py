import requests as r
import multiprocessing
import json
import pandas as pd
import re
import os

with open('API-key.txt', 'r') as api_key:
    API_KEY = api_key.read()

def get_data(url, key = API_KEY):
    #print(url.replace('YOUR_API_KEY_HERE',API_KEY))
    data = r.get(url.replace('YOUR_API_KEY_HERE',API_KEY))
    return data.json()

def save_json(json_dump, filename): #pass in filename string
    #if filename:
    # Writing JSON data
    with open(filename, 'w') as f:
        #print(json.dumps(json_dump))
        json.dump(json_dump, f)
    #else:

if __name__ == "__main__":
    #get plant data - DONE
    #extract all plants - DONE
    #get category id for all plants - DONE
    #pull all plants by state - DONE
    #pull category id for all plants, all states - TABLE 1 - DONE
    #pull all metric category types - TABLE 2 - DONE
    #pull data for all types, all plants, all states - TABLE 3

    #pull all state IDs into one lookup
    from datetime import datetime
    startTime = datetime.now()

    #Python 3: 
    print(datetime.now() - startTime)


    states_call =  'http://api.eia.gov/category/?api_key=YOUR_API_KEY_HERE&category_id=1017'
    state_categories = get_data(states_call)
    state_categories = state_categories['category']['childcategories']
    stateIDs = {}
    for state in state_categories:
        stateIDs[state['category_id']] = state['name']      
    save_json(state_categories, 'states.json') #we'll save the full json dump for later
    
    #loop through each state and pull all plants
    plants_by_state = {}
    #{State:{ stateID: ID#, plants:{PlantID1: Plant1, PlantID2: Plant2...}}
    temp_call = 'http://api.eia.gov/category/?api_key=YOUR_API_KEY_HERE&category_id=####'
    for id in stateIDs:
         temp_data = get_data(temp_call.replace('####',str(id)))
         plant_temp = temp_data['category']['childcategories']
         plants_by_state[stateIDs[id]] = temp_data['category']['childcategories']

    # put all plants in a table with category ID and state
    plant_df = pd.DataFrame(columns=['State', 'category_id','Plant Name'])
    id_temp = []
    plant_temp = []
    state_temp = []
    for state in stateIDs.values(): 
        for i, plant in enumerate(plants_by_state[state]):    
            id_temp.append(plants_by_state[state][i]['category_id'])
            plant_temp.append(plants_by_state[state][i]['name'])
            state_temp.append(state)
    plant_df['State'] = state_temp
    plant_df['category_id'] = id_temp
    plant_df['Plant Name'] = plant_temp

    plant_df['Plant ID'] = [plant.split(' ')[0].strip('()') for plant in plant_df['Plant Name']]
    plant_df['Plant Name'] = [plant.split('(')[1].strip('()') for plant in plant_df['Plant Name']]

    plant_data = {}
    plant_temp_call = 'http://api.eia.gov/category/?api_key=YOUR_API_KEY_HERE&category_id=####'

    us_plants_file = 'plant-data.txt'
    if os.path.exists(us_plants_file):
        with open(us_plants_file, 'r') as jfile:
            plant_data = json.load(jfile)
    else: 
        for cat in plant_df['category_id']:
            plant_data[cat] = get_data(temp_call.replace('####',str(cat)))
        #print(plant_data)
        save_json(plant_data, us_plants_file)

    #for key in plant_data:
    #   print(plant)
    plant_data_calls = []
   
    for cat_id in list(plant_data):
        print(plant_data[cat_id],'\n')
        temp = plant_data[cat_id]['category']['childseries']
        print("temp",len(temp))
        for i, tmp in enumerate(temp):
            #print(temp[i]['series_id'])
            plant_data_calls.append(temp[i]['series_id'])
    print("length of plant data; ", len(list(plant_data)))
    print("length of plant data calls", len(plant_data_calls))
    #plant_data_calls = [plant_data[cat_id]['category']['childseries'][0]['series_id'] for cat_id in list(set(plant_data))]
    #[print(call) for call in plant_data_calls]
    #[print(cat_id) for cat_id in plant_data]
    save_json(plants_by_state, 'usplants.json') #save json data for later
    states_df = pd.read_json('states.json')
    states_df.to_csv('states.csv')
    plant_df.to_csv('us-plants.csv')

    series_temp_call = 'http://api.eia.gov/series/?api_key=YOUR_API_KEY_HERE&series_id=####'

    series_data_file = 'series-data.txt'
    series_data = {}
    pool_outputs = {}
    
    def get_series_data(call):
        #i=1
        #for call in calls:
        print('API CALL {0}'.format(call))
        try:
            series_data[call] = get_data(series_temp_call.replace('####', call))
        except:
            series_data[call] = 'REST CALL FAILED'
        #i=i+1
        #print(series_data)
        return series_data
    #print(plant_data_calls)
    if os.path.exists(series_data_file):
            with open(series_data_file, 'r') as sfile:
                pool_outputs = json.load(sfile)
    else:
        #multiprocessing.set_start_method('spawn')
        pool = multiprocessing.Pool(processes=6)
        #pool_outputs = pool.map_async(get_series_data, plant_data_calls)
        pool_outputs = pool.map_async(get_series_data, plant_data_calls).get()

        pool.close()
        pool.join()
        save_json(pool_outputs, series_data_file)
        # i=1
        # for call in plant_data_calls:
        #     print('API CALL {0}, {1} of {2}'.format(call,i,len(plant_data_calls)))
        #     series_data[call] = get_data(series_temp_call.replace('####', call))
        #     i=i+1
        # #print(series_data)
        # save_json(series_data, series_data_file)
    
    #print(series_data["ELEC.PLANT.CONS_EG_BTU.10173-ALL-ALL.A"])

    #print(row,': ', series_data[row]['series'][0]['name'],': ', series_data[row]['series'][0]['data']) for row in series_data]
                
    series_temp = []
    name_temp = []
    data_temp = []
    series_df = pd.DataFrame()
    print("length of series data; ", len(pool_outputs))
    for row in series_data:
        #print(series_data[row])
        series_temp.append(row)
        name_temp.append(series_data[row]['series'][0]['name'])
        data_temp.append(series_data[row]['series'][0]['data'])
    series_df['series_id'] = series_temp
    series_df['name'] = name_temp
    series_df['data'] = data_temp

    series_df.to_csv('series_data.csv',index=False)
    
    #Python 3: 
    print(datetime.now() - startTime)
    
