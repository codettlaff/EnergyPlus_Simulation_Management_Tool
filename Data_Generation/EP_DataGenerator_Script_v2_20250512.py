import os
from os import mkdir
import numpy as np
import pandas as pd
import scipy.io
import opyplus as op
import re
import shutil
import datetime
import pickle
from datetime import datetime, timedelta

THIS_SCRIPT_DIR = os.path.dirname(__file__)
SPECIAL_IDF_FILEPATH = os.path.join('Special.idf')
TEMPORARY_FOLDERPATH = os.path.join(THIS_SCRIPT_DIR, 'Temporary Folder')

default_data_folderpath = os.path.join(THIS_SCRIPT_DIR, '..', 'Data')
default_results_folderpath = os.path.join(THIS_SCRIPT_DIR, '..', 'Results')
default_simulation_settings = {
    "name": "new_simulation",
    "idf_year": 2013,
    "start_month": 1,
    "start_day": 1,
    "end_month": 1,
    "end_day": 3,
    "reporting_frequency": "timestep",
    "timestep_minutes": 5
}
default_simulation_variable_names = ['Schedule Value',
                                  'Facility Total HVAC Electric Demand Power',
                                  'Site Diffuse Solar Radiation Rate per Area',
                                  'Site Direct Solar Radiation Rate per Area',
                                  'Site Outdoor Air Drybulb Temperature',
                                  'Site Solar Altitude Angle',
                                  'Surface Inside Face Internal Gains Radiation Heat Gain Rate',
                                  'Surface Inside Face Lights Radiation Heat Gain Rate',
                                  'Surface Inside Face Solar Radiation Heat Gain Rate',
                                  'Surface Inside Face Temperature',
                                  'Zone Windows Total Transmitted Solar Radiation Rate',
                                  'Zone Air Temperature',
                                  'Zone People Convective Heating Rate',
                                  'Zone Lights Convective Heating Rate',
                                  'Zone Electric Equipment Convective Heating Rate',
                                  'Zone Gas Equipment Convective Heating Rate',
                                  'Zone Other Equipment Convective Heating Rate',
                                  'Zone Hot Water Equipment Convective Heating Rate',
                                  'Zone Steam Equipment Convective Heating Rate',
                                  'Zone People Radiant Heating Rate',
                                  'Zone Lights Radiant Heating Rate',
                                  'Zone Electric Equipment Radiant Heating Rate',
                                  'Zone Gas Equipment Radiant Heating Rate',
                                  'Zone Other Equipment Radiant Heating Rate',
                                  'Zone Hot Water Equipment Radiant Heating Rate',
                                  'Zone Steam Equipment Radiant Heating Rate',
                                  'Zone Lights Visible Radiation Heating Rate',
                                  'Zone Total Internal Convective Heating Rate',
                                  'Zone Total Internal Radiant Heating Rate',
                                  'Zone Total Internal Total Heating Rate',
                                  'Zone Total Internal Visible Radiation Heating Rate',
                                  'Zone Air System Sensible Cooling Rate',
                                  'Zone Air System Sensible Heating Rate',
                                  'System Node Temperature',
                                  'System Node Mass Flow Rate']

# Test
TEST_IDF_FILEPATH = r"C:\Users\codett\Downloads\ASHRAE901_OfficeLarge_STD2013_Seattle_debugging.idf"
TEST_EPW_FILEPATH = r"D:\Building_Modeling_Code\Data\TMY3_WeatherFiles_Commercial\USA_WA_Seattle-Tacoma.Intl.AP.727930_TMY3.epw"
TEST_DATA_FOLDERPATH = r"D:\Building_Modeling_Code\Data"

