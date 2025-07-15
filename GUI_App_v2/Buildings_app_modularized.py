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

PRESELECTED_VARIABLES = EPGen.preselected_variables()

DEFAULT_IDF_FILEPATH = os.path.join(DATA_FOLDERPATH, 'Commercial_Prototypes', 'ASHRAE', '90_1_2013', 'ASHRAE901_OfficeSmall_STD2013_Seattle.idf')
DEFAULT_EPW_FILEPATH = os.path.join(DATA_FOLDERPATH, 'TMY3_WeatherFiles_Commercial', 'USA_WA_Seattle-Tacoma.Intl.AP.727930_TMY3.epw')

CUSTOM_BUILDING_INFORMATION = {
    "building_type": "Custom"
}

# Instantiate our App and incorporate BOOTSTRAP theme Stylesheet
# Themes - https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/#available-themes
# Themes - https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/explorer/
# hackerthemes.com/bootstrap-cheatsheet/
app = Dash(__name__, external_stylesheets=[dbc.themes.LITERA], suppress_callback_exceptions=True)

# App Layout using Dash Bootstrap
app.layout = dbc.Container([

    #PSQL
    dcc.Store(id='db_settings', data=None),
    dcc.Store(id='generation_zones_df', data=None),
    dcc.Store(id='generation_building_id', data=None),

    # Generation Data Source Filepaths
    dcc.Store(id='gen_upload_idf_filepath', data=None),
    dcc.Store(id='gen_upload_epw_filepath', data=None),
    dcc.Store(id='pnnl_prototype_idf_filepath', data=None),
    dcc.Store(id='pnnl_prototype_weather_filepath', data=None),
    dcc.Store(id='generation_default_idf_filepath', data=None),
    dcc.Store(id='generation_default_epw_filepath', data=None),
    dcc.Store(id='generation_idf_filepath', data=None),
    dcc.Store(id='generation_epw_filepath', data=None),

    # Generation Simulation Parameters
    dcc.Store(id='gen_simulation_settings', data=None),
    dcc.Store(id='building_information', data=None),
    dcc.Store(id='generation_variable_list', data=[]),
    dcc.Store(id='generate_variables_initial_run_eio_filepath', data=None),
    dcc.Store(id='generate_variables_initial_run_rdd_filepath', data=None),
    dcc.Store('schedule_name', data=None),

    # Generation Results
    dcc.Store(id='generation_variables_pickle_filepath', data=None),
    dcc.Store(id='generation_eio_pickle_filepath', data=None),

    # Data Aggregation
    dcc.Store(id='agg_input_variables_pickle_filepath'),
    dcc.Store(id='agg_input_eio_pickle_filepath'),
    dcc.Store(id='upload_variable_pickle_filepath', data=None),
    dcc.Store(id='upload_eio_pickle_filepath', data=None),
    dcc.Store(id='aggregation_simulation_name', data=None),
    dcc.Store(id='aggregation_building_information', data=None),
    dcc.Store(id='aggregation_simulation_information', data=None),
    dcc.Store(id='aggregation_building_id', data=None),
    dcc.Store(id='aggregated_pickle_filepath', data=None),

    # Visualization Data Sources
    dcc.Store(id='visualization_upload_variables_pickle_filepath', data=None),
    dcc.Store(id='visualization_upload_aggregated_pickle_filepath', data=None),
    dcc.Store(id='visualization_variables_pickle_filepath', data=None),
    dcc.Store(id='visualization_aggregated_pickle_filepath', data=None),
    dcc.Store(id='visualization_simulation_id', data=None),

    # Visualization Parameters
    dcc.Store(id='visualization_simulations_df', data=None),
    dcc.Store(id='visualization_time_series_data_name', data=None),
    dcc.Store(id='visualization_time_series_data_list', data=None),

    dbc.Row([
        html.H1(
            "EnergyPlus Simulation Management Tool",
            className = 'text-center text-primary mb-4'
        )
    ]),

    dcc.Tabs(
        id='main_tabs',
        value='tab-postgresql', # Default Tab
        children=[
        # postgreSQL Tab
        dcc.Tab(
            value = 'tab-postgresql',
            label='PostgreSQL',
            className='text-center text-primary mb-4',
            children=PSQL.tab_layout
        ),

        # EP Generation Tab
        dcc.Tab(
            value = 'tab-generation',
            label='EP Generation',
            className = 'text-center text-primary mb-4',
            children=EPGen.tab_layout
        ),

        # EP Aggregation Tab
        dcc.Tab(
            value = 'tab-aggregation',
            label = 'Aggregation',
            className = 'text-center text-primary mb-4',
            children = EPAgg.tab_layout
        ),

        # EP Visualization Tab
        dcc.Tab(
            value = 'tab-visualization',
            label = 'Visualization & Analysis',
            className = 'text-center text-primary mb-4',
            children = EPVis.tab_layout
        )
    ])
], fluid = False)

