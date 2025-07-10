"""
Created on Tue Jan 30 15:32:25 2024

@author: Athul Jose P

main function of web app
"""

# Importing Required Modules
import os
import sys
import re
import shutil
import pickle
import copy
import datetime
from datetime import date
from datetime import datetime
from os import mkdir
import base64

import numpy as np
import pandas as pd
from dash import Dash, dcc, html, Input, Output, State, dash_table, callback_context, no_update
import dash_daq as daq
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import opyplus as op

# Importing User-Defined Modules
import EPGenApp_Module as EPGen
import EPAggApp_Module as EPAgg
import EPVisApp_Module as EPVis
import PSQLApp_Module as PSQL
from Archive.Data_Generation.EP_DataGenerator_Script_v2_20250512 import TEMPORARY_FOLDERPATH

# Directory Paths
UPLOAD_DIRECTORY = os.path.join(os.path.dirname(__file__), "Uploads")
DATA_FOLDERPATH = os.path.join(os.path.dirname(__file__), '..', '..', 'Data')
RESULTS_FOLDERPATH = os.path.join(os.path.dirname(__file__), '..', '..', 'Results')
SPECIAL_IDF_FILEPATH = os.path.join(DATA_FOLDERPATH, 'Special.idf')

if os.path.exists(UPLOAD_DIRECTORY): shutil.rmtree(UPLOAD_DIRECTORY)
os.mkdir(UPLOAD_DIRECTORY)

TEMPORARY_FOLDERPATH = os.path.join(os.path.dirname(__file__), '..', 'Data_Generation', 'TEMPORARY_FOLDERPATH')
if os.path.exists(TEMPORARY_FOLDERPATH): shutil.rmtree(TEMPORARY_FOLDERPATH)

########## System Variables ##########

DATA_IDF_FILEPATH = None
DATA_EPW_FILEPATH = None
PRESELECTED_VARIABLES = EPGen.preselected_variables()
INITIAL_RUN_EIO_FILEPATH = None
INITIAL_RUN_RDD_FILEPATH = None

DEFAULT_IDF_FILEPATH = os.path.join(DATA_FOLDERPATH, 'Commercial_Prototypes', 'ASHRAE', '90_1_2013', 'ASHRAE901_OfficeSmall_STD2013_Seattle.idf')
DEFAULT_EPW_FILEPATH = os.path.join(DATA_FOLDERPATH, 'TMY3_WeatherFiles_Commercial', 'USA_WA_Seattle-Tacoma.Intl.AP.727930_TMY3.epw')

SIMULATION_SETTINGS = {
    "name": None,
    "start_datetime": date(2020, 1, 1),
    "end_datetime": date(2020, 1, 2),
    "reporting_frequency": 'timestep',
    "timestep_minutes": 5,
    "variables": PRESELECTED_VARIABLES,
    "ep_version": None
}

BUILDING_INFORMATION = {
    "building_type": None,
    "prototype": None,
    "energy_code": None,
    "idf_climate_zone": None,
    "idf_location": None,
    "heating_type": None,
    "foundation_type": None,
}
default_building_information = {
    "building_type": "Commercial",
    "prototype": "OfficeSmall",
    "energy_code": "ASHRAE2013",
    "idf_climate_zone": "4C",
    "idf_location": "Seattle",
    "heating_type": None,
    "foundation_type": None,
}

RESULTS_FILEPATHS = {
    'variables_pickle_filepath': None,
    'eio_pickle_filepath': None,
    'aggregated_pickle_filepath': None
}

########## Data Aggregation ##########

RESULTS_AGGREGATED_PICKLE_FILEPATH = None

AGGREGATION_SETTINGS = {}
example_aggregation_settings = {
    "aggregation_type": "average",
    "zone_list": [],
    "variable_list": None
}

########## Database ##########

USING_DATABASE = False
DB_SETTINGS = None
example_db_settings = {
    "dbanme": "New Database",
    "user": "Casey",
    "password": "OfficeLarge",
    "host": "localhost",
    "port": 5432
}

ZONES_DF = None # Contains zone_name, zone_id


# Instantiate our App and incorporate BOOTSTRAP theme Stylesheet
# Themes - https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/#available-themes
# Themes - https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/explorer/
# hackerthemes.com/bootstrap-cheatsheet/
app = Dash(__name__, external_stylesheets=[dbc.themes.LITERA], suppress_callback_exceptions=True)

# App Layout using Dash Bootstrap
app.layout = dbc.Container([

    dcc.Store(id='generation_default_idf_filepath', data=None),
    dcc.Store(id='generation_default_epw_filepath', data=None),
    dcc.Store(id='generation_idf_filepath', data=None),
    dcc.Store(id='generation_epw_filepath', data=None),
    dcc.Store(id='building_information', data=None),

    dbc.Row([
        html.H1(
            "EnergyPlus Simulation Management Tool",
            className = 'text-center text-primary mb-4'
        )
    ]),

    dcc.Tabs([
        # postgreSQL Tab
        dcc.Tab(
            label='PostgreSQL',
            className='text-center text-primary mb-4',
            children=PSQL.tab_layout
        ),

        # EP Generation Tab
        dcc.Tab(
            label='EP Generation',
            className = 'text-center text-primary mb-4',
            children=EPGen.tab_layout
        ),

        # EP Aggregation Tab
        dcc.Tab(
            label = 'Aggregation',
            className = 'text-center text-primary mb-4',
            children = EPAgg.tab_layout
        ),

        # EP Visualization Tab
        dcc.Tab(
            label = 'Visualization & Analysis',
            className = 'text-center text-primary mb-4',
            children = EPVis.tab_layout
        )
    ])
], fluid = False)

########## Callbacks ##########

def format_datetime(date_string):
    year, month, day = date_string.split('-')
    formatted_datetime = datetime(int(year), int(month), int(day))
    return formatted_datetime

def valid_filepath(filepath):
    if filepath is not None:
        if os.path.isfile(filepath):
            return True
    return False

########## PostgreSQL ##########

def get_callback_id():
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    return triggered_id

# Database Selection
@app.callback(
    Output('PSQL_Div_CreateSelectDatabase', 'hidden'),
    Input('PSQL_RadioButton_UsingDatabase', 'value'),
    prevent_initial_call=True
)
def database_selection(selection):
    global USING_DATABASE
    USING_DATABASE = selection
    return not selection

# Create/Select Database
@app.callback(
    Output('PSQL_Div_EnterInfo', 'hidden'),
    Output('PSQL_Div_SelectDbfromExist', 'hidden'),
    Input('PSQL_RadioButton_CreateSelectDatabase', 'value'),
    Input('PSQL_RadioButton_UsingDatabase', 'value'),
    prevent_initial_call=True
)
def create_select_database(selection, using_db):
    if (selection == 1) and using_db: return False, True
    elif (selection == 2) and using_db: return True, False
    else: return True, True

# Create Database Enter Information
@app.callback(
    Input('PSQL_Textarea_Username', 'value'),
    Input('PSQL_Textarea_Password', 'value'),
    Input('PSQL_Textarea_PortNumber', 'value'),
    Input('PSQL_Textarea_HostName', 'value'),
    Input('PSQL_Textarea_DbName', 'value'),
    prevent_initial_call=True
)
def enter_database_information(username, password, port, host, dbname):
    global DB_SETTINGS
    db_settings = {
        "dbname": dbname,
        "user": username,
        "password": password,
        "host": host,
        "port": port
    }
    DB_SETTINGS = db_settings

# Create Database Button
@app.callback(
    Output('PSQL_Button_CreateDatabase', 'children'),
    Input('PSQL_Button_CreateDatabase', 'n_clicks'),
    Input('PSQL_Textarea_Username', 'value'),
    Input('PSQL_Textarea_Password', 'value'),
    Input('PSQL_Textarea_PortNumber', 'value'),
    Input('PSQL_Textarea_HostName', 'value'),
    Input('PSQL_Textarea_DbName', 'value'),
    prevent_initial_call=True
)
def create_database(n_clicks, user, password, port, host, dbname):
    if get_callback_id() == 'PSQL_Button_CreateDatabase': return PSQL.create_database(DB_SETTINGS)
    else: return "Create Database"