def generate_variables(idf_filepath, epw_filepath):

    edited_idf_filepath = os.path.join(TEMPORARY_FOLDERPATH, "edited.idf")
    initial_run_folderpath = os.path.join(TEMPORARY_FOLDERPATH, "initial_run")
    rdd_filepath = os.path.join(initial_run_folderpath, "eplusout.rdd")

    if not os.path.exists(TEMPORARY_FOLDERPATH): mkdir(TEMPORARY_FOLDERPATH)
    if not os.path.exists(initial_run_folderpath): mkdir(initial_run_folderpath)

    shutil.copy(idf_filepath, edited_idf_filepath)

    # Appending Output Variable Dictionary - This tells EP to generate rdd file.
    with open(edited_idf_filepath, "a") as idf_to:
        idf_to.write('\nOutput:VariableDictionary,IDF;')

    op.simulate(edited_idf_filepath, epw_filepath, base_dir_path=initial_run_folderpath)

    variable_names = []
    with open(rdd_filepath, "r") as rdd_file:

        lines = rdd_file.readlines()
        for line in lines:
            if not line.startswith('!'):
                variable_name = line.split(',')[2]
                variable_names.append(variable_name)

    shutil.rmtree(TEMPORARY_FOLDERPATH)

    return variable_names

def simulate_variables(idf_filepath, epw_filepath, variable_names, simulation_settings=default_simulation_settings, results_folderpath=default_results_folderpath):

    edited_idf_filepath = os.path.join(TEMPORARY_FOLDERPATH, "edited.idf")
    sim_results_folderpath = os.path.join(results_folderpath, simulation_settings["name"])
    sim_results_output_folderpath = os.path.join(sim_results_folderpath, "Sim_OutputFiles")
    sim_results_processed_data_folderpath = os.path.join(sim_results_folderpath, "Sim_ProcessedData")

    processed_data_pickle_filepath = os.path.join(sim_results_processed_data_folderpath, "Output_Variables.pickle")
    eio_filepath = os.path.join(sim_results_output_folderpath, "eplusout.eio")
    eio_pickle_filepath = os.path.join(sim_results_processed_data_folderpath, "eio.pickle")

    if not os.path.exists(TEMPORARY_FOLDERPATH): mkdir(TEMPORARY_FOLDERPATH)
    if not os.path.exists(results_folderpath): mkdir(results_folderpath)
    if not os.path.exists(sim_results_folderpath): mkdir(sim_results_folderpath)
    if not os.path.exists(sim_results_output_folderpath): mkdir(sim_results_output_folderpath)
    if not os.path.exists(sim_results_processed_data_folderpath): mkdir(sim_results_processed_data_folderpath)

    shutil.copy(idf_filepath, edited_idf_filepath)

    with open(SPECIAL_IDF_FILEPATH, "r") as special_idf_file:
        special_idf_data = special_idf_file.read()

    with open(edited_idf_filepath, "a") as edited_idf_file:
        edited_idf_file.write("\n")
        edited_idf_file.write(special_idf_data)

    current_idf = op.Epm.load(edited_idf_filepath)

    # Editing Run Period
    current_idf_run_period = current_idf.RunPeriod.one()
    current_idf_run_period['begin_day_of_month'] = simulation_settings["start_day"]
    current_idf_run_period['begin_month'] = simulation_settings["start_month"]
    current_idf_run_period['end_day_of_month'] = simulation_settings["end_day"]
    current_idf_run_period['end_month'] = simulation_settings["end_month"]

    # Editing Time Step
    current_idf_timestep = current_idf.Timestep.one()
    current_idf_timestep['number_of_timesteps_per_hour'] = int(60/simulation_settings["timestep_minutes"])

    current_idf_schedules = current_idf.Schedule_Compact

    # Generate and Organize Time Series Data
    output_variable_query_set = current_idf.Output_Variable.one()
    for variable in variable_names:

        data_csv_filename = variable.replace(' ', '_') + '.csv'

        output_variable_query_set['key_value'] = '*'
        output_variable_query_set['reporting_frequency'] = simulation_settings["reporting_frequency"]
        output_variable_query_set['variable_name'] = variable

        current_idf.save(edited_idf_filepath)
        op.simulate(edited_idf_filepath, epw_filepath, base_dir_path=TEMPORARY_FOLDERPATH)
        os.remove(edited_idf_filepath)

        from_csv_filepath = os.path.join(TEMPORARY_FOLDERPATH, 'eplusout.csv')
        to_csv_filepath = os.path.join(sim_results_processed_data_folderpath, data_csv_filename)
        if os.path.exists(from_csv_filepath):
            shutil.copy(from_csv_filepath, to_csv_filepath)
            os.remove(from_csv_filepath)
        else: print(f"No Results for {variable}\n")

        for filename in os.listdir(TEMPORARY_FOLDERPATH):

            filepath = os.path.join(TEMPORARY_FOLDERPATH, filename)
            to_filepath = os.path.join(sim_results_output_folderpath, os.path.basename(filepath))
            shutil.copy(filepath, to_filepath)
            os.remove(filepath)

    # Process Time Series Data
    output_variable_data_dict = {}
    i = 0

    for csv_filename in os.listdir(sim_results_processed_data_folderpath):

        csv_filepath = os.path.join(sim_results_processed_data_folderpath, csv_filename)
        current_df = pd.read_csv(csv_filepath)

        # Get Datetime List from first variable
        if i == 0:
            datetime_list = current_df['Date/Time'].tolist()
            i += 1

        current_df = current_df.drop(columns=['Date/Time'], axis=1)

        variable_name = csv_filename.replace('_', ' ').replace('.csv', '')
        output_variable_data_dict[variable_name] = current_df

        os.remove(csv_filepath)

    # Format Datetimes
    formatted_datetime_list = []
    for date_time in datetime_list:

        datetime_split = date_time.split(' ')

        if (len(datetime_split) == 4):
            date_split = datetime_split[1].split('/')
            time_split = datetime_split[3].split(':')

        elif (len(datetime_split) == 3):
            date_split = datetime_split[0].split('/')
            time_split = datetime_split[2].split(':')

        elif (len(datetime_split) == 2):

            date_split = datetime_split[0].split('/')
            time_split = datetime_split[1].split(':')

        if int(time_split[0]) == 24: # Handle conversion from 24th hour to 0th hour of next day.
            current_date = datetime(simulation_settings["idf_year"], int(date_split[0]), int(date_split[1]), hour=0)
            formatted_datetime = current_date + timedelta(days=1)

        else:
            formatted_datetime = datetime(simulation_settings["idf_year"], int(date_split[0]), int(date_split[1]), hour=int(time_split[0]), minute=int(time_split[1]))

        formatted_datetime_list.append(formatted_datetime)

    output_variable_data_dict['DateTime_List'] = formatted_datetime_list
    pickle.dump(output_variable_data_dict, open(processed_data_pickle_filepath, 'wb'))

    # Process EIO Output File
    eio_dict = {}

    with open(eio_filepath, 'r') as eio_file:
        lines = eio_file.readlines()

    lines = lines[1:] # removing into line
    category_key_list = [
        "Zone Information", "Zone Internal Gains Nominal", "People Internal Gains Nominal",
        "Lights Internal Gains Nominal", "ElectricEquipment Internal Gains Nominal",
        "GasEquipment Internal Gains Nominal", "HotWaterEquipment Internal Gains Nominal",
        "SteamEquipment Internal Gains Nominal", "OtherEquipment Internal Gains Nominal"
    ]

    def is_table_header(line, key):
        if ((line.find(key) >= 0) and (line.find('!') >= 0)):
            Is_Table_Header = True
        else:
            Is_Table_Header = False

    for line1 in lines:

        for key in category_key_list:

            if is_table_header(line1, key):

                column_name_list = line1.split(',')[1:]
                column_name_list[-1] = column_name_list[-1].replace('\n', '')
                if column_name_list[-1] == '': column_name_list = column_name_list[:-1]

                index_list = []
                data_list = []

                for line2 in lines:

                    if ((line2.find('!') == -1) and (line2.find(key) > 0)):

                        line2_split = line2.split(',')
                        line2_split[-1] = line2_split[-1].replace('\n', '')
                        if line2_split[-1] == '': line2_split = line2_split[:-1]

                        index_list.append(line2_split[0])

                        line2_split = line2_split[1:]
                        line2_len = len(line2_split)

                        # Filling empty column
                        if line2_len < len(column_name_list):

                            diff = len(column_name_list) - line2_len

                            for i in range(diff):
                                line2_split.append('')

                        data_list.append(line2_split)

                df_table = pd.DataFrame(data_list, index=index_list, columns=column_name_list)

                eio_dict[key] = df_table

        pickle.dump(eio_dict, open(eio_pickle_filepath, 'wb'))