########## Callbacks ##########

def format_datetime(date_string):
    year, month, day = date_string.split('-')
    day = day.split('T')[0]
    formatted_datetime = datetime(int(year), int(month), int(day))
    return formatted_datetime

def valid_filepath(filepath):
    if filepath is not None:
        if os.path.isfile(filepath):
            return True
    return False

def is_valid_dict(d):
    if d is None:
        return False
    if not isinstance(d, dict):
        return False
    if len(d) == 0:
        return False
    for key, value in d.items():
        if value is None:
            return False
        if isinstance(value, str) and value.strip() == '':
            return False
        if isinstance(value, (list, dict)) and len(value) == 0:
            return False
    return True

def is_valid_string(s):
    return isinstance(s, str) and s.strip() != ''

def is_valid_int(n):
    return isinstance(n, int) and n > 0

def upload_file(filename, content):
    try:
        upload_filepath = os.path.join(UPLOAD_DIRECTORY, filename)
        data = content.encode("utf8").split(b";base64,")[1]
        with open(upload_filepath, "wb") as fp:
            fp.write(base64.decodebytes(data))
        short_name = filename[:20] + "..." if len(filename) > 10 else filename
        return f"Uploaded {short_name}", upload_filepath
    except Exception as e:
        return "Upload Failed", None

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

# Create Database Button
@app.callback(
    Output('PSQL_Button_CreateDatabase', 'children'),
    Input('PSQL_Button_CreateDatabase', 'n_clicks'),
    State('PSQL_Textarea_Username', 'value'),
    State('PSQL_Textarea_Password', 'value'),
    State('PSQL_Textarea_PortNumber', 'value'),
    State('PSQL_Textarea_HostName', 'value'),
    State('PSQL_Textarea_DbName', 'value'),
    prevent_initial_call=True
)
def create_database(n_clicks, username, password, port, host, dbname):
    db_settings = {
        "dbname": dbname,
        "user": username,
        "password": password,
        "host": host,
        "port": port
    }
    if get_callback_id() == 'PSQL_Button_CreateDatabase': return PSQL.create_database(db_settings)
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
    Output('db_settings', 'data'),
    Input('PSQL_Dropdown_ExistDbList', 'value'),
    prevent_initial_call=True
)
def select_database(dbname):
    db_settings = PSQL.get_db_settings(dbname)
    return db_settings

########## Data Generation ##########

# Data Source Selection
@app.callback(
    Output('building_details', 'hidden'),
    Output('upload_files', 'hidden'),
    Output('generation_simulation_name', 'value'),
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
def upload_epw(filename, content):
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
    elif get_callback_id() == 'pnnl_prototype_weather_filepath' and valid_filepath(pnnl_prototype_epw_filepath):
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
            return CUSTOM_BUILDING_INFORMATION
    else: return {}

# Callback triggered by change in IDF and EPW filepath.
@app.callback(
    Output('simulation_details', 'hidden'),
    Input('generation_idf_filepath', 'data'),
    Input('generation_epw_filepath', 'data'),
    prevent_initial_call=True
)
def unhide_simulation_details(idf_filepath, epw_filepath):
    if valid_filepath(idf_filepath) and valid_filepath(epw_filepath): return False
    else: return True

# Simulation Details
@app.callback(
    Output('gen_simulation_settings', 'data'),
    Input('generation_simulation_name', 'value'),
    Input('sim_TimeStep', 'value'),
    Input('sim_run_period', 'start_date'),
    Input('sim_run_period', 'end_date'),
    Input('simReportFreq_selection', 'value'),
    Input('generation_epw_filepath', 'data'),
    prevent_initial_call=True
)
def update_simulation_details(simulation_name, timestep, start_date, end_date, report_freq_selection, epw_filepath):
    try:
        epw_location = EPGen.get_location_from_epw(epw_filepath)
    except Exception as e:
        epw_location = 'Unknown'
    simulation_settings = {
        'name': simulation_name,
        'timestep_minutes': timestep,
        'start_datetime': start_date, # Only a string, not a datetime, can be stored in dcc.Store
        'end_datetime': end_date,
        'reporting_frequency': report_freq_selection,
        'epw_location': epw_location,
    }
    return simulation_settings

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
    State('generation_idf_filepath', 'data'),
    State('generation_epw_filepath', 'data'),
    prevent_initial_call=True
)
def generate_variables(n_clicks, idf_filepath, epw_filepath):
    try:
        eio_filepath, rdd_filepath, variables_list = EPGen.generate_variables(idf_filepath, epw_filepath)
        return 'Variables Generated', variables_list, eio_filepath, rdd_filepath
    except Exception as e:
        return 'Failed to Generate', [], None, None