# Select Database Dropdown Options
@ app.callback(
    Output('PSQL_Dropdown_ExistDbList', 'options'),
    Input('PSQL_Button_CreateDatabase', 'n_clicks'),
    prevent_initial_call=False
)
def populate_select_db_dropdown(n_clicks):
    if os.path.exists(PSQL.databases_csv_filepath()): return PSQL.get_db_names()
    else: return []

# Select Database Dropdown Selection
@app.callback(
    Input('PSQL_Dropdown_ExistDbList', 'value'),
    prevent_initial_call=True
)
def select_database(dbname):
    global DB_SETTINGS
    DB_SETTINGS = PSQL.get_db_settings(dbname)
    print(DB_SETTINGS)

########## Data Generation ##########

# Update Simulation Name
@app.callback(
    Input('simulation_name', 'value'),
    prevent_initial_call=True
)
def update_simulation_name(simulation_name):
    global SIMULATION_SETTINGS
    SIMULATION_SETTINGS['name'] = simulation_name

# Data Source Selection
@app.callback(
    Output('building_details', 'hidden'),
    Output('upload_files', 'hidden'),
    Output('simulation_name', 'value'),
    Output('generation_default_idf_filepath', 'data'),
    Output('generation_default_epw_filepath', 'data'),
    Input('data_source_selection', 'value'),
    prevent_initial_call=True
)
def data_source_selection(selection):

    if selection == 1: return False, True, no_update, None, None
    elif selection == 2: return True, False, no_update, None, None
    elif selection == 3:
        upload_idf_filepath = os.path.join(UPLOAD_DIRECTORY, os.path.basename(DEFAULT_IDF_FILEPATH))
        upload_epw_filepath = os.path.join(UPLOAD_DIRECTORY, os.path.basename(DEFAULT_EPW_FILEPATH))
        shutil.copy(DEFAULT_IDF_FILEPATH, upload_idf_filepath)
        shutil.copy(DEFAULT_EPW_FILEPATH, upload_epw_filepath)
        return True, True, 'Seattle_OfficeSmall', upload_idf_filepath, upload_epw_filepath
    else: return True, True, no_update, None, None

# PNNL Prototypes Drop-Down Menu
@app.callback(
    Output('level_1', 'options'),
    Output('level_2', 'options'),
    Output('level_3', 'options'),
    Output('location_selection', 'options'),
    Output('pnnl_prototype_idf_filepath', 'data'),
    Output('pnnl_prototype_weather_filepath', 'data'),
    Input('buildingType_selection', 'value'),
    Input('level_1', 'value'),
    Input('level_2', 'value'),
    Input('level_3', 'value'),
    Input('location_selection', 'value'),
    prevent_initial_call=True
)
def pnnl_prototypes_dropdown(building_type, level1, level2, level3, location):
    options1, options2, options3, location_options, idf_filepath, epw_filepath = EPGen.pnnl_prototypes_dropdown(building_type, level1, level2, level3, location, DATA_FOLDERPATH, UPLOAD_DIRECTORY)
    return options1, options2, options3, location_options, idf_filepath, epw_filepath

# Upload IDF File Interaction
@app.callback(
    Output('upload_idf', 'children'),
    Output('gen_upload_idf_filepath', 'data'),
    Input('upload_idf', 'filename'),
    Input('upload_idf', 'contents'),
    prevent_initial_call=True
)
def upload_idf(filename, content):
    try:
        upload_filepath = os.path.join(UPLOAD_DIRECTORY, filename)
        data = content.encode("utf8").split(b";base64,")[1]
        with open(upload_filepath, "wb") as fp:
            fp.write(base64.decodebytes(data))
        short_name = filename[:20] + "..." if len(filename) > 10 else filename
        return f"Uploaded {short_name}", upload_filepath
    except Exception as e:
        return "Upload Failed", None

# Upload EPW File Interaction
@app.callback(
    Output('upload_epw', 'children'),
    Output('gen_upload_epw_filepath', 'data'),
    Input('upload_epw', 'filename'),
    Input('upload_epw', 'contents'),
    prevent_initial_call=True
)
def upload_idf(filename, content):
    try:
        upload_filepath = os.path.join(UPLOAD_DIRECTORY, filename)
        data = content.encode("utf8").split(b";base64,")[1]
        with open(upload_filepath, "wb") as fp:
            fp.write(base64.decodebytes(data))
        short_name = filename[:20] + "..." if len(filename) > 10 else filename
        return f"Uploaded {short_name}", upload_filepath
    except Exception as e:
        return "Upload Failed", None

# Get Data Generation IDF and EPW File
@app.callback(
    Output('generation_idf_filepath', 'data'),
    Input('generation_default_idf_filepath', 'data'),
    Input('pnnl_prototype_idf_filepath', 'data'),
    Input('gen_upload_idf_filepath', 'data'),
    prevent_initial_call=True
)
def get_generation_idf_filepath(generation_default_idf_filepath, pnnl_prototype_idf_filepath, gen_upload_idf_filepath):
    if get_callback_id() == 'generation_default_idf_filepath' and valid_filepath(generation_default_idf_filepath):
        return generation_default_idf_filepath
    elif get_callback_id() == 'pnnl_prototype_idf_filepath' and valid_filepath(pnnl_prototype_idf_filepath):
        return pnnl_prototype_idf_filepath
    elif get_callback_id() == 'gen_upload_idf_filepath' and valid_filepath(gen_upload_idf_filepath):
        return gen_upload_idf_filepath
    else: return None

@app.callback(
    Output('generation_epw_filepath', 'data'),
    Input('generation_default_epw_filepath', 'data'),
    Input('pnnl_prototype_weather_filepath', 'data'),
    Input('gen_upload_epw_filepath', 'data'),
    prevent_initial_call=True
)
def get_generation_epw_filepath(generation_default_epw_filepath, pnnl_prototype_epw_filepath, gen_upload_epw_filepath):
    if get_callback_id() == 'generation_default_epw_filepath' and valid_filepath(generation_default_epw_filepath):
        return generation_default_epw_filepath
    elif get_callback_id() == 'pnnl_prototype_epw_filepath' and valid_filepath(pnnl_prototype_epw_filepath):
        return pnnl_prototype_epw_filepath
    elif get_callback_id() == 'gen_upload_epw_filepath' and valid_filepath(gen_upload_epw_filepath):
        return gen_upload_epw_filepath
    else: return None

# Get Building Information
@app.callback(
    Output('building_information', 'data'),
    Input('generation_idf_filepath', 'data'),
    prevent_initial_call=True
)
def get_building_information(idf_filepath):
    if valid_filepath(idf_filepath):
        try:
            building_information = PSQL.get_building_information(idf_filepath)
            return building_information
        except Exception as e:
            return None
    else: return None

# Callback triggered by change in IDF and EPW filepath.
@app.callback(
    Output('simulation_details', 'hidden'),
    Input('generation_idf_filepath', 'data'),
    Input('generation_epw_filepath', 'data'),
    prevent_initial_call=True
)
def unhide_simulation_details(idf_filepath, epw_filepath):
    if valid_filepath(idf_filepath) and valid_filepath(epw_filepath):
        building_information = PSQL.get_building_information(idf_filepath)
        BUILDING_INFORMATION = building_information
        return False
    else: return True

# Simulation Details
@app.callback(
    Output('gen_simulation_settings', 'data'),
    Input('simulation_name', 'value'),
    Input('sim_TimeStep', 'value'),
    Input('sim_run_period', 'start_date'),
    Input('sim_run_period', 'end_date'),
    Input('simReportFreq_selection', 'value'),
    prevent_initial_call=True
)
def update_simulation_details(simulation_name, timestep, start_date, end_date, report_freq_selection):
    global SIMULATION_SETTINGS
    SIMULATION_SETTINGS['name'] = simulation_name
    SIMULATION_SETTINGS['timestep_minutes'] = timestep
    SIMULATION_SETTINGS['start_datetime'] = format_datetime(start_date)
    SIMULATION_SETTINGS['end_datetime'] = format_datetime(end_date)
    SIMULATION_SETTINGS['reporting_frequency'] = report_freq_selection
    return SIMULATION_SETTINGS

