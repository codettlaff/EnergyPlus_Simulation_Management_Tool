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

import numpy as np
import pandas as pd
from dash import Dash, dcc, html, Input, Output, State, dash_table
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

# Directory Paths
UPLOAD_DIRECTORY = os.path.join(os.path.dirname(__file__), "Uploads")
DATA_FOLDERPATH = os.path.join(os.path.dirname(__file__), '..', '..', 'Data')
RESULTS_FOLDERPATH = os.path.join(os.path.dirname(__file__), '..', '..', 'Results')
SPECIAL_IDF_FILEPATH = os.path.join(DATA_FOLDERPATH, 'Special.idf')

if os.path.exists(UPLOAD_DIRECTORY): shutil.rmtree(UPLOAD_DIRECTORY)
os.mkdir(UPLOAD_DIRECTORY)

########## System Variables ##########

DATA_IDF_FILEPATH = None
DATA_EPW_FILEPATH = None
PRESELECTED_VARIABLES = EPGen.preselected_variables()

SIMULATION_SETTINGS = None
example_simulation_settings = {
    "name": "new_simulation",
    "idf_year": 2013,
    "start_datetime": datetime(2013, 1, 1),
    "end_datetime": datetime(2014, 1, 1),
    "reporting_frequency": "timestep",
    "timestep_minutes": 5,
    "variables": []
}
BUILDING_INFORMATION = None
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

RESULTS_VARIABLES_PICKLE_FILEPATH = None
RESULTS_EIO_PICKLE_FILEPATH = None

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

########## PostgreSQL ##########

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
    prevent_initial_call=True
)
def create_database(n_clicks):
    return PSQL.create_database(DB_SETTINGS)

########## Data Generation ##########

# Update Simulation Name
@app.callback(
    Input('simulation_name', 'value')
)
def update_simulation_name(simulation_name):
    global SIMULATION_SETTINGS
    SIMULATION_SETTINGS = example_simulation_settings
    SIMULATION_SETTINGS['name'] = simulation_name

# Data Source Selection
@app.callback(
    Output('building_details', 'hidden'),
    Output('upload_files', 'hidden'),
    Input('data_source_selection', 'value')
)
def data_source_selection(selection):
    if selection == 1: return False, True
    elif selection == 2: return True, False
    else: return True, True