# Variable Selection
@app.callback(
    Output('generation_variable_list', 'data'),
    Input('preselected_variable_selection', 'value'),
    Input('custom_variable_selection', 'value'),
    Input('EPGen_Radiobutton_VariableSelection', 'value'), # 1: All Preselected Variables 2: Select Variables
    prevent_initial_call=False
)
def variable_selection(preselected_variable_selection, custom_variable_selection, choice):
    if choice == 1:
        return PRESELECTED_VARIABLES
    elif choice == 2:
        return preselected_variable_selection + custom_variable_selection

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
    Output('generation_variables_pickle_filepath', 'data'),
    Output('generation_eio_pickle_filepath', 'data'),
    Input('EPGen_Button_GenerateData', 'n_clicks'),
    State('generation_idf_filepath', 'data'),
    State('generation_epw_filepath', 'data'),
    State('gen_simulation_settings', 'data'),
    State('generation_variable_list', 'data'),
    prevent_initial_call = True
)
def generate_data(n_clicks, idf_filepath, epw_filepath, simulation_settings, variable_names):
    try:
        simulation_settings['start_datetime'] = format_datetime(simulation_settings['start_datetime'])
        simulation_settings['end_datetime'] = format_datetime(simulation_settings['end_datetime'])
        variables_pickle_filepath, eio_pickle_filepath = EPGen.generate_data(idf_filepath, epw_filepath, simulation_settings, variable_names, RESULTS_FOLDERPATH)
        return 'Data Generated', variables_pickle_filepath, eio_pickle_filepath
    except Exception as e:
        return "Generation Failed", no_update

# Unhide Download Buttons
@app.callback(
    Output('download_variables_pickle_button', 'hidden'),
    Output('download_eio_pickle_button', 'hidden'),
    Output('upload_to_db_button', 'hidden'),
    Input('generation_variables_pickle_filepath', 'data'),
    Input('generation_eio_pickle_filepath', 'data'),
    prevent_initial_call = True
)
def unhide_download_buttons(variables_pickle_filepath, eio_pickle_filepath):
    if variables_pickle_filepath is not None and eio_pickle_filepath is not None:
        return False, False, False
    else: return True, True, True

# Download Variables Pickle
@app.callback(
    Output('download_variables_pickle_button', 'children'),
    Output('download_variables_pickle', 'data'),
    Input('download_variables_pickle_button', 'n_clicks'),
    State('generation_variables_pickle_filepath', 'data'),
    prevent_initial_call = True
)
def download_variables_pickle(n_clicks, variables_pickle_filepath):
    return 'Downloaded Variables Pickle', dcc.send_file(variables_pickle_filepath)

# Download Eio Pickle
@app.callback(
    Output('download_eio_pickle_button', 'children'),
    Output('download_eio_pickle', 'data'),
    Input('download_eio_pickle_button', 'n_clicks'),
    State('generation_eio_pickle_filepath', 'data'),
    prevent_initial_call = True
)
def download_eio_pickle(n_clicks, eio_pickle_filepath):
    return 'Downloaded Eio Pickle', dcc.send_file(eio_pickle_filepath)