# Unhide Generate Variables
@app.callback(
    Output('generate_variables', 'hidden'),
    Input('generation_idf_filepath', 'data'),
    Input('generation_epw_filepath', 'data'),
    prevent_initial_call=True
)
def unhide_generate_variables_button(idf_filepath, epw_filepath):
    if valid_filepath(idf_filepath) and valid_filepath(epw_filepath): return False
    else: return True

# Generate Variables Button
@app.callback(
    Output('EPGen_Button_GenerateVariables', 'children'),
    Output('custom_variable_selection', 'options'),
    Output('generate_variables_initial_run_eio_filepath', 'data'),
    Output('generate_variables_initial_run_rdd_filepath', 'data'),
    Input('EPGen_Button_GenerateVariables', 'n_clicks'),
    Input('pnnl_prototype_idf_filepath', 'data'),
    Input('gen_upload_idf_filepath', 'data'),
    prevent_initial_call=True
)
def generate_variables(n_clicks, val1, val2):

    if get_callback_id() == 'EPGen_Button_GenerateVariables':
        try:
            eio_filepath, rdd_filepath, variables_list = EPGen.generate_variables(DATA_IDF_FILEPATH, DATA_EPW_FILEPATH)
            INITIAL_RUN_EIO_FILEPATH = eio_filepath
            INITIAL_RUN_RDD_FILEPATH = rdd_filepath
            return 'Variables Generated', variables_list, eio_filepath, rdd_filepath
        except Exception as e:
            return 'Failed to Generate', [], None, None
    else: return 'Generate Variables', [], None, None

# Variable Selection
@app.callback(
    Input('preselected_variable_selection', 'value'),
    Input('custom_variable_selection', 'value'),
    Input('EPGen_Radiobutton_VariableSelection', 'value'), # 1: All Preselected Variables 2: Select Variables
    prevent_initial_call=True
)
def variable_selection(preselected_variable_selection, custom_variable_selection, choice):
    global SIMULATION_SETTINGS
    if choice == 1:
        SIMULATION_SETTINGS['variables'] = PRESELECTED_VARIABLES
    elif choice == 2:
        SIMULATION_SETTINGS['variables'] = preselected_variable_selection + custom_variable_selection

@app.callback(
    Output('schedules', 'hidden'),
    Input('edit_or_keep_schedules_button', 'value'),
    Input('generation_idf_filepath', 'data'),
    Input('generation_epw_filepath', 'data'),
    prevent_initial_call=True
)
def unhide_edit_schedules(button_selection, idf_filepath, epw_filepath):
    if button_selection == 1 and valid_filepath(idf_filepath) and valid_filepath(epw_filepath): return False
    else: return True

# What will cause the schedule dropdowns to change: new idf, new epw
@app.callback(
    Output('people_schedules', 'options'),
    Output('equip_schedules', 'options'),
    Output('light_schedules', 'options'),
    Output('heating_schedules', 'options'),
    Output('cooling_schedules', 'options'),
    Output('temperature_schedules', 'options'),
    Input('edit_or_keep_schedules_button', 'value'),
    Input('generate_variables_initial_run_eio_filepath', 'data'),
    Input('generation_idf_filepath', 'data'),
    Input('generation_epw_filepath', 'data'),
    prevent_initial_call=True
)
def fill_schedule_dropdowns(button_selection, eio_filepath, idf_filepath, epw_filepath):

    if button_selection == 2: return no_update * 6

    if not valid_filepath(eio_filepath) and valid_filepath(idf_filepath) and valid_filepath(epw_filepath):
        rdd_filepath, eio_filepath = EPGen.initial_run(idf_filepath, epw_filepath)

    if valid_filepath(eio_filepath):
        schedules = EPGen.get_schedules(eio_filepath, idf_filepath)
        return (
            schedules['people_schedules'],
            schedules['equipment_schedules'],
            schedules['light_schedules'],
            schedules['heating_schedules'],
            schedules['cooling_schedules'],
            schedules['temperature_schedules']
        )
    else: return [no_update] * 6

# Handle Schedule Selection - Makes sure only one Schedule is selected at a time.
@app.callback(
    Output('schedule_name', 'data'),
    Output('people_schedules', 'value'),
    Output('equip_schedules', 'value'),
    Output('light_schedules', 'value'),
    Output('heating_schedules', 'value'),
    Output('cooling_schedules', 'value'),
    Output('temperature_schedules', 'value'),
    Input('people_schedules', 'value'),
    Input('equip_schedules', 'value'),
    Input('light_schedules', 'value'),
    Input('heating_schedules', 'value'),
    Input('cooling_schedules', 'value'),
    Input('temperature_schedules', 'value'),
    prevent_initial_call=True
)
def handle_schedule_selection(people_schedule_selection, equip_schedule_selection, light_schedule_selection, heating_schedule_selection, cooling_schedule_selection, temperature_schedule_selection):
    if get_callback_id() == 'people_schedules':
        return people_schedule_selection, no_update, [], [], [], [], []
    elif get_callback_id() == 'equip_schedules':
        return equip_schedule_selection, [],no_update,[],[],[],[]
    elif get_callback_id() == 'light_schedules':
        return light_schedule_selection, [], [], no_update,[],[],[]
    elif get_callback_id() == 'heating_schedules':
        return heating_schedule_selection, [], [], [], no_update,[],[]
    elif get_callback_id() == 'cooling_schedules':
        return cooling_schedule_selection, [], [], [], [], no_update,[]
    elif get_callback_id() == 'temperature_schedules':
        return temperature_schedule_selection, [], [], [], [], [], no_update

# Upload Selected Schedule
@app.callback(
    Output('schedule_input', 'value'),
    Input('load_schedule_button', 'n_clicks'),
    State('generation_idf_filepath', 'data'),
    State('schedule_name', 'data'),
    prevent_initial_call=True
)
def load_schedule(n_clicks, idf_filepath, schedule_name):
    if schedule_name is not None:
        text = EPGen.schedule_compact_to_text(idf_filepath, schedule_name)
        return text
    else: return ''

# Update Schedule Selection
@app.callback(
    Output('update_schedule_button', 'children'),
    Input('update_schedule_button', 'n_clicks'),
    State('schedule_name', 'data'),
    State('schedule_input', 'value'),
    State('generation_idf_filepath', 'data'),
    prevent_initial_call = True
)
def update_schedule(n_clicks, schedule_name, schedule_input, idf_filepath):

    try:
        EPGen.update_schedule(idf_filepath, schedule_name, schedule_input)
        return "Schedule Updated Successfully"
    except Exception as e:
        print(e)
        return 'Failed to Update'

# Unhide Generate Data Button
# Needed for Generation: Valid IDF Path, Valid EPW Path, Valid Simulation Settings.
@app.callback(
    Output('final_download', 'hidden'),
    Input('generation_idf_filepath', 'data'),
    Input('generation_epw_filepath', 'data'),
    Input('gen_simulation_settings', 'data'),
    prevent_initial_call = True)
def unhide_generate_data_button(idf_filepath, epw_filepath, simulation_settings):
    if valid_filepath(idf_filepath) and valid_filepath(epw_filepath):
        for key, value in simulation_settings.items():
            if key == 'ep_version' or (value is not None and value != '' and value != []):
                pass
            else: return True
    else: return True
    return False

