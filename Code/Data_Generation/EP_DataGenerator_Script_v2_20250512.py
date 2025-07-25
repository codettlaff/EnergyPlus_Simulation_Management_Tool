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
import requests

DATA_FOLDERPATH = os.path.join(os.path.dirname(__file__), '..', '..','..', 'Data')
RESULTS_FOLDERPATH = os.path.join(os.path.dirname(__file__), '..', '..', 'Results')
SPECIAL_IDF_FILEPATH = os.path.join(DATA_FOLDERPATH, 'Special.idf')
TEMPORARY_FOLDERPATH = os.path.join(os.path.dirname(__file__), 'temporary_folder')

PRESELECTED_VARIABLES =  ['Schedule Value',
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

def preselected_variables(): return PRESELECTED_VARIABLES

# Test
TEST_IDF_FILEPATH = r"C:\Users\codett\Downloads\ASHRAE901_OfficeLarge_STD2013_Seattle_debugging.idf"
TEST_EPW_FILEPATH = r"D:\Building_Modeling_Code\Data\TMY3_WeatherFiles_Commercial\USA_WA_Seattle-Tacoma.Intl.AP.727930_TMY3.epw"
TEST_DATA_FOLDERPATH = r"D:\Building_Modeling_Code\Data"

example_simulation_settings = {
    "name": "new_simulation",
    "idf_year": 2013,
    "start_datetime": datetime(2013, 1, 1),
    "end_datetime": datetime(2014, 1, 1),
    "reporting_frequency": "timestep",
    "timestep_minutes": 5,
    "variables": PRESELECTED_VARIABLES
}

example_building_information = {
    "building_type": "Commercial",
    "prototype": "OfficeSmall",
    "energy_code": "ASHRAE2013",
    "idf_climate_zone": "2A",
    "idf_location": "Seattle",
    "heating_type": "NA",
    "foundation_type": "NA",
    "building_id": 1
}

def initial_run(idf_filepath, epw_filepath):

    edited_idf_filepath = os.path.abspath(os.path.join(TEMPORARY_FOLDERPATH, "edited.idf"))
    initial_run_folderpath = os.path.abspath(os.path.join(TEMPORARY_FOLDERPATH, "initial_run"))
    initial_run_results_folderpath = os.path.join(TEMPORARY_FOLDERPATH, "initial_run_results")
    rdd_filepath = os.path.join(initial_run_folderpath, "eplusout.rdd")
    eio_filepath = os.path.join(initial_run_folderpath, "eplusout.eio")

    if not os.path.exists(TEMPORARY_FOLDERPATH): mkdir(TEMPORARY_FOLDERPATH)
    if not os.path.exists(initial_run_folderpath): mkdir(initial_run_folderpath)
    if not os.path.exists(initial_run_results_folderpath): mkdir(initial_run_results_folderpath)

    shutil.copy(idf_filepath, edited_idf_filepath)

    # Appending Output Variable Dictionary - This tells EP to generate rdd file.
    with open(edited_idf_filepath, "a") as idf_to:
        idf_to.write('\nOutput:VariableDictionary,IDF;')

    op.simulate(edited_idf_filepath, epw_filepath, base_dir_path=initial_run_folderpath)

    move_to_rdd_filepath = os.path.join(initial_run_results_folderpath, "eplusout.rdd")
    move_to_eio_filepath = os.path.join(initial_run_results_folderpath, "eplusout.eio")
    shutil.copy(rdd_filepath, move_to_rdd_filepath)
    shutil.copy(eio_filepath, move_to_eio_filepath)

    shutil.rmtree(initial_run_folderpath)

    return move_to_rdd_filepath, move_to_eio_filepath

def get_variable_list(rdd_filepath):

    variable_names = []
    with open(rdd_filepath, "r") as rdd_file:

        lines = rdd_file.readlines()
        for line in lines:
            if not line.startswith('!'):
                variable_name = line.split(',')[2]
                variable_names.append(variable_name)

    variable_names.sort()

    return variable_names

def parse_eio_file(filepath, category_key_list=None):

    tables = {}  # Store parsed tables here

    with open(filepath, "r") as file:

        current_table_name = None
        current_columns = None
        rows = []

        first_line = True
        mismatch = False

        for line in file:

            line = line.strip()  # Remove leading/trailing whitespace

            if first_line:
                first_line = False
                continue

            if line.startswith("!"):  # Header line detected

                # Printing results of previous table.
                if mismatch:
                    print(f"Mismatch in table '{current_table_name}' {len(current_columns)} columns are defined, but {len(row_values)} values were provided.")

                # If there's an existing table's data, add it to `tables`
                if current_table_name and current_columns and rows:
                    table_name = current_table_name.replace('<', '').replace('>', '')
                    tables[table_name] = pd.DataFrame(rows, columns=current_columns)

                # Parse the table header
                parts = line[1:].split(",")  # Ignore "!" and split by commas
                current_table_name = parts[0].strip()  # Table name
                current_columns = [col.strip() for col in parts[1:]]  # Column names
                rows = []  # Reset rows for the new table

                mismatch = False

            elif line:  # Data lines
                # Parse the data row and split by commas
                line = line.rstrip(",") # Get rid of trailing comma, if it exists
                row_values = [value.strip() for value in line.split(",")][1:]

                # Ensure row length matches the number of columns
                if len(row_values) == len(current_columns):
                    rows.append(row_values)
                else:
                    mismatch = True


        # Add the last table after EOF
        if current_table_name and current_columns and rows:
            table_name = current_table_name.replace('<','').replace('>','')
            tables[table_name] = pd.DataFrame(rows, columns=current_columns)

    if category_key_list:
        filtered_table_dict = {key: value for key, value in tables.items() if key in category_key_list}

    return tables

def simulate_variables(idf_filepath, epw_filepath, simulation_settings, variable_names, results_folderpath=RESULTS_FOLDERPATH):

    edited_idf_filepath = os.path.join(TEMPORARY_FOLDERPATH, "edited.idf")
    sim_results_folderpath = os.path.join(results_folderpath, simulation_settings["name"])
    sim_results_output_folderpath = os.path.join(sim_results_folderpath, "Sim_OutputFiles")
    sim_results_processed_data_folderpath = os.path.join(sim_results_folderpath, "Sim_ProcessedData")

    processed_data_pickle_filepath = os.path.join(sim_results_processed_data_folderpath, "Output_Variables.pickle")
    eio_filepath = os.path.join(sim_results_output_folderpath, "eplusout.eio")
    eio_pickle_filepath = os.path.join(sim_results_processed_data_folderpath, "eio.pickle")

    temporary_folderpath = os.path.join(TEMPORARY_FOLDERPATH, "temp")
    if not os.path.exists(TEMPORARY_FOLDERPATH): mkdir(TEMPORARY_FOLDERPATH)
    if not os.path.exists(temporary_folderpath): mkdir(temporary_folderpath)
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
    current_idf_run_period['begin_day_of_month'] = simulation_settings["start_datetime"].day
    current_idf_run_period['begin_month'] = simulation_settings["start_datetime"].month
    current_idf_run_period['end_day_of_month'] = simulation_settings["end_datetime"].day
    current_idf_run_period['end_month'] = simulation_settings["end_datetime"].month

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
        op.simulate(edited_idf_filepath, epw_filepath, base_dir_path=temporary_folderpath)
        os.remove(edited_idf_filepath)

        from_csv_filepath = os.path.join(temporary_folderpath, 'eplusout.csv')
        to_csv_filepath = os.path.join(sim_results_processed_data_folderpath, data_csv_filename)
        if os.path.exists(from_csv_filepath):
            shutil.copy(from_csv_filepath, to_csv_filepath)
            os.remove(from_csv_filepath)
        else: print(f"No Results for {variable}\n")

        for filename in os.listdir(temporary_folderpath):

            filepath = os.path.join(temporary_folderpath, filename)
            to_filepath = os.path.join(sim_results_output_folderpath, os.path.basename(filepath))
            shutil.copy(filepath, to_filepath)
            os.remove(filepath)

        shutil.rmtree(temporary_folderpath)

    # Process Time Series Data
    output_variable_data_dict = {}
    i = 0

    for csv_filename in os.listdir(sim_results_processed_data_folderpath):

        if csv_filename.endswith(".csv"):
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
            current_date = datetime(simulation_settings["start_datetime"].year, int(date_split[0]), int(date_split[1]), hour=0)
            formatted_datetime = current_date + timedelta(days=1)

        else:
            formatted_datetime = datetime(simulation_settings["start_datetime"].year, int(date_split[0]), int(date_split[1]), hour=int(time_split[0]), minute=int(time_split[1]))

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
        return (key in line) and ('!' in line)

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

    return os.path.join(results_folderpath, simulation_settings["name"])