'''

# Update Simulation Name
@app.callback(
    Input(component_id = 'folder_name', component_property = 'value')
)
def update_simulation_name(simulation_name):
    global SIMULATION_FOLDERNAME
    SIMULATION_FOLDERNAME = simulation_name

@app.callback(
    Output(component_id = 'building_details', component_property = 'hidden'),
    Output(component_id = 'upload_files', component_property = 'hidden'),
    Output(component_id = 'simulation_details', component_property = 'hidden', allow_duplicate = True),
    Output(component_id = 'schedules', component_property = 'hidden', allow_duplicate = True),
    Output(component_id = 'generate_variables', component_property = 'hidden', allow_duplicate = True),
    Output(component_id = 'download_variables', component_property = 'hidden', allow_duplicate = True),
    Output(component_id = 'final_download', component_property = 'hidden', allow_duplicate = True),
    State(component_id = 'folder_name', component_property = 'value'),
    Input(component_id = 'database_selection', component_property = 'value'),
    prevent_initial_call = True)
def EPGen_Radiobutton_DatabaseSelection_Interaction(folder_name, database_selection):
    building_details, upload_files, simulation_details , schedules, generate_variables, download_variables, final_download = EPGen.EPGen_Radiobutton_DatabaseSelection_Interaction_Function(folder_name, database_selection)
    return building_details, upload_files, simulation_details , schedules, generate_variables, download_variables, final_download

@app.callback(
    Output(component_id = 'upload_idf', component_property = 'children'),
    Input(component_id = 'upload_idf', component_property = 'filename'),
    State(component_id = 'upload_idf', component_property = 'contents'),
    prevent_initial_call = False)
def EPGen_Upload_IDF_Interaction(filename, content):
    message = EPGen.EPGen_Upload_IDF_Interaction_Function(filename, content)
    return message

@app.callback(
    Output(component_id = 'upload_epw', component_property = 'children'),
    Input(component_id = 'upload_epw', component_property = 'filename'),
    State(component_id = 'upload_epw', component_property = 'contents'),
    prevent_initial_call = False)
def EPGen_Upload_EPW_Interaction(filename, content):
    message = EPGen.EPGen_Upload_EPW_Interaction_Function(filename, content)
    return message

@app.callback(
    Output(component_id = 'simulation_details', component_property = 'hidden', allow_duplicate = True),
    Input(component_id = 'version_selection', component_property = 'value'),
    prevent_initial_call = True)
def EPGen_Dropdown_EPVersion_Interaction(version_selection):
    simulation_details = EPGen.EPGen_Dropdown_EPVersion_Interaction_Function(version_selection)
    return simulation_details

@app.callback(
    Output(component_id = 'simulation_details', component_property = 'hidden', allow_duplicate = True),
    Input(component_id = 'location_selection', component_property = 'value'),
    prevent_initial_call = True)
def EPGen_Dropdown_Location_Interaction(location_selection):
    simulation_details = EPGen.EPGen_Dropdown_Location_Interaction_Function(location_selection)
    return simulation_details

@app.callback(
    Output(component_id = 'generate_variables', component_property = 'hidden', allow_duplicate = True),
    Input(component_id = 'simReportFreq_selection', component_property = 'value'),
    prevent_initial_call = True)
def EPGen_Dropdown_SimReportFreq_Interaction(simReportFreq_selection):
    generate_variables = EPGen.EPGen_Dropdown_SimReportFreq_Interaction_Function(simReportFreq_selection)
    return generate_variables

# Variable selection radio button interaction
@app.callback(
    Output(component_id = 'schedules', component_property = 'hidden', allow_duplicate = True),
    Output(component_id = 'people_schedules', component_property = 'options'),
    Output(component_id = 'equip_schedules', component_property = 'options'),
    Output(component_id = 'light_schedules', component_property = 'options'),
    Output(component_id = 'heating_schedules', component_property = 'options'),
    Output(component_id = 'cooling_schedules', component_property = 'options'),
    Output(component_id = 'temperature_schedules', component_property = 'options'),
    Input(component_id = 'EPGen_Radiobutton_EditSchedules', component_property = 'value'),
    prevent_initial_call = True)
def EPGen_RadioButton_EditSchedule_Interaction(EPGen_Radiobutton_VariableSelection):
    schedules, People_Schedules, Equip_Schedules, Light_Schedules, HeatingSetpoint_Schedules, CoolingSetpoint_Schedules, TemperatureSetpoint_Schedules = EPGen.EPGen_RadioButton_EditSchedule_Interaction_Function(EPGen_Radiobutton_VariableSelection)
    return schedules, People_Schedules, Equip_Schedules, Light_Schedules, HeatingSetpoint_Schedules, CoolingSetpoint_Schedules, TemperatureSetpoint_Schedules

@app.callback(
    Output(component_id = 'final_download', component_property = 'hidden', allow_duplicate = True),
    Input(component_id = 'download_selection', component_property = 'value'),
    prevent_initial_call = True)
def EPGen_Dropdown_DownloadSelection_Interaction(download_selection):
    final_download = EPGen.EPGen_Dropdown_DownloadSelection_Interaction_Function(download_selection)
    return final_download

# Level 1 list
@app.callback(
    Output(component_id = 'level_1', component_property = 'options'),
    Output(component_id = 'level_2', component_property = 'options', allow_duplicate = True),
    Output(component_id = 'level_3', component_property = 'options', allow_duplicate = True),
    Output(component_id = 'location_selection', component_property = 'options'),
    Output(component_id = 'level_1', component_property = 'value'),
    Output(component_id = 'level_2', component_property = 'value', allow_duplicate = True),
    Output(component_id = 'level_3', component_property = 'value', allow_duplicate = True),
    Output(component_id = 'location_selection', component_property = 'value'),
    Input(component_id = 'buildingType_selection', component_property = 'value'),
    prevent_initial_call = True)
def EPGen_Dropdown_BuildingType_Interaction(buildingType_selection):
    level_1_list, level_2_list, level_3_list, Weather_list, level_1_value, level_2_value, level_3_value, Weather_value = EPGen.EPGen_Dropdown_BuildingType_Interaction_Function(buildingType_selection)
    return level_1_list, level_2_list, level_3_list, Weather_list, level_1_value, level_2_value, level_3_value, Weather_value

# Level 2 list
@app.callback(
    Output(component_id = 'level_2', component_property = 'options', allow_duplicate = True),
    Output(component_id = 'level_3', component_property = 'options', allow_duplicate = True),
    Output(component_id = 'level_2', component_property = 'value', allow_duplicate = True),
    Output(component_id = 'level_3', component_property = 'value', allow_duplicate = True),
    State(component_id = 'buildingType_selection', component_property = 'value'),
    Input(component_id = 'level_1', component_property = 'value'),
    prevent_initial_call = True)
def EPGen_Dropdown_SubLevel1_Interaction(buildingType_selection, level_1):
    level_2_list, level_3_list, level_2_value, level_3_value = EPGen.EPGen_Dropdown_SubLevel1_Interaction_Function(buildingType_selection, level_1)
    return level_2_list, level_3_list, level_2_value, level_3_value

# Level 3 list
@app.callback(
    Output(component_id = 'level_3', component_property = 'options', allow_duplicate = True),
    Output(component_id = 'level_3', component_property = 'value', allow_duplicate = True),
    State(component_id = 'buildingType_selection', component_property = 'value'),
    State(component_id = 'level_1', component_property = 'value'),
    Input(component_id = 'level_2', component_property = 'value'),
    prevent_initial_call = True)
def EPGen_Dropdown_SubLevel2_Interaction(buildingType_selection, level_1, level_2):
    level_3_list, level_3_value = EPGen.EPGen_Dropdown_SubLevel2_Interaction_Function(buildingType_selection, level_1, level_2)
    return level_3_list, level_3_value

# Update IDF and Weather File Selection
@ app.callback(
    Input('buildingType_selection', 'value'),
    Input('level_1', 'value'),
    Input('level_2', 'value'),
    Input('level_3', 'value'),
    Input('location_selection', 'value'),
    prevent_initial_call=True
)
def Update_IDF_Weather_Files(buildingType, level1, level2, level3, location):
    global DATA_IDF_FILEPATH
    global DATA_WEATHER_FILEPATH
    global BUILDING_TYPE

    BUILDING_TYPE = buildingType

    idf_filepath, weather_filepath = EPGen.Update_IDF_Weather_Files(buildingType, level1, level2, level3, location)
    if idf_filepath is not None: DATA_IDF_FILEPATH = idf_filepath
    if weather_filepath is not None: DATA_WEATHER_FILEPATH = weather_filepath

# Generate Variable List Button (Initial Run)
@app.callback(
    Output(component_id = 'your_variable_selection', component_property = 'options'),
    Output(component_id = 'our_variable_selection', component_property = 'options'),
    State(component_id = 'database_selection', component_property = 'value'),
    State(component_id = 'buildingType_selection', component_property = 'value'),
    State(component_id = 'level_1', component_property = 'value'),
    State(component_id = 'level_2', component_property = 'value'),
    State(component_id = 'level_3', component_property = 'value'),
    State(component_id = 'location_selection', component_property = 'value'),
    Input(component_id = 'EPGen_Button_GenerateVariables', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPGen_Button_GenerateVariables_Interaction(database_selection, buildingType_selection, level_1, level_2, level_3, location_selection, n_clicks):
    your_variable_selection, our_variable_selection = EPGen.EPGen_Button_GenerateVariables_Interaction_Function(database_selection, buildingType_selection, level_1, level_2, level_3, location_selection, n_clicks)
    return your_variable_selection, our_variable_selection

# User Variable Selection Interaction
@app.callback(
    Input(component_id = 'your_variable_selection', component_property = 'value'),
    Input(component_id = 'our_variable_selection', component_property = 'value'),
    Input('EPGen_Radiobutton_VariableSelection', 'value'), # 1: All Preselected Variables 2: Custom Variable Selection
    prevent_initial_call = True
)
def update_simulation_variables_list(your_variable_selection, our_variable_selection, variable_selection_button):

    global SIMULATION_VARIABLE_LIST
    sim_variable_list = EPGen.update_simulation_variables_list(your_variable_selection, our_variable_selection, variable_selection_button)
    SIMULATION_VARIABLE_LIST = sim_variable_list

# Edit Schedules
@app.callback(
    Output(component_id = 'update_selected_schedule', component_property = 'children', allow_duplicate = True),
    Input(component_id = 'people_schedules', component_property = 'value'),
    Input(component_id = 'equip_schedules', component_property = 'value'),
    Input(component_id = 'light_schedules', component_property = 'value'),
    Input(component_id = 'heating_schedules', component_property = 'value'),
    Input(component_id = 'cooling_schedules', component_property = 'value'),
    Input(component_id = 'temperature_schedules', component_property = 'value'),
    prevent_initial_call = True)
def EPGen_Dropdown_EditSchedule_Interaction(people_schedules, equip_schedules, light_schedules, heating_schedules, cooling_schedules, temperature_schedules):
    update_selected_schedule = EPGen.EPGen_Dropdown_EditSchedule_Interaction_Function(people_schedules, equip_schedules, light_schedules, heating_schedules, cooling_schedules, temperature_schedules)
    return update_selected_schedule

@app.callback(
    Output(component_id = 'update_selected_schedule', component_property = 'children', allow_duplicate = True),
    State(component_id = 'people_schedules', component_property = 'value'),
    State(component_id = 'equip_schedules', component_property = 'value'),
    State(component_id = 'light_schedules', component_property = 'value'),
    State(component_id = 'heating_schedules', component_property = 'value'),
    State(component_id = 'cooling_schedules', component_property = 'value'),
    State(component_id = 'temperature_schedules', component_property = 'value'),
    State(component_id = 'schedule_input', component_property = 'value'),
    Input(component_id = 'update_selected_schedule', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPGen_Button_UpdateSelectedSchedule_Interaction(people_schedules, equip_schedules, light_schedules, heating_schedules, cooling_schedules, temperature_schedules, schedule_input, n_clicks):
    update_selected_schedule = EPGen.EPGen_Button_UpdateSelectedSchedule_Interaction_Function(people_schedules, equip_schedules, light_schedules, heating_schedules, cooling_schedules, temperature_schedules, schedule_input, n_clicks)
    return update_selected_schedule

@app.callback(
    Output(component_id = 'download_variables', component_property = 'hidden', allow_duplicate = True),
    Input(component_id = 'EPGen_Radiobutton_EditSchedules', component_property = 'value'),
    prevent_initial_call = True)
def EPGen_RadioButton_EditSchedules_Interaction_2(EPGen_Radiobutton_VariableSelection):
    download_variables = EPGen.EPGen_RadioButton_EditSchedules_Interaction_2_Function(EPGen_Radiobutton_VariableSelection)
    return download_variables

@app.callback(
    Output(component_id = 'download_variables', component_property = 'hidden', allow_duplicate = True),
    Input(component_id = 'done_updating_schedule', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPGen_Button_DoneUpdatingSchedule_Interaction(n_clicks):
    download_variables = EPGen.EPGen_Button_DoneUpdatingSchedule_Interaction_Function(n_clicks)
    return download_variables

@app.callback(
    Output(component_id = 'final_download', component_property = 'hidden'),
    Input(component_id = 'download_selection', component_property = 'value'),
    prevent_initial_call = True)
def EPGen_Checkbox_DownloadSelection_Interaction(download_selection):
    final_download = EPGen.EPGen_Checkbox_DownloadSelection_Interaction_Function(download_selection)
    return final_download

# Simulation Settings Box
@app.callback(
    Input(component_id = 'sim_run_period', component_property = 'start_date'),
    Input(component_id = 'sim_run_period', component_property = 'end_date'),
    Input(component_id = 'sim_TimeStep', component_property = 'value'),
    Input(component_id = 'simReportFreq_selection', component_property = 'value')
)
def update_simulation_settings(start_date, end_date, sim_TimeStep, simReportFreq_selection):

    global SIMULATION_SETTINGS
    start_date = datetime.fromisoformat(start_date)
    end_date = datetime.fromisoformat(end_date)
    SIMULATION_SETTINGS = {
    "name": SIMULATION_FOLDERNAME,
    "idf_year": start_date.year,
    "start_month": start_date.month,
    "start_day": start_date.day,
    "end_month": end_date.month,
    "end_day": end_date.day,
    "reporting_frequency": simReportFreq_selection,
    "timestep_minutes": sim_TimeStep
    }
    print(SIMULATION_SETTINGS)

# Generate Data Button
@app.callback(
    Output(component_id = 'EPGen_Button_GenerateData', component_property = 'children'),
    State(component_id = 'download_selection', component_property = 'value'),
    State(component_id = 'sim_run_period', component_property = 'start_date'),
    State(component_id = 'sim_run_period', component_property = 'end_date'),
    State(component_id = 'sim_TimeStep', component_property = 'value'),
    State(component_id = 'simReportFreq_selection', component_property = 'value'),
    State(component_id = 'EPGen_Radiobutton_VariableSelection', component_property = 'value'),
    State(component_id = 'your_variable_selection', component_property = 'value'),
    Input(component_id = 'EPGen_Button_GenerateData', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPGen_Button_GenerateData_Interaction(download_selection, start_date, end_date, Sim_TimeStep, Sim_OutputVariable_ReportingFrequency, Var_selection, your_vars, n_clicks):
    global SIMULATION_RESULTS_FOLDERPATH, VARIABLES_PICKLE_FILEPATH, EIO_PICKLE_FILEPATH
    button_text, SIMULATION_RESULTS_FOLDERPATH, VARIABLES_PICKLE_FILEPATH, EIO_PICKLE_FILEPATH = EPGen.EPGen_Button_GenerateData_Interaction_Function(RESULTS_FOLDERPATH, start_date, end_date, Sim_TimeStep, Sim_OutputVariable_ReportingFrequency, n_clicks)
    return button_text

@app.callback(
    Output(component_id = 'EPGen_Download_DownloadFiles', component_property = 'data'),
    State(component_id = 'download_selection', component_property = 'value'),
    Input(component_id = 'EPGen_Button_DownloadFiles', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPGen_Button_DownloadFiles_Interaction(download_selection, n_clicks):
    download_path = EPGen.EPGen_Button_DownloadFiles_Interaction_Function(download_selection, n_clicks)
    return download_path

@app.callback(
    Output(component_id = 'EPGen_Button_EndSession', component_property = 'children'),
    Input(component_id = 'EPGen_Button_EndSession', component_property = 'n_clicks'),
    prevent_initial_call = True)
def EPGen_Button_EndSession_Interaction(n_clicks):
    message = EPGen.EPGen_Button_EndSession_Interaction_Function(n_clicks)
    return message

##########################################################################################################

#################### Aggregation #########################################################################

##########################################################################################################


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
'''
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
'''

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
    
'''


# Running the App
if __name__ == '__main__':
    app.run(port=4050)
    