# Generate Data
@app.callback(
    Output('EPGen_Button_GenerateData', 'children'),
    Output('results_filepaths', 'data'),
    Input('EPGen_Button_GenerateData', 'n_clicks'),
    prevent_initial_call = True
)
def generate_data(n_clicks):
    global RESULTS_FILEPATHS
    try:
        RESULTS_FILEPATHS['variables_pickle_filepath'], RESULTS_FILEPATHS['eio_pickle_filepath'] = EPGen.generate_data(DATA_IDF_FILEPATH, DATA_EPW_FILEPATH, SIMULATION_SETTINGS, RESULTS_FOLDERPATH)
        return 'Data Generated', RESULTS_FILEPATHS
    except Exception as e:
        return "Generation Failed", no_update

# Unhide Download Buttons
@app.callback(
    Output('download_variables_pickle_button', 'hidden'),
    Output('download_eio_pickle_button', 'hidden'),
    Output('upload_to_db_button', 'hidden'),
    Input('results_filepaths', 'data'),
    Input('data_source_selection', 'value'), # Refreshes Everything
    prevent_initial_call = True
)
def unhide_download_buttons(results_filepaths, trig):
    global RESULTS_FILEPATHS
    if RESULTS_FILEPATHS['variables_pickle_filepath'] is not None and RESULTS_FILEPATHS['eio_pickle_filepath'] is not None:
        return False, False, False
    else: return True, True, True

# Download Variables Pickle
@app.callback(
    Output('download_variables_pickle_button', 'children'),
    Output('download_variables_pickle', 'data'),
    Input('download_variables_pickle_button', 'n_clicks'),
    prevent_initial_call = True
)
def download_variables_pickle(n_clicks):
    return 'Downloaded Variables Pickle', dcc.send_file(RESULTS_FILEPATHS['variables_pickle_filepath'])

# Download Eio Pickle
@app.callback(
    Output('download_eio_pickle_button', 'children'),
    Output('download_eio_pickle', 'data'),
    Input('download_eio_pickle_button', 'n_clicks'),
    prevent_initial_call = True
)
def download_eio_pickle(n_clicks):
    return 'Downloaded Eio Pickle', dcc.send_file(RESULTS_FILEPATHS['eio_pickle_filepath'])

# Upload to DB Button
@app.callback(
    Output('upload_to_db_button', 'children'),
    Input('upload_to_db_button', 'n_clicks'),
    prevent_initial_call = True
)
def upload_to_db(n_clicks):
    global BUILDING_INFORMATION, ZONES_DF
    try:
        BUILDING_INFORMATION['building_id'], ZONES_DF = EPGen.upload_to_db(DATA_IDF_FILEPATH, DATA_EPW_FILEPATH, SIMULATION_SETTINGS, BUILDING_INFORMATION, DB_SETTINGS, RESULTS_FILEPATHS)
        return 'Uploaded to Database'
    except Exception as e:
        return "Upload Failed"


##########################################################################################################

#################### Aggregation #########################################################################

##########################################################################################################

# Unhide Input Files Upload Menu
@app.callback(
    Output(component_id = 'agg_inputs_upload_files', component_property = 'hidden'),
    Input(component_id = 'agg_input_selection', component_property = 'value'), # 1: Continue Session, 2: Upload Files
    prevent_initial_call = True)
def unhide_upload_files(value):
    if value == 2: return False
    else: return True

# Upload Variables Pickle
@app.callback(
    Output('agg_upload_variables_pickle', 'children'),
    Output('upload_variable_pickle_filepath', 'data'),
    Input('agg_upload_variables_pickle', 'filename'),
    Input('agg_upload_variables_pickle', 'contents'),
    prevent_initial_call = True)
def agg_upload_variables_pickle(filename, contents):
    global RESULTS_FILEPATHS

    try:
        upload_filepath = os.path.join(RESULTS_FOLDERPATH, filename)
        data = contents.encode("utf8").split(b";base64,")[1]
        with open(upload_filepath, "wb") as fp:
            fp.write(base64.decodebytes(data))
        RESULTS_FILEPATHS['variables_pickle_filepath'] = upload_filepath
        short_name = filename[:20] + "..." if len(filename) > 10 else filename
        return f"Uploaded {short_name}", upload_filepath
    except Exception as e:
        return "Upload Failed", None

# Upload EIO Pickle Filepath
@app.callback(
    Output('agg_upload_eio_pickle', 'children'),
    Output('upload_eio_pickle_filepath', 'data'),
    Input('agg_upload_eio_pickle', 'filename'),
    Input('agg_upload_eio_pickle', 'contents'),
    prevent_initial_call = True)
def agg_upload_eio_pickle(filename, contents):
    global RESULTS_FILEPATHS

    try:
        upload_filepath = os.path.join(RESULTS_FOLDERPATH, filename)
        data = contents.encode("utf8").split(b";base64,")[1]
        with open(upload_filepath, "wb") as fp:
            fp.write(base64.decodebytes(data))
        RESULTS_FILEPATHS['eio_pickle_filepath'] = upload_filepath
        short_name = filename[:20] + "..." if len(filename) > 10 else filename
        return f"Uploaded {short_name}", upload_filepath
    except Exception as e:
        return "Upload Failed", None

# Set Inputs Filepaths for Aggregation
@app.callback(
    Output('agg_input_variables_pickle_filepath', 'data'),
    Output('agg_input_eio_pickle_filepath', 'data'),
    Input('results_filepaths', 'data'),
    Input('upload_variable_pickle_filepath', 'data'),
    Input('upload_eio_pickle_filepath', 'data'),
    State('agg_input_selection', 'value'),
    prevent_initial_call = True
)
def agg_set_input_filepaths(results_filepaths, upload_variables, upload_eio, input_selection):
    if input_selection == 1 and valid_filepath(results_filepaths['variables_pickle_filepath']) and valid_filepath(results_filepaths['eio_pickle_filepath']):
        return results_filepaths['variables_pickle_filepath'], results_filepaths['eio_pickle_filepath']
    elif input_selection == 2 and valid_filepath(upload_variables) and valid_filepath(upload_eio):
        return upload_variables, upload_eio
    else: return None, None

@app.callback(
    Output('agg_variables_menu', 'hidden'),
    Input('agg_input_variables_pickle_filepath', 'data'),
    Input('agg_input_eio_pickle_filepath', 'data'),
    prevent_initial_call = True)
def unhide_agg_variables_menu(upload_variables, upload_eio):
    if valid_filepath(upload_variables) and valid_filepath(upload_eio): return False
    else: return True

@app.callback(
    Output('agg_variable_selection', 'options'),
    Input('agg_variables_menu', 'hidden'),
    State('agg_input_variables_pickle_filepath', 'data'),
    prevent_initial_call = True)
def agg_populate_available_variables_dropdown(variables_menu_hidden, variables_pickle_filepath):
    if variables_menu_hidden == False:
        variables = EPAgg.get_variable_list(variables_pickle_filepath)
        return variables
    else: return []

@app.callback(
    Output('aggregation_details_menu', 'hidden'),
    Input('agg_input_variables_pickle_filepath', 'data'),
    Input('agg_input_eio_pickle_filepath', 'data'),
    prevent_initial_call = True)
def unhide_aggregation_details_menu(variables_pickle_filepath, eio_pickle_filepath):
    if valid_filepath(variables_pickle_filepath) and valid_filepath(eio_pickle_filepath): return False
    else: return True

@app.callback(
    Output('agg_zone_list', 'options'),
    Input('aggregation_details_menu', 'hidden'),
    State('agg_input_eio_pickle_filepath', 'data'),
    prevent_initial_call = True
)
def agg_populate_available_zones_dropdown(aggregation_details_hidden, eio_pickle_filepath):
    if aggregation_details_hidden == False:
        zone_list = EPAgg.get_zone_list(eio_pickle_filepath)
        return zone_list
    else: return []

@app.callback(
    Output('aggregation_settings', 'data'),
    Input('aggregate_to_selection', 'value'),
    Input('custom_aggregation_zone_list', 'value'),
    Input('aggregation_type', 'value'),
    Input('agg_variable_all_or_select', 'value'),
    Input('agg_variable_selection', 'value'),
    State('agg_zone_list', 'options'),
    State('agg_variable_selection', 'options'),
    prevent_initial_call = True)