# Upload to DB Button
@app.callback(
    Output('upload_to_db_button', 'children'),
    Output('generation_zones_df', 'data'),
    Output('generation_building_id', 'data'),
    Input('upload_to_db_button', 'n_clicks'),
    State('db_settings', 'data'),
    State('generation_simulation_name', 'value'),
    State('gen_simulation_settings', 'data'),
    State('generation_variable_list', 'data'),
    State('building_information', 'data'),
    State('generation_variables_pickle_filepath', 'data'),
    State('generation_eio_pickle_filepath', 'data'),
    prevent_initial_call = True
)
def upload_to_db(n_clicks, db_settings, simulation_name, simulation_settings, variable_list, building_information, variable_pickle_filepath, eio_pickle_filepath):
    try:
        simulation_settings['start_datetime'] = format_datetime(simulation_settings['start_datetime'])
        simulation_settings['end_datetime'] = format_datetime(simulation_settings['end_datetime'])
        building_id, zones_df = EPGen.upload_to_db(simulation_name, simulation_settings, variable_list, building_information, db_settings, variable_pickle_filepath, eio_pickle_filepath)
        return 'Uploaded to Database', zones_df.to_dict('records'), building_id
    except Exception as e:
        return "Upload Failed", None, None


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

    try:
        upload_filepath = os.path.join(UPLOAD_DIRECTORY, filename)
        data = contents.encode("utf8").split(b";base64,")[1]
        with open(upload_filepath, "wb") as fp:
            fp.write(base64.decodebytes(data))
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

    try:
        upload_filepath = os.path.join(UPLOAD_DIRECTORY, filename)
        data = contents.encode("utf8").split(b";base64,")[1]
        with open(upload_filepath, "wb") as fp:
            fp.write(base64.decodebytes(data))
        short_name = filename[:20] + "..." if len(filename) > 10 else filename
        return f"Uploaded {short_name}", upload_filepath
    except Exception as e:
        return "Upload Failed", None

# Set Inputs Filepaths for Aggregation
@app.callback(
    Output('agg_input_variables_pickle_filepath', 'data'),
    Output('agg_input_eio_pickle_filepath', 'data'),
    Input('generation_variables_pickle_filepath', 'data'),
    Input('generation_eio_pickle_filepath', 'data'),
    Input('upload_variable_pickle_filepath', 'data'),
    Input('upload_eio_pickle_filepath', 'data'),
    State('agg_input_selection', 'value'),
    prevent_initial_call = True
)
def agg_set_input_filepaths(generation_variables_pickle_filepath, generation_eio_pickle_filepath, upload_variables, upload_eio, input_selection):
    if input_selection == 1 and valid_filepath(generation_variables_pickle_filepath) and valid_filepath(generation_eio_pickle_filepath):
        return generation_variables_pickle_filepath, generation_eio_pickle_filepath
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
    Output('aggregated_pickle_filepath', 'data'),
    Input('aggregate_data_button', 'n_clicks'),
    State('aggregation_settings', 'data'),
    State('agg_input_variables_pickle_filepath', 'data'),
    State('agg_input_eio_pickle_filepath', 'data'),
    prevent_initial_call = True
)
def aggregate_data(n_clicks, aggregation_settings, variables_pickle_filepath, eio_pickle_filepath):
    try:
        aggregated_pickle_filepath = EPAgg.aggregate_data(aggregation_settings, variables_pickle_filepath, eio_pickle_filepath)
        return 'Data Aggregated', aggregated_pickle_filepath
    except Exception as e:
        return 'Aggregation Failed', no_update

@app.callback(
    Output('agg_download_button', 'hidden'),
    Input('aggregated_pickle_filepath', 'data'),
    prevent_initial_call = True
)
def unhide_download_buttons(aggregation_pickle_filepath):
    if valid_filepath(aggregation_pickle_filepath): return False
    else: return True

@app.callback(
    Output('agg_download_button', 'children'),
    Output('agg_download_files', 'data'),
    Input('agg_download_button', 'n_clicks'),
    State('aggregated_pickle_filepath', 'data'),
    prevent_initial_call = True
)
def agg_download_pickle(n_clicks, aggregation_pickle_filepath):
    if valid_filepath(aggregation_pickle_filepath):
        return 'Pickle File Downloaded', dcc.send_file(aggregation_pickle_filepath)
    else: return 'Download Failed', no_update