# simulate_variables(TEST_IDF_FILEPATH, TEST_EPW_FILEPATH, default_simulation_variable_names)

def get_location_climate_zone(location=None, climate_zone=None):

    climate_zones = {
        "Miami": "1A",
        "Tampa": "2A",
        "Tucson": "2B",
        "Atlanta": "3A",
        "ElPaso": "3B",
        "SanDiego": "3C",
        "NewYork": "4A",
        "Albuquerque": "4B",
        "Seattle": "4C",
        "Buffalo": "5A",
        "Denver": "5B",
        "PortAngeles": "5C",
        "Rochester": "6A",
        "GreatFalls": "6B",
        "InternationalFalls": "7",
        "Fairbanks": "8"
    }

    if location: return climate_zones.get(location, "Climate Zone not found.")
    if climate_zone:
        reversed_climate_zones = {v: k for k, v in climate_zones.items()}
        return reversed_climate_zones.get(climate_zone, "Location not found.")

def get_idf_weather_filepaths(building_type, idf_filter_list, idf_weather_df=None, data_folderpath=default_data_folderpath):

    # Initialize file lists
    all_idf_filepath_list = []
    all_epw_filepath_list = []

    # If no `idf_weather_df` is provided, collect all .idf and .epw files from the data folder
    if idf_weather_df is None:
        for root, _, files in os.walk(data_folderpath):
            for file in files:
                if file.endswith(".idf") and building_type in root:
                    all_idf_filepath_list.append(os.path.join(root, file))
                elif file.endswith(".epw"):
                    all_epw_filepath_list.append(os.path.join(root, file))
        idf_files = all_idf_filepath_list
        epw_files = all_epw_filepath_list
    else:
        # Get idf and epw file lists from `idf_weather_df`
        idf_files = idf_weather_df['filtered_idf_filepath'].tolist()
        epw_files = idf_weather_df['filtered_epw_filepath'].dropna().tolist()

    # Filter IDF files based on `idf_filter_list` (2D list)
    filtered_idf_files = []
    for filters in idf_filter_list:  # Each inner list represents a set of filters
        for idf in idf_files:
            if all(f in os.path.basename(idf) for f in filters):  # All filters must match
                filtered_idf_files.append(idf)

    # Create a dataframe to store mapping of filtered IDF and EPW filepaths
    data = []
    for idf in filtered_idf_files:
        idf_filename = os.path.basename(idf)
        if building_type == 'Commercial':
            location = idf_filename.split('_')[3].replace('.idf', '')
        elif building_type == 'Residential':
            climate_zone = idf_filename.split('+')[2]
            location = get_location_climate_zone(climate_zone=climate_zone)
        elif building_type == 'Manufactured':
            location = idf_filename.split('_')[1]
        else:
            location = None

        # Find the corresponding EPW file for the location
        corresponding_epw = None
        for epw in epw_files:
            epw_filename = os.path.basename(epw).replace('.', '')
            if building_type in epw and location in epw_filename:
                corresponding_epw = epw
                break

        data.append({'filtered_idf_filepath': idf, 'filtered_epw_filepath': corresponding_epw})

    # Return as a dataframe
    return pd.DataFrame(data)

idf_filter_list = [['Seattle']]
df = get_idf_weather_filepaths('Commercial', idf_filter_list, data_folderpath=TEST_DATA_FOLDERPATH)
idf_filter_list = [['Hospital'], ['ApartmentHighRise'], ['ApartmentMidRise']]
df = get_idf_weather_filepaths('Commercial', idf_filter_list, idf_weather_df=df)
print(df)