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

default_results_folderpath = os.path.join(THIS_SCRIPT_DIR, '..', 'Results')
default_simulation_settings = {
    "name": "new_simulation",
    "idf_year": 2013,
    "start_month": 1,
    "start_day": 1,
    "end_month": 12,
    "end_day": 31,
    "reporting_frequency": "timestep",
    "timestep_minutes": 5
}

# Test
TEST_IDF_FILEPATH = r"D:\Building_Modeling_Code\Data\Commercial_Prototypes\ASHRAE\90_1_2013\ASHRAE901_OfficeSmall_STD2013_Seattle.idf"
TEST_EPW_FILEPATH = r"D:\Building_Modeling_Code\Data\TMY3_WeatherFiles_Commercial\USA_WA_Seattle-Tacoma.Intl.AP.727930_TMY3.epw"

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

        output_variable_query_set['key value'] = '*'
        output_variable_query_set['reporting_frequency'] = simulation_settings["reporting_frequency"]
        output_variable_query_set['variable_name'] = variable

        current_idf.save(edited_idf_filepath)
        op.simulate(edited_idf_filepath, epw_filepath, base_dir_path=TEMPORARY_FOLDERPATH)
        os.remove(edited_idf_filepath)

        for filename in os.listdir(TEMPORARY_FOLDERPATH):

            filepath = os.path.join(TEMPORARY_FOLDERPATH, filename)

            if filepath.endswith('.csv'):
                to_csv_filepath = os.path.join(sim_results_processed_data_folderpath, os.path.basename(filepath))
                shutil.copy(filepath, to_csv_filepath)
            else:
                to_filepath = os.path.join(sim_results_output_folderpath, os.path.basename(filepath))
                shutil.copy(filepath, to_filepath)

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
    for datetime in datetime_list:

        datetime_split = datetime.split(' ')

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
            current_date = datetime(simulation_settings["idf_year"], date_split[0], date_split[1], hour=0)
            formatted_datetime = current_date + timedelta(days=1)

        else:
            formatted_datetime = datetime(simulation_settings["idf_year"], date_split[0], date_split[1], hour=int(time_split[0]), minute=int(time_split[1]))

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