@app.callback(
    Output('aggregation_simulation_name', 'data'),
    Input('main_tabs', 'value'),
    Input('agg_input_selection', 'value'),
    State('generation_simulation_name', 'value'),
    prevent_initial_call = True
)
def get_aggregation_simulation_name(selected_tab, agg_input_selection, generation_simulation_name):
    if selected_tab == 'tab-aggregation' and agg_input_selection == 1: return generation_simulation_name
    elif selected_tab == 'tab-aggregation' and agg_input_selection == 2: return 'Unnamed Simulation'
    else: return no_update

@app.callback(
    Output('aggregation_building_information', 'data'),
    Input('agg_input_selection', 'value'),
    Input('building_information', 'data'),
    prevent_initial_call = True
)
def get_aggregation_building_information(agg_input_selection, building_information):
    if agg_input_selection == 1: return building_information
    else: return CUSTOM_BUILDING_INFORMATION

@app.callback(
    Output('aggregation_simulation_information', 'data'),
    Input('agg_input_selection', 'value'),
    Input('agg_input_variables_pickle_filepath', 'data'),
    State('gen_simulation_settings', 'data'),
    prevent_initial_call=True
)
def get_aggregation_simulation_settings(agg_input_selection, variables_pickle_filepath, simulation_information):
    if agg_input_selection == 1: return simulation_information
    elif valid_filepath(variables_pickle_filepath):
        try:
            with open(variables_pickle_filepath, 'rb') as f: data_dict = pickle.load(f)
            start_datetime, end_datetime, time_resolution = EPAgg.get_time_res(data_dict)
            custom_simulation_settings = {
                "start_datetime": start_datetime,
                "end_datetime": end_datetime,
                "reporting_frequency": 'timestep',
                "timestep_minutes": time_resolution,
            }
            return custom_simulation_settings
        except Exception as e: return {}
    else: return None

@app.callback(
    Output('aggregation_building_id', 'data'),
    Input('main_tabs', 'value'),
    Input('agg_input_selection', 'value'),
    State('db_settings', 'data'),
    State('generation_building_id', 'data'),
    State('generation_idf_filepath', 'data'),
    State('building_information', 'data'),
    prevent_initial_call=True
)
def get_aggregation_building_id(tab_selection, agg_input_selection, db_settings, generation_building_id, generation_idf_filepath, building_information):

    if tab_selection != 'tab-aggregation': return no_update

    if agg_input_selection == 1:
        if generation_building_id is not None: return generation_building_id
        else:
            building_type = building_information['building_type']
            if building_type == 'Custom':
                conn = PSQL.connect(db_settings)
                building_id = EPAgg.upload_custom_building(conn)
                conn.close()
                return building_id
            else:
                building_name = os.path.basename(generation_idf_filepath).replace('.idf', '')
                conn = PSQL.connect(db_settings)
                building_id = EPAgg.get_building_id_old(conn, building_type, building_name)
                conn.close()
                return building_id
    elif agg_input_selection == 2:
        conn = PSQL.connect(db_settings)
        building_id = EPAgg.upload_custom_building(conn)
        conn.close()
        return building_id
    else: return None

@app.callback(
    Output('agg_upload_to_db_button', 'hidden'),
    Input('aggregation_simulation_name', 'data'),
    Input('aggregation_building_information', 'data'),
    Input('aggregation_simulation_information', 'data'),
    Input('aggregation_building_id','data'),
    Input('aggregated_pickle_filepath', 'data'),
    prevent_initial_call = True)
def unhide_upload_to_db_button(simulation_name, building_information, simulation_settings, building_id, pickle_filepath):
    if is_valid_string(simulation_name) and is_valid_dict(building_information) and is_valid_dict(simulation_settings) and is_valid_int(building_id) and valid_filepath(pickle_filepath): return False
    else: return True


# Upload to DB Button
@app.callback(
    Output('agg_upload_to_db_button', 'children'),
    Input('agg_upload_to_db_button', 'n_clicks'),
    State('db_settings', 'data'),
    State('aggregation_simulation_name', 'data'),
    State('aggregated_pickle_filepath', 'data'),
    State('aggregation_building_information', 'data'),
    State('aggregation_simulation_information', 'data'),
    State('aggregation_settings', 'data'),
    State('aggregation_building_id', 'data'),
    State('agg_input_variables_pickle_filepath', 'data'),
    State('agg_input_eio_pickle_filepath', 'data'),
    prevent_initial_call = True
)
def upload_to_db(n_clicks, db_settings, sim_name, aggregation_pickle_filepath, building_information, simulation_settings, aggregation_settings, building_id, variables_pickle_filepath, eio_pickle_filepath):
    try:
        simulation_settings['start_datetime'] = format_datetime(simulation_settings['start_datetime'])
        simulation_settings['end_datetime'] = format_datetime(simulation_settings['end_datetime'])
        zones_df = EPAgg.upload_to_db(db_settings, sim_name, aggregation_pickle_filepath, building_information, simulation_settings, aggregation_settings, building_id, variables_pickle_filepath, eio_pickle_filepath)
        return 'Uploaded to Database'
    except Exception as e:
        return 'Upload Failed'