def set_aggregation_settings(aggregate_to_selection, aggregation_zone_list, aggregation_type, agg_variable_button_selection, agg_variable_selection, zone_list, variable_list):

    if agg_variable_button_selection == 1 and len(variable_list) > 0:
        variable_selection = variable_list
    elif agg_variable_button_selection == 2 and len(agg_variable_selection) > 0:
        variable_selection = agg_variable_selection
    else: return no_update

    if aggregate_to_selection == 1 and zone_list is not None:
        final_aggregation_zone_list = []
        final_aggregation_zone_list.append(zone_list)
    elif aggregate_to_selection == 2 and aggregation_zone_list is not None:
        try:
            split1 = aggregation_zone_list.split(';')
            final_aggregation_zone_list = []
            for list in split1:
                split2 = list.split(',')
                inner_list = []
                for item in split2:
                    inner_list.append(item)
                final_aggregation_zone_list.append(inner_list)
        except Exception as e:
            final_aggregation_zone_list = [[]]
    else: return no_update

    aggregation_settings = {
        'aggregation_zone_list': final_aggregation_zone_list,
        'aggregation_type': aggregation_type,
        'aggregation_variable_list': variable_selection
    }

    return aggregation_settings

@app.callback(
    Output('aggregate_data_button', 'hidden'),
    Output('aggregation_final_box', 'hidden'),
    Input('aggregation_settings', 'data'),
    prevent_initial_call = True
)
def unhide_aggregate_data_button(aggregation_settings):
    if aggregation_settings['aggregation_zone_list'] != [[]] and aggregation_settings['aggregation_variable_list'] != [] and aggregation_settings['aggregation_type'] is not None:
        return False, False
    else: return True, True

@app.callback(
    Output('aggregate_data_button', 'children'),
    Output('aggregation_pickle_filepath', 'data'),
    Input('aggregate_data_button', 'n_clicks'),
    State('aggregation_settings', 'data'),
    State('agg_input_variables_pickle_filepath', 'data'),
    State('agg_input_eio_pickle_filepath', 'data'),
    prevent_initial_call = True
)
def aggregate_data(n_clicks, aggregation_settings, variables_pickle_filepath, eio_pickle_filepath):
    global RESULTS_FILEPATHS
    try:
        aggregated_pickle_filepath = EPAgg.aggregate_data(aggregation_settings, variables_pickle_filepath, eio_pickle_filepath)
        RESULTS_FILEPATHS[aggregated_pickle_filepath] = aggregated_pickle_filepath
        return 'Data Aggregated', aggregated_pickle_filepath
    except Exception as e:
        return 'Aggregation Failed', no_update

@app.callback(
    Output('agg_download_button', 'hidden'),
    Input('aggregation_pickle_filepath', 'data'),
    prevent_initial_call = True
)
def unhide_download_buttons(aggregation_pickle_filepath):
    if valid_filepath(aggregation_pickle_filepath): return False
    else: return True

@app.callback(
    Output('agg_download_button', 'children'),
    Output('agg_download_files', 'data'),
    Input('agg_download_button', 'n_clicks'),
    State('aggregation_pickle_filepath', 'data'),
    prevent_initial_call = True
)
def agg_download_pickle(n_clicks, aggregation_pickle_filepath):
    if valid_filepath(aggregation_pickle_filepath):
        return 'Pickle File Downloaded', dcc.send_file(aggregation_pickle_filepath)
    else: return 'Download Failed', no_update


# Unhide Simulation Informaiton Box
@app.callback(
    Output('simulation_info_box', 'hidden'),
    Input('aggregation_pickle_filepath', 'data'),
)
def unhide_simulation_info_box(aggregation_pickle_filepath):
    if valid_filepath(aggregation_pickle_filepath): return False
    else: return True

@app.callback(
    Output('agg_upload_to_db_button', 'hidden'),
    Input('agg_simulation_name', 'value'),
    Input('agg_upload_to_db_custom_or_no', 'value'),
    Input('building_id','value'),
    Input('aggregation_pickle_filepath', 'data'),
    prevent_initial_call = True)
def unhide_upload_to_db_button(simulation_name, custom_or_no, building_id, pickle_filepath):
    if len(simulation_name)>0 and (custom_or_no == 1 or building_id > 0) and valid_filepath(pickle_filepath):
        return False
    else: return True

# Upload to DB Button
@app.callback(
    Output('agg_upload_to_db_button', 'children'),
    Input('agg_upload_to_db_button', 'n_clicks'),
    State('agg_input_variables_pickle_filepath', 'data'),
    State('agg_input_eio_pickle_filepath', 'data'),
    State('aggregation_pickle_filepath', 'data'),
    State('aggregation_settings', 'data'),
    State('agg_simulation_name', 'value'),
    State('agg_upload_to_db_custom_or_no', 'value'),
    State('building_id', 'value'),
    prevent_initial_call = True
)
def upload_to_db(n_clicks, variables_pickle_filepath, eio_pickle_filepath, aggregation_pickle_filepath, aggregation_settings, sim_name, custom_or_no, building_id):
    try:
        zones_df = EPAgg.upload_to_db(variables_pickle_filepath, eio_pickle_filepath, DB_SETTINGS, ZONES_DF, aggregation_pickle_filepath, aggregation_settings, sim_name, custom_or_no, building_id)
        return 'Uploaded to Database'
    except Exception as e:
        return 'Upload Failed'
