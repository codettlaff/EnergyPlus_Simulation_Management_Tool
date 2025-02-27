# =============================================================================
# Import Required Modules
# =============================================================================

# External Modules
import os
import pandas as pd
import numpy as np
import pickle
import datetime

# =============================================================================
# Read Aggregated Pickle
# =============================================================================

script_directory = os.path.dirname(__file__)
# results_folderpath = os.path.join(script_directory, 'Results', 'Processed_BuildingSim_Data')
results_folderpath = r"D:\Building_Results" # Overriding default path

def make_all_zones_aggregation_csvs():
  
    Simulation_Name_List = []
    for filepath in os.listdir(results_folderpath):
        simulation_name = os.path.basename(filepath)
        Simulation_Name_List.append(simulation_name)
    
    for Simulation_Name in Simulation_Name_List:
    
        aggregation_folderpath = os.path.join(results_folderpath, Simulation_Name, 'Sim_AggregatedData')
        aggregation_pickle_filepath = os.path.join(aggregation_folderpath, 'Aggregation_Dict_AllZones.pickle')

        aggregation_csv_folderpath = os.path.join(aggregation_folderpath, 'Aggregation_AllZones')
        os.makedirs(aggregation_csv_folderpath, exist_ok=True)
    
        with open(aggregation_pickle_filepath, 'rb') as file:
            data = pickle.load(file)
    
        for key, value in data.items():

            if isinstance(value, pd.DataFrame):
                # value.insert(0, 'Datetime', data['DateTime_List'])
                csv_filename = key + '.csv'
                csv_filepath = os.path.join(aggregation_csv_folderpath, csv_filename)
                value.to_csv(csv_filepath, index=False)


def make_one_zone_aggregation_csvs():

    Simulation_Name_List = []
    for filepath in os.listdir(results_folderpath):
        simulation_name = os.path.basename(filepath)
        Simulation_Name_List.append(simulation_name)

    for Simulation_Name in Simulation_Name_List:

        aggregation_folderpath = os.path.join(results_folderpath, Simulation_Name, 'Sim_AggregatedData')
        aggregation_pickle_filepath = os.path.join(aggregation_folderpath, 'Aggregation_Dict_OneZone.pickle')

        with open(aggregation_pickle_filepath, 'rb') as file:
            data = pickle.load(file)

        for key, value in data.items():

            if isinstance(value, pd.DataFrame):
                # value.insert(0, 'Datetime', data['DateTime_List'])
                csv_filename = key + '.csv'
                csv_filepath = os.path.join(aggregation_folderpath, csv_filename)
                value.to_csv(csv_filepath, index=False)

make_one_zone_aggregation_csvs()
make_all_zones_aggregation_csvs()