##########################################################################################################

#################### Visualization #######################################################################

##########################################################################################################

@app.callback(
    Output('visualization_upload_data_menu', 'hidden'),
    Input('main_tabs', 'value'),
    Input('visualization_data_source', 'value'),
    prevent_initial_call = True
)
def unhide_visualization_upload_data_menu(tab, visualization_data_source):
    if tab == 'tab-visualization' and visualization_data_source == 2: return False
    else: return True

@app.callback(
    Output('visualization_select_from_database_menu', 'hidden'),
    Input('main_tabs', 'value'),
    Input('visualization_data_source', 'value'),
    prevent_initial_call = True
)
def unhide_visualization_select_from_database_menu(tab, visualization_data_source):
    if tab == 'tab-visualization' and visualization_data_source == 3: return False
    else: return True

@app.callback(
    Output('visualization_upload_generated_data_box', 'children'),
    Output('visualization_upload_variables_pickle_filepath', 'data'),
    Input('visualization_upload_generated_data_box', 'filename'),
    Input('visualization_upload_generated_data_box', 'contents'),
    prevent_initial_call=True
)
def upload_variables_pickle(filename, content):
    return upload_file(filename, content)

@app.callback(
    Output('visualization_upload_aggregated_data_box', 'children'),
    Output('visualization_upload_aggregated_pickle_filepath', 'data'),
    Input('visualization_upload_aggregated_data_box', 'filename'),
    Input('visualization_upload_aggregated_data_box', 'contents'),
    prevent_initial_call=True
)
def upload_aggregated_pickle(filename, content):
    return upload_file(filename, content)

@app.callback(
    Output('visualization_database_simulation_dropdown', 'options'),
    Output('visualization_simulations_df', 'data'),
    Input('main_tabs', 'value'),
    Input('PSQL_RadioButton_UsingDatabase', 'value'),
    State('db_settings', 'data'),
    prevent_initial_call = True
)
def populate_db_settings(main_tabs, using_db, db_settings):
    if main_tabs == 'tab-visualization' and using_db == True:
        simulations_df = PSQL.get_simulations(db_settings)
        return simulations_df['simulation_name'].tolist(), simulations_df.to_dict('records')
    else: return []

@app.callback(
    Output('visualization_simulation_id', 'data'),
    Input('visualization_database_simulation_dropdown', 'value'),
    Input('visualization_simulations_df', 'data'),
    prevent_initial_call = True
)
def get_simulation_id(simulation_name, simulations_df):
    if simulations_df and simulation_name:
        simulations_df = pd.DataFrame.from_dict(simulations_df)
        simulation_id = simulations_df.loc[simulations_df['simulation_name'] == simulation_name, 'id'].iloc[0]
        return simulation_id
    else: return None

@app.callback(
    Output('visualization_generated_or_aggregated_data_selection_menu', 'hidden'),
    Input('main_tabs', 'value'),
    Input('visualization_data_source', 'value'),
    prevent_initial_call = True
)
def unhide_generated_or_aggregated_data_selection(main_tabs, visualization_data_source):
    if main_tabs == 'tab-visualization' and visualization_data_source != 3: return False
    else: return True

@app.callback(
    Output('visualization_date_picker', 'hidden'),
    Input('main_tabs', 'value'),
    prevent_initial_call = True
)
def unhide_date_picker(tab):
    if tab == "tab-visualization": return False
    else: return True