"""


@app.callback(
    Output(component_id = 'EPAgg_Div_UploadFiles', component_property = 'hidden'),
    Output(component_id = 'EPAgg_Div_AggregationVariables', component_property = 'hidden'),
    Input(component_id = 'EPAgg_RadioButton_InputSelection', component_property = 'value'), # 1: Continue Session, 2: Upload Files
    prevent_initial_call = True)
def EPAgg_RadioButton_InputSelection_Interaction(value):

    global BUILDING_ID
    global SIMULATION_VARIABLE_LIST

    upload_div, variable_div = EPAgg.EPAgg_RadioButton_InputSelection_Interaction_Function(value)
    if USING_DATABASE:
        if (BUILDING_ID == None) and (value == 1):
            conn = PSQL.connect_to_database(DB_SETTINGS)
            BUILDING_ID = DB_Uploader.get_building_id(conn, BUILDING_TYPE, os.path.basename(DATA_IDF_FILEPATH))
        if (BUILDING_ID == None) or (value == 2):
            conn = PSQL.connect_to_database(DB_SETTINGS)
            BUILDING_ID = DB_Uploader.upload_custom_building(conn)

    return upload_div, variable_div

@app.callback(
    Output(component_id = 'EPAgg_Upload_Pickle', component_property = 'children'),
    State(component_id = 'EPAgg_Upload_Pickle', component_property = 'filename'),
    Input(component_id = 'EPAgg_Upload_Pickle', component_property = 'contents'),
    prevent_initial_call = True)
def EPAgg_Upload_Pickle_Interaction(filename, content):
    global VARIABLES_PICKLE_FILEPATH, BUILDING_TYPE, SIMULATION_RESULTS_FOLDERPATH
    message, variables_pickle_filepath = EPAgg.EPAgg_Upload_Pickle_Interaction_Function(filename, content)
    VARIABLES_PICKLE_FILEPATH = variables_pickle_filepath
    BUILDING_TYPE = 'Custom'

    simulation_results_folderpath = os.path.join(RESULTS_FOLDERPATH, SIMULATION_FOLDERNAME)
    if not os.path.exists(simulation_results_folderpath): mkdir(simulation_results_folderpath)
    SIMULATION_RESULTS_FOLDERPATH = simulation_results_folderpath

    # Get list of all possible variables
    global VARIABLES_PICKLE_VARIABLE_LIST
    VARIABLES_PICKLE_VARIABLE_LIST = EPAgg.get_variable_list(VARIABLES_PICKLE_FILEPATH)

    return message

@app.callback(
    Output(component_id = 'EPAgg_Upload_EIO', component_property = 'children'),
    Input(component_id = 'EPAgg_Upload_EIO', component_property = 'filename'),
    State(component_id = 'EPAgg_Upload_EIO', component_property = 'contents'),
    prevent_initial_call = True)
def EPAgg_Upload_EIO_Interaction(filename, content):
    global EIO_PICKLE_FILEPATH
    message, eio_pickle_filepath = EPAgg.EPAgg_Upload_EIO_Interaction_Function(filename, content)
    EIO_PICKLE_FILEPATH = eio_pickle_filepath
    return message

# Unhide Aggregation Details Window, populate Zone List dropdown.
@app.callback(
    Output(component_id = 'EPAgg_Div_AggregationDetails', component_property = 'hidden'),
    Output(component_id = 'EPAgg_DropDown_ZoneList', component_property = 'options'),
    Input(component_id = 'EPAgg_RadioButton_AggregationVariables', component_property = 'value'),
    Input(component_id = 'EPAgg_DropDown_PreselectedVariables', component_property = 'value'),
    prevent_initial_call = True)
def EPAgg_DropDown_AggregationVariables_Interaction(selection, value):
    div = EPAgg.EPAgg_DropDown_AggregationVariables_Interaction_Function(selection, value)
    zone_list = EPAgg.get_zone_list(EIO_PICKLE_FILEPATH)
    return div, zone_list

# Populate Variable Selection DropDown
@app.callback(
    Output(component_id = 'EPAgg_DropDown_PreselectedVariables', component_property = 'options'),
    # Output(component_id = 'EPAgg_DropDown_ZoneList', component_property = 'options'),
    # Input(component_id = 'EPAgg_RadioButton_InputSelection', component_property = 'value'), # 1: Continue Session 2: Upload Files
    Input(component_id = 'EPAgg_RadioButton_AggregationVariables', component_property = 'value'), # 1: All Variables 2: Select Variables
    Input(component_id = 'EPAgg_DropDown_PreselectedVariables', component_property = 'value'), # Variable Selection DropDown
    prevent_initial_call = True)
def EPAgg_RadioButton_AggregationVariables_Interaction(VariableSelection, Variable_DropDown_Selection):
    # pre_list, custom_list, zone_list = EPAgg.EPAgg_RadioButton_AggregationVariables_Interaction_Function(InputSelection, VariableSelection)
    global AGGREGATION_VARIABLE_SELECTION, VARIABLES_PICKLE_VARIABLE_LIST
    if VARIABLES_PICKLE_VARIABLE_LIST == None:
        VARIABLES_PICKLE_VARIABLE_LIST = EPAgg.get_variable_list(VARIABLES_PICKLE_FILEPATH)
    if VariableSelection == 1: aggregation_variable_selection = VARIABLES_PICKLE_VARIABLE_LIST # All Variables
    elif VariableSelection == 2: aggregation_variable_selection = Variable_DropDown_Selection # Selected Variables
    AGGREGATION_VARIABLE_SELECTION = aggregation_variable_selection
    return VARIABLES_PICKLE_VARIABLE_LIST

@app.callback(
    Output(component_id = 'EPAgg_Div_FinalDownload', component_property = 'hidden'),
    Input(component_id = 'EPAgg_DropDown_TypeOfAggregation', component_property = 'value'),
    prevent_initial_call = True)
def EPAgg_DropDown_TypeOfAggregation_Interaction(value):
    div = EPAgg.EPAgg_DropDown_TypeOfAggregation_Interaction_Function(value)
    return div

# Update Variable Selection
@app.callback(
    Input(component_id = 'EPAgg_RadioButton_AggregationVariables', component_property = 'value'),
    Input(component_id = 'EPAgg_DropDown_PreselectedVariables', component_property = 'value'),
    Input(component_id = 'EPAgg_DropDown_CustomVariables', component_property = 'value'),
    prevent_initial_call = True
)
def update_variables_list(button_value, preselected_variables, custom_variables):
    global SIMULATION_VARIABLE_LIST
    if button_value == 1: SIMULATION_VARIABLE_LIST = preselected_variables
    elif button_value == 2: SIMULATION_VARIABLE_LIST = custom_variables

# Update Aggregation Zone List
@app.callback(
    Input(component_id = 'EPAgg_RadioButton_AggregateTo', component_property = 'value'), # Aggregate to One or Custom Aggregation
    Input(component_id = 'EPAgg_DropDown_CustomAggregationZoneList', component_property = 'value'), # User Input List using commas and semicolon
)
def update_aggregation_zone_list(button_value, zone_list):
    global AGGREGATION_ZONE_LIST
    if button_value == 1: AGGREGATION_ZONE_LIST = 'one_zone'
    elif button_value == 2: AGGREGATION_ZONE_LIST = zone_list

@app.callback(
    Output(component_id = 'EPAgg_Button_Aggregate', component_property = 'children'),
    #State(component_id = 'EPAgg_RadioButton_AggregationVariables', component_property = 'value'),
    #State(component_id = 'EPAgg_DropDown_CustomVariables', component_property = 'value'),
    #State(component_id = 'EPAgg_RadioButton_AggregateTo', component_property = 'value'),
    #State(component_id = 'EPAgg_DropDown_CustomAggregationZoneList', component_property = 'value'),
    State(component_id = 'EPAgg_DropDown_TypeOfAggregation', component_property = 'value'),
    Input(component_id = 'EPAgg_Button_Aggregate', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPAgg_Button_Aggregate_Interaction(aggregation_type, n_clicks):
    global AGGREGATION_PICKLE_FILEPATH
    # message = EPAgg.EPAgg_Button_Aggregate_Interaction_Function(SIMULATION_VARIABLE_LIST, aggregate_to, custom_zone_list, Type_Aggregation, n_clicks)
    AGGREGATION_PICKLE_FILEPATH = EPAgg.aggregate_data(VARIABLES_PICKLE_FILEPATH, EIO_PICKLE_FILEPATH, SIMULATION_RESULTS_FOLDERPATH, AGGREGATION_VARIABLE_SELECTION, aggregation_type, AGGREGATION_ZONE_LIST)
    return "Aggregation Completed"

@app.callback(
    Output(component_id = 'EPAgg_Download_DownloadFiles', component_property = 'data'),
    Input(component_id = 'EPAgg_Button_Download', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPAgg_Button_Download_Interaction(n_clicks):
    download_path = EPAgg.EPAgg_Button_Download_Interaction_Function(AGGREGATION_PICKLE_FILEPATH)
    return download_path

##########################################################################################################

#################### Visualization #######################################################################

##########################################################################################################

@app.callback(
    Output(component_id = 'EPVis_Div_Datatobeselected', component_property = 'hidden', allow_duplicate = True),
    Output(component_id = 'EPVis_Div_UploadData', component_property = 'hidden'),
    Input(component_id = 'EPVis_RadioButton_DataSource', component_property = 'value'),
    prevent_initial_call = True)
def EPVis_RadioButton_DataSource_Interaction(data_source):
    data_selection, upload_data = EPVis.EPVis_RadioButton_DataSource_Interaction_Function(data_source)
    return data_selection, upload_data

@app.callback(
    Output(component_id = 'EPVis_Upload_GeneratedData', component_property = 'children'),
    Input(component_id = 'EPVis_Upload_GeneratedData', component_property = 'filename'),
    State(component_id = 'EPVis_Upload_GeneratedData', component_property = 'contents'),
    prevent_initial_call = False)
def EPVis_Upload_GeneratedData_Interaction(filename, content):
    message = EPVis.EPVis_Upload_GeneratedData_Interaction_Function(filename, content)
    return message

@app.callback(
    Output(component_id = 'EPVis_Upload_AggregatedData', component_property = 'children'),
    Output(component_id = 'EPVis_Div_Datatobeselected', component_property = 'hidden', allow_duplicate = True),
    Input(component_id = 'EPVis_Upload_AggregatedData', component_property = 'filename'),
    State(component_id = 'EPVis_Upload_AggregatedData', component_property = 'contents'),
    prevent_initial_call = True)
def EPVis_Upload_AggregatedData_Interaction(filename, content):
    message, data_selection = EPVis.EPVis_Upload_AggregatedData_Interaction_Function(filename, content)
    return message, data_selection

@app.callback(
    Output(component_id = 'EPVis_Div_DateRangeUploadedFile', component_property = 'hidden'),
    Output(component_id = 'EPVis_Div_DateRangeVis', component_property = 'hidden'),
    Output(component_id = 'EPVis_Div_SelectVariableGenerateData', component_property = 'hidden'),
    Output(component_id = 'EPVis_Div_SelectVariableAggregateData', component_property = 'hidden'),
    Output(component_id = 'EPVis_Button_DistGeneratedData', component_property = 'hidden'),
    Output(component_id = 'EPVis_Button_DistAggregatedData', component_property = 'hidden'),
    Output(component_id = 'EPVis_Button_DistBothData', component_property = 'hidden'),
    Output(component_id = 'EPVis_Row_GeneratedDataDetails', component_property = 'hidden'),
    Output(component_id = 'EPVis_Row_AggregatedDataDetails', component_property = 'hidden'),
    Output(component_id = 'EPVis_Button_ScatterBothData', component_property = 'hidden'),
    Output(component_id = 'EPVis_Button_TimeGeneratedData', component_property = 'hidden'),
    Output(component_id = 'EPVis_Button_TimeAggregatedData', component_property = 'hidden'),
    Output(component_id = 'EPVis_Button_TimeBothData', component_property = 'hidden'),
    Output(component_id = 'EPVis_DatePickerRange_UploadedFile', component_property = 'min_date_allowed'),
    Output(component_id = 'EPVis_DatePickerRange_UploadedFile', component_property = 'max_date_allowed'),
    Output(component_id = 'EPVis_DatePickerRange_Visualization', component_property = 'min_date_allowed'),
    Output(component_id = 'EPVis_DatePickerRange_Visualization', component_property = 'max_date_allowed'),
    Output(component_id = 'EPVis_DatePickerRange_UploadedFile', component_property = 'start_date'),
    Output(component_id = 'EPVis_DatePickerRange_UploadedFile', component_property = 'end_date'),
    Output(component_id = 'EPVis_DropDown_GeneratedDataTables', component_property = 'options'),
    Output(component_id = 'EPVis_DropDown_AggregatedDataTables', component_property = 'options'),

    State(component_id = 'EPVis_RadioButton_DataSource', component_property = 'value'),
    Input(component_id = 'EPVis_RadioButton_DataToBeSelected', component_property = 'value'),
    prevent_initial_call = True)
def EPVis_Radio_DataToBeSelected_Interaction(InputSelection, selection):
    date_range1, date_range2, var_gendata, var_aggrdata, button_dist_gen, button_dist_agg, button_dist_both, mean_gen, mean_agg, button_scat_both, button_time_gen, button_time_agg, button_time_both, min_date_upload, max_date_upload, min_date_upload, max_date_upload, min_date_upload, max_date_upload, Generated_Variables, Aggregated_Variables = EPVis.EPVis_Radio_DataToBeSelected_Interaction_Function(InputSelection, selection)
    return date_range1, date_range2, var_gendata, var_aggrdata, button_dist_gen, button_dist_agg, button_dist_both, mean_gen, mean_agg, button_scat_both, button_time_gen, button_time_agg, button_time_both, min_date_upload, max_date_upload, min_date_upload, max_date_upload, min_date_upload, max_date_upload, Generated_Variables, Aggregated_Variables

@app.callback(
    Output(component_id = 'EPVis_DropDown_GeneratedDataColumns', component_property = 'options'),
    Input(component_id = 'EPVis_DropDown_GeneratedDataTables', component_property = 'value'),
    prevent_initial_call = True)
def EPVis_DropDown_GeneratedDataTables_Interaction(variable):
    columns = EPVis.EPVis_DropDown_GeneratedDataTables_Interaction_Function(variable)
    return columns

@app.callback(
    Output(component_id = 'EPVis_DropDown_AggregatedDataColumns', component_property = 'options'),
    Input(component_id = 'EPVis_DropDown_AggregatedDataTables', component_property = 'value'),
    prevent_initial_call = True)
def EPVis_DropDown_AggregatedDataTables_Interaction(variable):
    columns = EPVis.EPVis_DropDown_AggregatedDataTables_Interaction_Function(variable)
    return columns

@app.callback(
    Output(component_id = 'EPVis_Graph_Distribution', component_property = 'figure', allow_duplicate = True),
    Output(component_id = 'EPVis_Table_GeneratedData', component_property = 'data', allow_duplicate = True),
    State(component_id = 'EPVis_DropDown_GeneratedDataTables', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_GeneratedDataColumns', component_property = 'value'),
    Input(component_id = 'EPVis_Button_DistGeneratedData', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPVis_Button_DistGeneratedData_Interaction(table, column, n_clicks):
    figure,data = EPVis.EPVis_Button_DistGeneratedData_Interaction_Function(table, column, n_clicks)
    return figure,data

@app.callback(
    Output(component_id = 'EPVis_Graph_Distribution', component_property = 'figure',allow_duplicate = True),
    State(component_id = 'EPVis_DropDown_AggregatedDataTables', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_AggregatedDataColumns', component_property = 'value'),
    Input(component_id = 'EPVis_Button_DistAggregatedData', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPVis_Button_DistAggregatedData_Interaction(table, column, n_clicks):
    figure = EPVis.EPVis_Button_DistAggregatedData_Interaction_Function(table, column, n_clicks)
    return figure

@app.callback(
    Output(component_id = 'EPVis_Graph_Distribution', component_property = 'figure',allow_duplicate = True),
    State(component_id = 'EPVis_DropDown_GeneratedDataTables', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_GeneratedDataColumns', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_AggregatedDataTables', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_AggregatedDataColumns', component_property = 'value'),
    Input(component_id = 'EPVis_Button_DistBothData', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPVis_Button_DistBothData_Interaction(table_gen, column_gen, table_agg, column_agg, n_clicks):
    figure = EPVis.EPVis_Button_DistBothData_Interaction_Function(table_gen, column_gen, table_agg, column_agg, n_clicks)
    return figure

@app.callback(
    Output(component_id = 'EPVis_H5_ScatterPlotComment', component_property = 'hidden'),
    Input(component_id = 'EPVis_DropDown_GeneratedDataColumns', component_property = 'value'),
    Input(component_id = 'EPVis_DropDown_AggregatedDataColumns', component_property = 'value'),
    prevent_initial_call = True)
def EPVis_H5_ScatterPlotComment_Interaction(gen_column, agg_column):
    comment = EPVis.EPVis_H5_ScatterPlotComment_Interaction_Function(gen_column, agg_column)
    return comment

@app.callback(
    Output(component_id = 'EPVis_Graph_Scatter', component_property = 'figure',allow_duplicate = True),
    State(component_id = 'EPVis_DropDown_GeneratedDataTables', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_GeneratedDataColumns', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_AggregatedDataTables', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_AggregatedDataColumns', component_property = 'value'),
    Input(component_id = 'EPVis_Button_ScatterBothData', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPVis_Button_ScatGeneratedData_Interaction(table_gen, column_gen, table_agg, column_agg, n_clicks):
    figure = EPVis.EPVis_Button_ScatGeneratedData_Interaction_Function(table_gen, column_gen, table_agg, column_agg, n_clicks)
    return figure

@app.callback(
    Output(component_id = 'EPVis_Graph_TimeSeries', component_property = 'figure',allow_duplicate = True),
    State(component_id = 'EPVis_DropDown_GeneratedDataTables', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_GeneratedDataColumns', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_AggregatedDataTables', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_AggregatedDataColumns', component_property = 'value'),
    Input(component_id = 'EPVis_Button_TimeGeneratedData', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPVis_Button_TimeGeneratedData_Interaction(table_gen, column_gen, table_agg, column_agg, n_clicks):
    figure = EPVis.EPVis_Button_TimeGeneratedData_Interaction_Function(table_gen, column_gen, table_agg, column_agg, n_clicks)
    return figure

@app.callback(
    Output(component_id = 'EPVis_Graph_TimeSeries', component_property = 'figure',allow_duplicate = True),
    State(component_id = 'EPVis_DropDown_GeneratedDataTables', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_GeneratedDataColumns', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_AggregatedDataTables', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_AggregatedDataColumns', component_property = 'value'),
    Input(component_id = 'EPVis_Button_TimeAggregatedData', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPVis_Button_TimeAggregatedData_Interaction(table_gen, column_gen, table_agg, column_agg, n_clicks):
    figure = EPVis.EPVis_Button_TimeGeneratedData_Interaction_Function(table_gen, column_gen, table_agg, column_agg, n_clicks)
    return figure
    
@app.callback(
    Output(component_id = 'EPVis_Graph_TimeSeries', component_property = 'figure',allow_duplicate = True),
    State(component_id = 'EPVis_DropDown_GeneratedDataTables', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_GeneratedDataColumns', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_AggregatedDataTables', component_property = 'value'),
    State(component_id = 'EPVis_DropDown_AggregatedDataColumns', component_property = 'value'),
    Input(component_id = 'EPVis_Button_TimeGeneratedData', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPVis_Button_TimeGeneratedData_Interaction(table_gen, column_gen, table_agg, column_agg, n_clicks):
    # Generated Data
    Generated_Dict_file = open(os.path.join(WORKSPACE_DIRECTORY,'Visualization','Generated.pickle'),"rb")
    Generated_OutputVariable_Dict = pickle.load(Generated_Dict_file)

    # Aggregated Data
    Aggregated_Dict_file = open(os.path.join(WORKSPACE_DIRECTORY,'Visualization','Aggregated.pickle'),"rb")
    Aggregated_OutputVariable_Dict = pickle.load(Aggregated_Dict_file)

    if table_gen is not None and column_gen is not None:
        Data_DF = Generated_OutputVariable_Dict[table_gen][column_gen]
    else:
        Data_DF = pd.DataFrame()

    # Creating DF for plotting
    column_agg_new = []
    for item in column_agg:
        Current_DF = Aggregated_OutputVariable_Dict[item][table_agg].to_frame()
        column_name = "".join([item, table_agg])
        column_agg_new.append(column_name)
        Current_DF = Current_DF.rename(columns={table_agg: column_name})
        Data_DF = pd.concat([Data_DF, Current_DF], axis=1)

    if column_gen is not None:
        time_list = pd.DataFrame(Generated_OutputVariable_Dict['DateTime_List'], columns=['Date'])
    elif column_agg is not None:
        time_list = pd.DataFrame(Aggregated_OutputVariable_Dict['DateTime_List'], columns=['Date'])

    # Merging the dataframes
    merged_df = pd.concat([time_list, Data_DF], axis=1)

    # Melting the dataframe for Plotly Express
    if column_gen is not None:
        variable_list = column_gen+column_agg_new
    else:
        variable_list = column_agg_new
    melted_df = merged_df.melt(id_vars='Date', value_vars=variable_list, var_name='Variable', value_name='Value')

    # Plotting the time series using Plotly Express
    figure = px.line(melted_df, x='Date', y='Value', color='Variable', labels={'Date': 'Date', 'Value': 'Variable', 'Variable': 'Data Series'})

    return figure


# Want to make sure windows go away when 'No' is selected.
@app.callback(
    Output(component_id = 'PSQL_Div_CreateSelectDatabase', component_property = 'hidden'),
    Input(component_id = 'PSQL_RadioButton_UsingDatabase', component_property = 'value'),
    prevent_initial_call = True)
def PSQL_Radiobutton_UsingDatabase_Interaction(selection):
    global USING_DATABASE
    database_selection = PSQL.PSQL_Radiobutton_UsingDatabase_Interaction_Function(selection)
    if selection == 1: USING_DATABASE = True
    elif selection == 2: USING_DATABASE = False
    return database_selection

@app.callback(
    Output(component_id = 'PSQL_Div_EnterInfo', component_property = 'hidden'),
    Output(component_id = 'PSQL_Div_SelectDbfromExist', component_property = 'hidden'),
    Input(component_id = 'PSQL_RadioButton_CreateSelectDatabase', component_property = 'value'),
    prevent_initial_call = True)
def PSQL_Radiobutton_CreateSelectDatabase_Interaction(selection):
    enterinfo_hidden, existdblist_hidden = PSQL.PSQL_Radiobutton_CreateSelectDatabase_Interaction_Function(selection)
    return enterinfo_hidden, existdblist_hidden

### Casey's Code ###

@app.callback(
    Output('PSQL_Div_EnterInfo', 'children'),  # You can also use a different feedback div
    Input('PSQL_Button_CreateDatabase', 'n_clicks'),
    State('PSQL_Textarea_Username', 'value'),
    State('PSQL_Textarea_Password', 'value'),
    State('PSQL_Textarea_PortNumber', 'value'),
    State('PSQL_Textarea_DbName', 'value'),
    prevent_initial_call=True
)
def on_create_database(n_clicks, username, password, port, dbname):
    global DB_SETTINGS
    print(f"Creating database {dbname}\n Username: {username}\n Password: {password}\n Port: {port}")
    DB_SETTINGS = PSQL.create_database(username, password, port, dbname)

@app.callback(
    Output('PSQL_Dropdown_ExistDbList', 'options'),
    Input('PSQL_RadioButton_CreateSelectDatabase', 'value'),
    prevent_initial_call=True
)
def populate_existing_db_dropdown(selection):
    dropdown_options = PSQL.populate_existing_db_dropdown(selection)
    return dropdown_options

@app.callback(
    #Output('PSQL_Div_CreateStatus', 'children'),  # or some other feedback/output
    Input('PSQL_Dropdown_ExistDbList', 'value'),
    #prevent_initial_call=True
)
def handle_existing_db_selection(selected_dbname):
    global DB_SETTINGS
    DB_SETTINGS = PSQL.get_conn_from_dbname(selected_dbname)

@ app.callback(
    Output('EPGen_Button_UploadtoDb', 'children'),
    Input('EPGen_Button_UploadtoDb', 'n_clicks'),
    prevent_initial_call=True
)
def gen_upload_to_db(n_clicks):

    global BUILDING_ID, ZONES_DF
    conn = PSQL.connect_to_database(DB_SETTINGS)
    button_text, building_id, zones_df = EPGen.upload_to_db(conn, BUILDING_TYPE, VARIABLES_PICKLE_FILEPATH, EIO_PICKLE_FILEPATH, SIMULATION_RESULTS_FOLDERPATH, SIMULATION_SETTINGS, SIMULATION_VARIABLE_LIST)
    BUILDING_ID = building_id
    conn.close()
    ZONES_DF = zones_df
    return button_text

@ app.callback(
    Output('EPAgg_Button_UploadtoDb', 'children'),
    Input('EPAgg_Button_UploadtoDb', 'n_clicks'),
    prevent_initial_call=True
)
def agg_upload_to_db(n_clicks):

    global BUILDING_ID
    conn = PSQL.connect_to_database(DB_SETTINGS)

    simulation_settings = EPAgg.get_simulation_settings(VARIABLES_PICKLE_FILEPATH)

    message = EPAgg.upload_to_db(conn, DATA_EPW_FILEPATH, AGGREGATION_PICKLE_FILEPATH, EIO_PICKLE_FILEPATH, BUILDING_ID, simulation_settings, AGGREGATION_ZONE_LIST, ZONES_DF)

    return message
    
"""

# Running the App
if __name__ == '__main__':
    app.run(port=4050)
    