@app.callback(
    Output('visualization_variables_pickle_filepath', 'data'),
    Output('visualization_aggregated_pickle_filepath', 'data'),
    Input('main_tabs', 'value'),
    Input('visualization_data_source', 'value'),
    Input('visualization_generated_or_aggregated_data_selection', 'value'),
    Input('visualization_upload_variables_pickle_filepath', 'data'),
    Input('visualization_upload_aggregated_pickle_filepath', 'data'),
    State('generation_variables_pickle_filepath', 'data'),
    State('aggregated_pickle_filepath', 'data'),
    prevent_initial_call = True
)
def set_visualization_pickle_filepaths(tab, data_source, generated_or_aggregated, upload_variables_pickle, upload_aggregated_pickle, generation_variables_pickle, aggregation_pickle):

    if tab != 'tab-visualization': return None, None
    if data_source == 3: return None, None

    if data_source == 1:
        if generated_or_aggregated == 1: return generation_variables_pickle, None
        elif generated_or_aggregated == 2: return None, aggregation_pickle
        else: return generation_variables_pickle, aggregation_pickle
    elif data_source == 2:
        if generated_or_aggregated == 1: return upload_variables_pickle, None
        elif generated_or_aggregated == 2: return None, upload_aggregated_pickle
        else: return upload_variables_pickle, upload_aggregated_pickle

@app.callback(
    Output('visualization_date_picker_calendar', 'min_date_allowed'),
    Output('visualization_date_picker_calendar', 'max_date_allowed'),
    Output('visualization_date_picker_calendar', 'start_date'),
    Output('visualization_date_picker_calendar', 'end_date'),
    Input('main_tabs', 'value'),
    Input('visualization_variables_pickle_filepath', 'data'),
    Input('visualization_aggregated_pickle_filepath', 'data'),
    Input('visualization_simulation_id', 'data'),
    State('db_settings', 'data'),
    prevent_initial_call = True
)
def populate_min_max_date_allowed(tab, generated_pickle, aggregated_pickle, simulation_id, db_settings):

    if tab != 'tab-visualization': return None, None, None, None

    if generated_pickle:
        with open(generated_pickle, 'rb') as f: generated_data = pickle.load(f)
        generated_data_min_datetime = generated_data['DateTime_List'][0]
        generated_data_max_datetime = generated_data['DateTime_List'][-1]

    if aggregated_pickle:
        with open(aggregated_pickle, 'rb') as f: aggregated_data = pickle.load(f)
        aggregated_data_min_datetime = aggregated_data['DateTime_List'][0]
        aggregated_data_max_datetime = aggregated_data['DateTime_List'][-1]

    if generated_pickle and aggregated_pickle:
        min_datetime = max(generated_data_min_datetime, aggregated_data_min_datetime)
        max_datetime = min(generated_data_max_datetime, aggregated_data_max_datetime)
        if min_datetime > max_datetime: return None, None, None, None # Error
    elif generated_pickle:
        min_datetime = generated_data_min_datetime
        max_datetime = generated_data_max_datetime
    elif aggregated_pickle:
        min_datetime = aggregated_data_min_datetime
        max_datetime = aggregated_data_max_datetime
    else: # Using Database
        min_datetime, start_datetime_id, max_datetime, end_datetime_id = PSQL.get_simulation_start_end_datetimes(db_settings, simulation_id)

    return (
        min_datetime.date().isoformat(),
        max_datetime.date().isoformat(),
        min_datetime.date().isoformat(),
        max_datetime.date().isoformat()
    )

@app.callback(
    Output('visualization_aggregated_data_zone_selection_menu', 'hidden'),
    Input('visualization_data_source', 'value'),
    Input('visualization_generated_or_aggregated_data_selection', 'value'),
    Input('visualization_aggregated_pickle_filepath', 'data'),
    prevent_initial_call = True
)
def unhide_visualization_select_variable(data_source, generated_or_aggregated, aggregated_pickle):
    if ((generated_or_aggregated == 2 or generated_or_aggregated == 3) and valid_filepath(aggregated_pickle)) or data_source == 3: return False
    else: return True

@app.callback(
    Output('visualization_generation_zones_dropdown', 'options'),
    Output('visualization_aggregated_zones_dropdown', 'options'),
    Input('visualization_data_source', 'value'),
    Input('visualization_generated_or_aggregated_data_selection', 'value'),
    Input('visualization_variables_pickle_filepath', 'data'),
    Input('visualization_aggregated_pickle_filepath', 'data'),
    Input('visualization_simulation_id', 'data'),
    State('db_settings', 'data'),
    prevent_initial_call = True
)
def populate_zones_dropdowns(data_source, generated_or_aggregated, generated_pickle, aggregated_pickle, simulation_id, db_settings):

    generation_zones = []
    aggregation_zones = []

    if aggregated_pickle:
        with open(aggregated_pickle, 'rb') as f: aggregated_data = pickle.load(f)
        aggregation_zones = list(aggregated_data.keys())
        aggregation_zones.remove('DateTime_List')
        return [], aggregation_zones

    if data_source == 3:
        generation_zones_df, aggregation_zones_df = PSQL.get_generation_aggregation_zones(db_settings, simulation_id)
        return generation_zones_df['zone_name'].tolist(), aggregation_zones_df['zone_name'].tolist()

@app.callback(
Output('visualization_generation_zones_dropdown', 'value'),
    Output('visualization_aggregated_zones_dropdown', 'value'),
    Input('visualization_generation_zones_dropdown', 'value'),
    Input('visualization_aggregated_zones_dropdown', 'value'),
    prevent_initial_call = True
)
def handle_exclusive_dropdowns(generation_zone_selection, aggregation_zone_selection):
    if get_callback_id() == 'visualization_generation_zones_dropdown':
        return no_update, ''
    elif get_callback_id() == 'visualization_aggregated_zones_dropdown':
        return '', no_update
    else: return no_update, no_update

# Unhide Variable Selection for Aggregated Data
@app.callback(
    Output('visualization_generated_data_variable_selection_menu', 'hidden'),
    Input('visualization_generated_or_aggregated_data_selection', 'value'),
    Input('visualization_variables_pickle_filepath', 'data'),
    prevent_initial_call = True
)
def unhide_generated_data_variable_selection_menu(generated_or_aggregated, generated_pickle):
    if (generated_or_aggregated == 1 or generated_or_aggregated == 3) and valid_filepath(generated_pickle): return False
    else: return True

@app.callback(
    Output('visualization_aggregated_data_variable_dropdown', 'options'),
    Input('visualization_generation_zones_dropdown', 'value'),
    Input('visualization_aggregated_zones_dropdown', 'value'),
    State('db_settings', 'data'),
    prevent_initial_call = True
)
def populate_variables_dropdowns(generation_zone_selection, aggregation_zone_selection, db_settings):
    if generation_zone_selection: zone_selection = generation_zone_selection
    elif aggregation_zone_selection: zone_selection = aggregation_zone_selection
    else: zone_selection = None

    if zone_selection:
        variables = PSQL.get_variables(db_settings, zone_selection)
        return variables
    else: return []

@app.callback(
    Output('visualization_generated_data_variable_dropdown', 'options'),
    Input('visualization_variables_pickle_filepath', 'data'),
    prevent_initial_call=True
)
def populate_generated_data_variable_dropdowns(generated_pickle):
    if valid_filepath(generated_pickle):
        with open(generated_pickle, 'rb') as f: generated_data = pickle.load(f)
        generated_data_variables = list(generated_data.keys())
        return generated_data_variables
    else: return []

@app.callback(
    Output('visualization_generated_data_variable_column_dropdown', 'options'),
    Input('visualization_generated_data_variable_dropdown', 'value'),
    State('visualization_variables_pickle_filepath', 'data')
)
def populate_generated_data_variable_column_dropdowns(variable_selection, generated_pickle):
    if valid_filepath(generated_pickle):
        with open(generated_pickle, 'rb') as f: generated_data = pickle.load(f)
        variable_columns = generated_data[variable_selection].columns.tolist()
        return variable_columns
    else: return []

@app.callback(
    Output('visualization_time_series_data_name', 'data'),
    Output('visualization_time_series_data_list', 'data'),
    Input('visualization_generated_data_variable_dropdown', 'value'),
    Input('visualization_generated_data_variable_column_dropdown', 'value'),
    Input('visualization_generated_data_custom_label_input', 'n_blur'),
    State('visualization_variables_pickle_filepath', 'data'),
    State('visualization_generated_data_custom_label_input', 'value'),
    prevent_initial_call = True
)
def generated_data_get_time_series_data(variable, column, n_blur, pickle_filepath, custom_label):
    if variable and column and valid_filepath(pickle_filepath):
        with open(pickle_filepath, 'rb') as f: data = pickle.load(f)
        data_list = data[variable][column].tolist()
        data_name = custom_label
        return data_name, data_list
    else: return None, None

"""

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
    



